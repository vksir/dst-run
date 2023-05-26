package tmodloader

import (
	"context"
	"dst-run/assets"
	"dst-run/internal/comm"
	"dst-run/internal/core"
	"dst-run/thirdparty/github"
	"encoding/json"
	"fmt"
	"github.com/spf13/viper"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"time"
)

type AgentAdapter struct {
	processes      []*core.Process
	recordHandlers []*core.Record
	cutHandlers    []*core.Cut
}

func NewAgentAdapter() *AgentAdapter {
	return &AgentAdapter{}
}

func (a *AgentAdapter) Processes() []*core.Process {
	return a.processes
}

func (a *AgentAdapter) Start() error {
	a.processes = []*core.Process{}
	a.recordHandlers = []*core.Record{}
	a.cutHandlers = []*core.Cut{}

	p := core.NewProcess("Tmod", getStartCmd())
	rh := core.NewRecord("Tmod", logPath)
	ch := core.NewCut("Tmod")

	p.RegisterHandler(rh)
	p.RegisterHandler(ch)
	if err := p.Start(); err != nil {
		return err
	}

	a.processes = append(a.processes, p)
	a.recordHandlers = append(a.recordHandlers, rh)
	a.cutHandlers = append(a.cutHandlers, ch)
	return nil
}

func (a *AgentAdapter) Stop() error {
	p := a.processes[0]

	if _, err := p.Stdin.Write([]byte("exit\n")); err != nil {
		log.Error("process write exit failed: ", err)
	}

	go func() {
		ctx, cancel := context.WithTimeout(p.Ctx, 15*time.Second)
		defer cancel()

		select {
		case <-ctx.Done():
			if err := ctx.Err(); err == context.DeadlineExceeded {
				log.Errorf("process exit timeout, begin kill: %s", err)
				if err := p.Stop(0); err != nil {
					log.Errorf("process kill failed: %s", err)
				}
			}
		}
	}()
	return nil
}

func (a *AgentAdapter) Install() error {
	latestTag, err := github.GetLatestRelease("tModLoader", "tModLoader")
	if err != nil {
		return err
	}
	return installProgram(latestTag)
}

func (a *AgentAdapter) Update() error {
	latestTag, err := github.GetLatestRelease("tModLoader", "tModLoader")
	if err != nil {
		return err
	}

	curVer, ok := data["version"]
	if ok {
		curVerString, ok := curVer.(string)
		if ok {
			if curVerString == latestTag {
				log.Infof("current version %s is lastest, no need update", curVerString)
				return nil
			}
		}
	}
	return installProgram(latestTag)
}

func (a *AgentAdapter) Config() error {
	if err := deployServerConfig(); err != nil {
		return err
	}
	if err := deployMod(); err != nil {
		return err
	}
	return nil
}

func (a *AgentAdapter) RunCmd(index int, cmd string) (string, error) {
	if index >= len(a.processes) {
		return "", fmt.Errorf("invalid index: %d", index)
	}

	p := a.processes[index]
	cut := a.cutHandlers[index]

	cmd = strings.TrimRight(cmd, "\n")
	if err := cut.BeginCut(); err != nil {
		return "", err
	}
	if _, err := p.Stdin.Write([]byte(fmt.Sprintf("[BEGIN_CMD]\n%s\n[END_CMD]\n", cmd))); err != nil {
		_, _ = cut.StopCut()
		return "", err
	}
	time.Sleep(500 * time.Millisecond)
	rawOut, err := cut.StopCut()
	if err != nil {
		return "", err
	}
	pattern := regexp.MustCompile(`(?ms)Invalid command.*^(.*)$\n.*Invalid command`)
	res := pattern.FindStringSubmatch(rawOut)
	if len(res) == 0 {
		return "", fmt.Errorf("regex cmd out failed: %s", rawOut)
	}
	log.Infof("run cmd %s success: %s", cmd, res[1])
	return res[1], nil
}

func installProgram(tag string) error {
	if err := comm.RemoveFile(programDir); err != nil {
		return err
	}
	if err := comm.MakeDir(programDir); err != nil {
		return err
	}

	if err := installTmodloader(tag); err != nil {
		return err
	}
	if err := installDotnet(); err != nil {
		return err
	}

	data["version"] = tag
	_ = SaveData()
	return nil
}

func installTmodloader(tag string) error {
	outputPath := filepath.Join(programDir, "tModLoader.zip")
	if err := github.DownLoadRelease(tag, "tModLoader.zip", outputPath); err != nil {
		return err
	}
	cmd := exec.Command("unzip", outputPath, "-d", programDir)
	if err := comm.RunCmd(cmd); err != nil {
		return err
	}
	return nil
}

