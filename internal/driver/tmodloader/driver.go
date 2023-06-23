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
	"strings"
	"sync"
	"time"
)

const (
	EventTypeServerActive   = "SERVER_ACTIVE"
	EventTypeServerInactive = "SERVER_INACTIVE"
)

var R = core.NewReport("TMod", getReportPatterns())
var Agent = core.NewAgent(NewAgentDriver())

type AgentDriver struct {
	processes      []*core.Process
	recordHandlers []*core.Record
	cutHandlers    []*core.Cut
}

func NewAgentDriver() *AgentDriver {
	return &AgentDriver{}
}

func (a *AgentDriver) Name() string {
	return "TMod"
}

func (a *AgentDriver) Start(ctx context.Context, wg *sync.WaitGroup) error {
	if err := a.config(); err != nil {
		return err
	}

	a.processes = []*core.Process{}
	a.recordHandlers = []*core.Record{}
	a.cutHandlers = []*core.Cut{}

	p := core.NewProcess("TMod", getStartCmd())
	rh := core.NewRecord("TMod", logPath)
	ch := core.NewCut("TMod")

	p.RegisterHandler(rh)
	p.RegisterHandler(ch)
	p.RegisterHandler(R)
	if err := p.Start(); err != nil {
		return err
	}

	a.processes = append(a.processes, p)
	a.recordHandlers = append(a.recordHandlers, rh)
	a.cutHandlers = append(a.cutHandlers, ch)

	go func() {
		R.WaitEvent(ctx, EventTypeServerActive)
		wg.Done()
	}()
	return nil
}

func (a *AgentDriver) Stop() error {
	p := a.processes[0]

	if _, err := p.Stdin.Write([]byte("exit\n")); err != nil {
		log.Errorf("[%s] process write exit failed: %s", a.Name(), err)
	}

	ctx, cancel := context.WithTimeout(p.Ctx, 15*time.Second)
	defer cancel()

	select {
	case <-ctx.Done():
	}

	if err := ctx.Err(); err == context.DeadlineExceeded {
		log.Errorf("[%s] process exit timeout, begin kill: %s", a.Name(), err)
		if err := p.Cmd.Process.Signal(os.Kill); err != nil {
			log.Panicf("[%s] process kill failed: %s", a.Name(), err)
			return comm.NewErr(err)
		}
	}

	R.CacheEvent(&core.ReportEvent{
		Time:  time.Now().Unix(),
		Msg:   "服务器停止运行",
		Level: "warning",
		Type:  EventTypeServerInactive,
	})

	a.processes = []*core.Process{}
	return nil
}

func (a *AgentDriver) Install() error {
	latestTag, err := github.GetLatestRelease("tModLoader", "tModLoader")
	if err != nil {
		return err
	}

	R.CacheEvent(&core.ReportEvent{
		Time:  time.Now().Unix(),
		Msg:   "正在安装服务器",
		Level: "warning",
	})
	return installProgram(latestTag)
}

func (a *AgentDriver) Update() error {
	latestTag, err := github.GetLatestRelease("tModLoader", "tModLoader")
	if err != nil {
		return err
	}

	curVer, ok := comm.GetCacheSafe("tml_version")
	if ok {
		curVerString, ok := curVer.(string)
		if ok {
			if curVerString == latestTag {
				log.Infof("current version %s is lastest, no need update", curVerString)
				return nil
			}
		}
	}

	R.CacheEvent(&core.ReportEvent{
		Time:  time.Now().Unix(),
		Msg:   "正在更新服务器",
		Level: "warning",
	})
	return installProgram(latestTag)
}

func (a *AgentDriver) RunCmd(index int, cmd string) (string, error) {
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

func (a *AgentDriver) config() error {
	worldName := viper.GetString("tmodloader.world_name")
	ap := NewArchivePath(worldName)
	if !comm.ExistPath(ap.Root) {
		if err := createArchive(worldName); err != nil {
			return err
		}
	}
	if err := deployServerConfig(); err != nil {
		return err
	}
	if err := deployMod(); err != nil {
		return err
	}
	return nil
}

func installProgram(tag string) error {
	if err := comm.ClearDir(programDir); err != nil {
		return err
	}

	if err := installTmodloader(tag); err != nil {
		return err
	}
	if err := installDotnet(); err != nil {
		return err
	}

	comm.SetCache("tml_version", tag)
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
	proxy := viper.GetString("ns.proxy")
	if proxy != "" {
		cmd.Env = append(cmd.Env, fmt.Sprintf("all_proxy=%s", proxy))
	}

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

	ap := NewCurArchivePath()
	m := map[string]string{
		"world":      ap.WldPath,
		"worldname":  viper.GetString("tmodloader.world_name"),
		"autocreate": viper.GetString("tmodloader.auto_create"),
		"difficulty": viper.GetString("tmodloader.difficulty"),
		"worldpath":  ap.Root,
		"seed":       viper.GetString("tmodloader.seed"),
		"maxplayers": viper.GetString("tmodloader.max_players"),
		"password":   viper.GetString("tmodloader.password"),
		"port":       viper.GetString("tmodloader.port"),
	}
	for k, v := range m {
		pattern := regexp.MustCompile(fmt.Sprintf(`(?m)^#%s=.*$`, k))
		content = pattern.ReplaceAllString(content, k+"="+v)
	}

	return comm.WriteFile(serverConfigPath, []byte(content))
}

func deployMod() error {
	if err := comm.ClearDir(modDir); err != nil {
		return err
	}

	enableModIds := viper.GetStringSlice("tmodloader.enable_mods")
	if len(enableModIds) == 0 {
		return nil
	}

	R.CacheEvent(&core.ReportEvent{
		Time:  time.Now().Unix(),
		Msg:   "正在下载 Mod",
		Level: "info",
	})

	if err := downloadMods(enableModIds); err != nil {
		return err
	}
	if err := installMods(enableModIds); err != nil {
		return err
	}
	return nil
}

func downloadMods(enableModIds []string) error {
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
	var enableModNames []string
	for _, id := range enableModIds {
		tmod, err := getCompatibleTmod(id)
		if err != nil {
			return err
		}

		// install mod
		if err := comm.CopyFile(tmod.Path, modDir); err != nil {
			return err
		}
		log.Debugf("copy mod from %s to %s", tmod.Path, modDir)

		enableModNames = append(enableModNames, tmod.Name)
	}

	// write enable.json
	bytes, err := json.MarshalIndent(enableModNames, "", "  ")
	if err != nil {
		return err
	}
	return comm.WriteFile(enableJson, bytes)
}

func createArchive(name string) error {
	ap := NewArchivePath(name)
	return comm.MkDir(ap.Root)
}
