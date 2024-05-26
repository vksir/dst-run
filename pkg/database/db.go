package database

import (
	"dst-run/pkg/workspace"
	"fmt"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	_ "modernc.org/sqlite"
)

var DB *gorm.DB

func InitDb() error {
	sql := sqlite.Dialector{
		DriverName: "sqlite",
		DSN:        workspace.DBPath,
	}

	var err error
	DB, err = gorm.Open(sql, &gorm.Config{})
	if err != nil {
		return fmt.Errorf("gorm open db failed: %v", err)
	}

	return migrate()
}
