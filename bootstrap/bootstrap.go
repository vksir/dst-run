package bootstrap

import (
	"dst-run/pkg/cache"
	"dst-run/pkg/config"
	"dst-run/pkg/database"
	"dst-run/pkg/log"
	"dst-run/pkg/workspace"
)

func Init() error {
	var err error

	err = workspace.InitWorkSpace()
	if err != nil {
		return err
	}

	err = config.InitConfig(workspace.ConfigDir)
	if err != nil {
		return err
	}

	err = log.InitLog(workspace.NSLogPath, "debug")
	if err != nil {
		return err
	}

	cache.InitCache()

	err = database.InitDb()
	if err != nil {
		return err
	}

	return nil
}
