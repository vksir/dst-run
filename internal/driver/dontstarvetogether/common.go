package dontstarvetogether

import (
	"dst-run/internal/comm"
	"github.com/spf13/viper"
	"os/exec"
	"path/filepath"
)

const (
	name    = "dontstarve"
	iconEye = "󰀅"
)

var log = comm.GetSugaredLogger()
var db = comm.GetDB()

var programDir = filepath.Join(comm.ProgramDir, name)
var resourceDir = filepath.Join(comm.ResourceDir, name)
var dataDir = filepath.Join(comm.DataDir, name)
var logPath = filepath.Join(comm.LogDir, name+".log")

var defaultTemplateDir = filepath.Join(resourceDir, "default_template")
var customTemplateDir = filepath.Join(dataDir, "custom_template")

var dstServPath = filepath.Join(programDir, "bin64/dontstarve_dedicated_server_nullrenderer_x64")
var modSetupPath = filepath.Join(programDir, "mods/dedicated_server_mods_setup.lua")

func NewClusterPath() *ClusterPath {
	var cp ClusterPath

	clusterName := viper.GetString("dontstarve.archive_name")

	cp.Root = filepath.Join(comm.Home(), ".klei/DoNotStarveTogether", clusterName)
	cp.SettingFile = filepath.Join(cp.Root, "cluster.ini")
	cp.AdminListFile = filepath.Join(cp.Root, "adminlist.txt")
	cp.TokenFile = filepath.Join(cp.Root, "cluster_token.txt")

	cp.Master.Root = filepath.Join(cp.Root, "Master")
	cp.Master.WorldOverrideFile = filepath.Join(cp.Master.Root, "leveldataoverride.lua")
	cp.Master.ModOverrideFile = filepath.Join(cp.Master.Root, "modoverrides.lua")

	cp.Caves.Root = filepath.Join(cp.Root, "Caves")
	cp.Caves.WorldOverrideFile = filepath.Join(cp.Caves.Root, "leveldataoverride.lua")
	cp.Caves.ModOverrideFile = filepath.Join(cp.Caves.Root, "modoverrides.lua")

	return &cp
}

func getStartCmd(shard string) *exec.Cmd {
	clusterName := viper.GetString("dontstarve.archive_name")
	cmd := exec.Command(dstServPath, "-console", "-cluster", clusterName, "-shard", shard)
	cmd.Dir = filepath.Join(programDir, "bin64")
	return cmd
}

func getInstallCmd() *exec.Cmd {
	cmd := exec.Command("steamcmd",
		"+force_install_dir", programDir,
		"+login", "anonymous",
		"+app_update", "343050", "validate",
		"+quit")
	return cmd
}

func init() {
	if err := comm.MkDir(dataDir, customTemplateDir); err != nil {
		panic(err)
	}

	initDB()
}
