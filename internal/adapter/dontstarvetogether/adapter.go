package dontstarvetogether

import (
	"dst-run/internal/comm"
	"dst-run/internal/core"
	"fmt"
	"github.com/spf13/viper"
	"gopkg.in/ini.v1"
	"os"
	"path/filepath"
	"regexp"
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

	for _, shard := range []string{"Master", "Caves"} {
		p := core.NewProcess(shard, getStartCmd(shard))
		rh := core.NewRecord(shard, logPath)
		ch := core.NewCut(shard)

		p.RegisterHandler(rh)
		p.RegisterHandler(ch)
		if err := p.Start(); err != nil {
			return err
		}

		a.processes = append(a.processes, p)
		a.recordHandlers = append(a.recordHandlers, rh)
		a.cutHandlers = append(a.cutHandlers, ch)
	}
	return nil
}

func (a *AgentAdapter) Stop() error {
	for _, p := range a.processes {
		if err := p.Stop(15 * time.Second); err != nil {
			return err
		}
	}
	return nil
}

func (a *AgentAdapter) Install() error {
	p := core.NewProcess("Steam", getInstallCmd())
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

func (a *AgentAdapter) Update() error {
	return a.Install()
}

func (a *AgentAdapter) Config() error {
	if err := createClusterIfNotExist(); err != nil {
		return err
	}
	if err := deployAdminList(); err != nil {
		return err
	}
	if err := deployClusterToken(); err != nil {
		return err
	}
	if err := deployClusterIni(); err != nil {
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
	pattern := regexp.MustCompile(`(?ms)BEGIN_CMD(.*?)END_CMD`)
	res := pattern.FindStringSubmatch(rawOut)
	if len(res) == 0 {
		return "", fmt.Errorf("regex cmd out failed: %s", rawOut)
	}
	log.Infof("run cmd %s success: %s", cmd, res[1])
	return res[1], nil
}

func createClusterIfNotExist() error {
	if _, err := os.Stat(clusterDir); err == os.ErrNotExist {
		return comm.CopyFile(filepath.Join(defaultTemplateDir, "default"), clusterDir)
	}
	return nil
}

func deployAdminList() error {
	admins := viper.GetStringSlice("dontstarve.admin_list")
	content := strings.Join(admins, "\n")
	return comm.WriteFile(adminListPath, []byte(content))
}

func deployClusterToken() error {
	token := viper.GetString("dontstarve.cluster_token")
	return comm.WriteFile(clusterTokenPath, []byte(token))
}

func deployClusterIni() error {
	cfg, err := ini.Load(clusterIniPath)
	if err != nil {
		return err
	}

	m := map[string][]string{
		"GAMEPLAY": {"game_mode", "max_players", "pvp"},
		"NETWORK":  {"cluster_name", "cluster_password", "cluster_description"},
	}
	for section, keys := range m {
		for _, k := range keys {
			v := viper.GetString(fmt.Sprintf("dontstarve.%s", k))
			if k == "cluster_name" {
				v = iconEye + v + iconEye
			}
			cfg.Section(section).Key(k).SetValue(v)
		}
	}
	return nil
}

func deployMod() error {
	enableModIds := viper.GetStringSlice("dontstarve.mod_ids")

	mods, err := getModsFromDB()
	if err != nil {
		return err
	}

	var enableModConfigs []string
	for _, id := range enableModIds {
		m, ok := mods[id]
		if ok {
			enableModConfigs = append(enableModConfigs, m.Config)
		}
	}

	content := "return {" + strings.Join(enableModConfigs, ",") + "}"
	if err := comm.WriteFile(masterModOverrides, []byte(content)); err != nil {
		return err
	}
	if err := comm.WriteFile(cavesModOverrides, []byte(content)); err != nil {
		return err
	}

	var enableModSetupConfigs []string
	for _, id := range enableModIds {
		enableModSetupConfigs = append(enableModSetupConfigs, fmt.Sprintf("ServerModSetup(\"%s\")", id))
	}
	content = strings.Join(enableModSetupConfigs, "\n")
	if err := comm.WriteFile(modSetupPath, []byte(content)); err != nil {
		return err
	}
	return nil
}
