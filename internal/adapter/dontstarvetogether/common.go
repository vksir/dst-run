package dontstarvetogether

import (
	"dst-run/internal/comm"
	"os/exec"
	"path/filepath"
)

const (
	name        = "dontstarve"
	clusterName = "Cluster"
	iconEye     = "󰀅"
)

var log = comm.SugaredLogger()
var db = comm.GetDB()

var programDir = filepath.Join(comm.ProgramDir, name)
var resourceDir = filepath.Join(comm.ResourceDir, name)
var dataDir = filepath.Join(comm.DataDir, name)
var logPath = filepath.Join(comm.LogDir, name+".log")

var defaultTemplateDir = filepath.Join(resourceDir, "default_template")
var customTemplateDir = filepath.Join(dataDir, "custom_template")

var dstServPath = filepath.Join(programDir, "bin64/dontstarve_dedicated_server_nullrenderer_x64")
var modSetupPath = filepath.Join(programDir, "mods/dedicated_server_mods_setup.lua")

var clusterDir = filepath.Join(comm.Home(), ".klei/DoNotStarveTogether", clusterName)
var adminListPath = filepath.Join(clusterDir, "adminlist.txt")
var clusterTokenPath = filepath.Join(clusterDir, "cluster_token.txt")
var clusterIniPath = filepath.Join(clusterDir, "cluster.ini")
var masterModOverrides = filepath.Join(clusterDir, "Master/modoverrides.lua")
var cavesModOverrides = filepath.Join(clusterDir, "Caves/modoverrides.lua")

func getStartCmd(shard string) *exec.Cmd {
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

func getModsFromDB() (map[string]*Mod, error) {
	rows, err := db.Query(`select * from t_dontstarve_mod`)
	if err != nil {
		return nil, err
	}

	mods := make(map[string]*Mod)
	for rows.Next() {
		var m Mod
		if err := rows.Scan(&m.Id, &m.Name, &m.Remark, &m.Config); err != nil {
			return nil, err
		}
		mods[m.Id] = &m
	}
	return mods, nil
}

func init() {
	if err := comm.MkDir(dataDir, customTemplateDir); err != nil {
		panic(err)
	}

	sql := `create table if not exists t_dontstarve_mod
(
	id text primary key not null,
	name text,
	remark text,
	config text
)`
	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}
}
