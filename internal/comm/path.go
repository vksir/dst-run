package comm

import (
	"os"
	"path/filepath"
)

func Home() string {
	h, err := os.UserHomeDir()
	if err != nil {
		panic(err)
	}
	return h
}

var NSHome = filepath.Join(Home(), "neutron-star")

var ProgramDir = filepath.Join(NSHome, "program")
var ResourceDir = filepath.Join(NSHome, "resource")
var ConfigDir = filepath.Join(NSHome, "config")
var DataDir = filepath.Join(NSHome, "data")
var LogDir = filepath.Join(NSHome, "log")

var NSConfigPath = filepath.Join(ConfigDir, "neutron-star.toml")
var NSLogPath = filepath.Join(LogDir, "neutron-star.log")
var DBPath = filepath.Join(DataDir, "neutron-star.db")

func initPath() {
	if err := MkDir(NSHome, ProgramDir, ResourceDir, ConfigDir, DataDir, LogDir); err != nil {
		panic(err)
	}
}
