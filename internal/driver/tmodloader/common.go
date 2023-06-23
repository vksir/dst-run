package tmodloader

import (
	"dst-run/internal/comm"
	"github.com/spf13/viper"
	"os/exec"
	"path/filepath"
)

const (
	DriveName = "tmodloader"
)

var log = comm.GetSugaredLogger()
var db = comm.GetDB()

var programDir = filepath.Join(comm.ProgramDir, DriveName)
var dataDir = filepath.Join(comm.DataDir, DriveName)
var logPath = filepath.Join(comm.LogDir, DriveName+".log")

var dotnetPath = filepath.Join(programDir, "dotnet/6.0.0/dotnet")
var serverConfigPath = filepath.Join(dataDir, "serverconfig.txt")

var archiveDir = filepath.Join(comm.Home(), ".local/share/Terraria/tModLoader/Worlds")
var steamModDir = filepath.Join(comm.Home(), "Steam/steamapps/workshop/content/1281930")
var modDir = filepath.Join(comm.Home(), ".local/share/Terraria/tModLoader/Mods")
var enableJson = filepath.Join(comm.Home(), ".local/share/Terraria/tModLoader/Mods/enabled.json")

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
	if err := comm.MkDir(dataDir); err != nil {
		panic(err)
	}

	initDB()
}
