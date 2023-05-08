package constant

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

func Workspace() string {
	p := filepath.Join(Home(), ".dst-run")
	if _, err := os.Stat(p); os.IsNotExist(err) {
		if err := os.Mkdir(p, 0755); err != nil {
			panic(err)
		}
	}
	return p
}

var InstallDir = filepath.Join(Home(), "neutron-star", "dst-run")
var ServerLogPath = filepath.Join(Workspace(), "dst-run.log")
var DotnetPath = filepath.Join(InstallDir, "tModLoader/dotnet/6.0.0/dotnet")
var ServerConfigPath = filepath.Join(Workspace(), "serverconfig.txt")
var TModLoaderLogPath = filepath.Join(Workspace(), "tModLoader.log")
var ConfigPath = filepath.Join(Workspace(), "config.json")
var WorldDir = filepath.Join(Home(), ".local/share/Terraria/tModLoader/Worlds")
var SteamModDir = filepath.Join(Home(), "Steam/steamapps/workshop/content/1281930")
var ModDir = filepath.Join(Home(), ".local/share/Terraria/tModLoader/Mods")
var EnableJson = filepath.Join(Home(), ".local/share/Terraria/tModLoader/Mods/enabled.json")
