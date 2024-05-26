package tmodloader

import (
	"dst-run/pkg/util"
	"dst-run/pkg/workspace"
	"github.com/spf13/viper"
	"os/exec"
	"path/filepath"
)

const (
	DriveName = "tmodloader"
)

var programDir = filepath.Join(workspace.ProgramDir, DriveName)
var dataDir = filepath.Join(workspace.DataDir, DriveName)
var logPath = filepath.Join(workspace.LogDir, DriveName+".log")

var dotnetPath = filepath.Join(programDir, "dotnet/6.0.0/dotnet")
var serverConfigPath = filepath.Join(dataDir, "serverconfig.txt")

var archiveDir = filepath.Join(workspace.Home(), ".local/share/Terraria/tModLoader/Worlds")
var steamModDir = filepath.Join(workspace.Home(), "Steam/steamapps/workshop/content/1281930")
var modDir = filepath.Join(workspace.Home(), ".local/share/Terraria/tModLoader/Mods")
var enableJson = filepath.Join(workspace.Home(), ".local/share/Terraria/tModLoader/Mods/enabled.json")

type ArchivePath struct {
	Root    string
	WldPath string
}

func NewCurArchivePath() *ArchivePath {
	archiveName := viper.GetString("tmodloader.world_name")
	return NewArchivePath(archiveName)
}

func NewArchivePath(archiveName string) *ArchivePath {
	var ap ArchivePath

	ap.Root = filepath.Join(archiveDir, archiveName)
	ap.WldPath = filepath.Join(ap.Root, archiveName+".wld")

	return &ap
}

func getStartCmd() *exec.Cmd {
	cmd := exec.Command(dotnetPath, "tModLoader.dll", "-server", "-config", serverConfigPath)
	cmd.Dir = filepath.Join(programDir)
	return cmd
}

func init() {
	if err := util.MkDir(dataDir); err != nil {
		panic(err)
	}

}
