package dontstarvetogether

import (
	"context"
	"dst-run/internal/comm"
	"dst-run/internal/core"
	"fmt"
	"github.com/spf13/viper"
	"gopkg.in/ini.v1"
	"os"
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

var R = core.NewReport("DST", getReportPatterns())
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
	return "DST"
}

func (a *AgentDriver) Processes() []*core.Process {
	return a.processes
}

func (a *AgentDriver) Start(ctx context.Context, wg *sync.WaitGroup) error {
	if err := a.config(); err != nil {
		return err
	}

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

	go func() {
		R.WaitEvent(ctx, EventTypeServerActive)
		wg.Done()
	}()

	return nil
}

func (a *AgentDriver) Stop() error {
	log.Infof("[%s] begin stop process: ", a.Name())
	for _, p := range a.processes {
		if err := p.Cmd.Process.Signal(os.Interrupt); err != nil {
			log.Errorf("[%s] process signal interrupt failed: %s", a.Name(), err)
		}
	}

	ctx, cancel := context.WithTimeout(context.Background(), time.Second*15)
	defer cancel()

	for _, p := range a.processes {
		select {
		case <-p.Ctx.Done():
		case <-ctx.Done():
		}
	}

	if err := ctx.Err(); err == context.DeadlineExceeded {
		log.Infof("[%s] stop process timeout, begin kill", a.Name())
		for _, p := range a.processes {
			if err := p.Cmd.Process.Signal(os.Kill); err != nil {
				log.Panicf("[%s] process kill failed: %s", a.Name(), err)
				return comm.NewErr(err)
			}
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
	R.CacheEvent(&core.ReportEvent{
		Time:  time.Now().Unix(),
		Msg:   "正在安装服务器",
		Level: "warning",
	})
	return installProgram()
}

func (a *AgentDriver) Update() error {
	R.CacheEvent(&core.ReportEvent{
		Time:  time.Now().Unix(),
		Msg:   "正在更新服务器",
		Level: "warning",
	})
	return installProgram()
}

func (a *AgentDriver) config() error {
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
	pattern := regexp.MustCompile(`(?ms)BEGIN_CMD(.*?)END_CMD`)
	res := pattern.FindStringSubmatch(rawOut)
	if len(res) == 0 {
		return "", fmt.Errorf("regex cmd out failed: %s", rawOut)
	}
	log.Infof("run cmd %s success: %s", cmd, res[1])
	return res[1], nil
}

func installProgram() error {
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

func createClusterIfNotExist() error {
	cp := NewClusterPath()
	if _, err := os.Stat(cp.Root); err == os.ErrNotExist {
		return comm.CopyFile(filepath.Join(defaultTemplateDir, "default"), cp.Root)
	}
	return nil
}

func deployAdminList() error {
	cp := NewClusterPath()
	admins := viper.GetStringSlice("dontstarve.admin_list")
	content := strings.Join(admins, "\n")
	return comm.WriteFile(cp.AdminListFile, []byte(content))
}

func deployClusterToken() error {
	cp := NewClusterPath()
	token := viper.GetString("dontstarve.cluster_token")
	return comm.WriteFile(cp.TokenFile, []byte(token))
}

func deployClusterIni() error {
	cp := NewClusterPath()
	cfg, err := ini.Load(cp.SettingFile)
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
	cp := NewClusterPath()
	enableModIds := viper.GetStringSlice("dontstarve.enable_mods")

	mods, err := getModsInDB()
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
	if err := comm.WriteFile(cp.Master.ModOverrideFile, []byte(content)); err != nil {
		return err
	}
	if err := comm.WriteFile(cp.Caves.ModOverrideFile, []byte(content)); err != nil {
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