// installDotnet
// use script: https://raw.githubusercontent.com/tModLoader/tModLoader/1.4.4/patches/tModLoader/Terraria/release_extras/LaunchUtils/ScriptCaller.sh
func installDotnet() error {
	// change script, exit before start tmodloader
	cmd := exec.Command("bash", "-c",
		`sed -i "s/.*tModLoader.dll.*/exit 0\n/g" ./LaunchUtils/ScriptCaller.sh`)
	cmd.Dir = programDir
	if err := comm.RunCmd(cmd); err != nil {
		log.Errorf("change script failed: %s", err)
		return err
	}

	cmd = exec.Command("bash", filepath.Join(programDir, "start-tModLoaderServer.sh"), "-nosteam")
	cmd.Dir = programDir
	p := core.NewProcess("Dotnet", cmd)
	rh := core.NewRecord("Dotnet", logPath)

	p.RegisterHandler(rh)
	if err := p.Start(); err != nil {
		return err
	}

	select {
	case <-p.Ctx.Done():
		return nil
	}
}

func deployServerConfig() error {
	b, err := assets.FS.ReadFile("assets/serverconfig.txt")
	if err != nil {
		panic(err)
	}
	content := string(b)

	worldName := viper.GetString("tmodloader.world_name")
	m := map[string]string{
		"world":      filepath.Join(worldDir, worldName+".wld"),
		"worldname":  viper.GetString("tmodloader.world_name"),
		"autocreate": viper.GetString("tmodloader.auto_create"),
		"difficulty": viper.GetString("tmodloader.difficulty"),
		"worldpath":  worldDir,
		"seed":       viper.GetString("tmodloader.seed"),
		"maxplayers": viper.GetString("tmodloader.max_players"),
		"password":   viper.GetString("tmodloader.password"),
	}
	for k, v := range m {
		pattern := regexp.MustCompile(fmt.Sprintf(`(?m)^#%s=.*$`, k))
		content = pattern.ReplaceAllString(content, k+"="+v)
	}

	return comm.WriteFile(serverConfigPath, []byte(content))
}

func deployMod() error {
	enableModIds := viper.GetStringSlice("tmodloader.mod_ids")
	if err := downloadMods(enableModIds); err != nil {
		return err
	}
	if err := installMods(enableModIds); err != nil {
		return err
	}
	if err := enableMods(enableModIds); err != nil {
		return err
	}
	return nil
}

func downloadMods(enableModIds []string) error {
	if len(enableModIds) == 0 {
		return nil
	}

	cmd := exec.Command("steamcmd", "+login", "anonymous")
	for _, id := range enableModIds {
		cmd.Args = append(cmd.Args, "+workshop_download_item", "1281930", id)
	}
	cmd.Args = append(cmd.Args, "+quit")

	p := core.NewProcess("Steam", cmd)
	rh := core.NewRecord("Steam", logPath)

	p.RegisterHandler(rh)
	if err := p.Start(); err != nil {
		return err
	}

	select {
	case <-p.Ctx.Done():
		return nil
	}
}

func installMods(enableModIds []string) error {
	if err := comm.RemoveFile(modDir); err != nil {
		return err
	}
	if err := comm.MakeDir(modDir); err != nil {
		return err
	}
	for _, id := range enableModIds {
		if err := copyMod(id); err != nil {
			return err
		}
	}
	return nil
}

func copyMod(id string) error {
	latestModDir, err := getLatestModDir(id)
	if err != nil {
		return err
	}
	files, err := os.ReadDir(latestModDir)
	for _, file := range files {
		if strings.HasSuffix(file.Name(), ".tmod") {
			if err := comm.CopyFile(filepath.Join(latestModDir, file.Name()), modDir); err != nil {
				return err
			}
			log.Infof("copy mod from %s to %s", filepath.Join(latestModDir, file.Name()), modDir)
		}
	}
	return nil
}

func getLatestModDir(id string) (string, error) {
	modDir := filepath.Join(steamModDir, id)
	if _, err := os.Stat(modDir); os.IsNotExist(err) {
		return "", err
	}
	files, err := os.ReadDir(modDir)
	if err != nil {
		return "", err
	}
	var s Sorter
	for _, file := range files {
		if file.IsDir() {
			t, err := time.Parse("2006.2", file.Name())
			if err != nil {
				return "", err
			}
			s = append(s, Sorter{{
				dirname: file.Name(),
				time:    t,
			}}...)
		}
	}
	sort.Sort(s)
	return filepath.Join(modDir, s[len(s)-1].dirname), nil
}

type Sorter []struct {
	dirname string
	time    time.Time
}

func (s Sorter) Len() int {
	return len(s)
}

func (s Sorter) Less(i, j int) bool {
	return s[i].time.Unix() < s[j].time.Unix()
}

func (s Sorter) Swap(i, j int) {
	s[i], s[j] = s[j], s[i]
}

func enableMods(enableModIds []string) error {
	bytes, err := json.MarshalIndent(enableModIds, "", "    ")
	if err != nil {
		return err
	}
	return comm.WriteFile(enableJson, bytes)
}
