package workspace

import (
	"dst-run/pkg/util"
	"fmt"
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

var NSHome = filepath.Join(Home(), "aurora-admin")

var ProgramDir = filepath.Join(NSHome, "program")
var ResourceDir = filepath.Join(NSHome, "resource")
var ConfigDir = filepath.Join(NSHome, "config")
var DataDir = filepath.Join(NSHome, "data")
var LogDir = filepath.Join(NSHome, "log")

var NSConfigPath = filepath.Join(ConfigDir, "aurora-admin.toml")
var CachePath = filepath.Join(DataDir, "cache.json")
var NSLogPath = filepath.Join(LogDir, "aurora-admin.log")
var DBPath = filepath.Join(DataDir, "aurora-admin.db")

func InitWorkSpace() error {
	err := util.MkDir(NSHome, ProgramDir, ResourceDir, ConfigDir, DataDir, LogDir)
	if err != nil {
		return fmt.Errorf("mkdir failed: %v", err)
	}
	return nil
}
