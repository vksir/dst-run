package database

import (
	"dst-run/internal/entity"
	"fmt"
)

func migrate() error {
	err := DB.AutoMigrate(
		&entity.DontStarveCluster{},
		&entity.DontStarveWorld{},
		&entity.DontStarveMod{},
		&entity.DontStarveModInCluster{},
	)
	if err != nil {
		return fmt.Errorf("auto migrate failed: %s", err)
	}

	return nil
}
