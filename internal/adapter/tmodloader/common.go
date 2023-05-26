package tmodloader

import (
	"dst-run/internal/comm"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
)

const (
	name = "tmodloader"
)

var log = comm.SugaredLogger()
var db = comm.GetDB()
var data = make(map[string]any)

var programDir = filepath.Join(comm.ProgramDir, name)
var dataDir = filepath.Join(comm.DataDir, name)
var logPath = filepath.Join(comm.LogDir, name+".log")

var dotnetPath = filepath.Join(programDir, "dotnet/6.0.0/dotnet")
var serverConfigPath = filepath.Join(dataDir, "serverconfig.txt")
var dataPath = filepath.Join(dataDir, "data.json")

var worldDir = filepath.Join(comm.Home(), ".local/share/Terraria/tModLoader/Worlds")
var steamModDir = filepath.Join(comm.Home(), "Steam/steamapps/workshop/content/1281930")
var modDir = filepath.Join(comm.Home(), ".local/share/Terraria/tModLoader/Mods")
var enableJson = filepath.Join(comm.Home(), ".local/share/Terraria/tModLoader/Mods/enabled.json")

func getStartCmd() *exec.Cmd {
	cmd := exec.Command(dotnetPath, "tModLoader.dll", "-server", "-config", serverConfigPath)
	cmd.Dir = filepath.Join(programDir)
	return cmd
}

func getModsFromDB() (map[string]*Mod, error) {
	rows, err := db.Query(`select * from t_tmodloader_mod`)
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

func SaveData() error {
	bytes, err := json.Marshal(&data)
	if err != nil {
		return err
	}
	return comm.WriteFile(dataPath, bytes)
}

func initData() {
	dataBytes, err := os.ReadFile(dataPath)
	if os.IsNotExist(err) {
		return
	}

	if err != nil {
		panic(err)
	}

	if err := json.Unmarshal(dataBytes, &data); err != nil {
		if err := comm.RemoveFile(dataPath); err != nil {
			panic(err)
		}
	}
}

func init() {
	if err := comm.MakeDir(dataDir); err != nil {
		panic(err)
	}

	initData()

	sql := `create table if not exists t_tmodloader_mod
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
