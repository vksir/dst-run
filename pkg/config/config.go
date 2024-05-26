package config

import (
	"dst-run/pkg/workspace"
	_ "embed"
	"fmt"
	"github.com/spf13/viper"
	"strings"
)

//go:embed config.toml
var defaultConfig string

func ViperGetStringSlice(key string) []string {
	s := viper.GetStringSlice(key)
	if s == nil {
		s = make([]string, 0)
	}
	return s
}

func SaveConfig() {
	if err := viper.WriteConfigAs(workspace.NSConfigPath); err != nil {
		panic(err)
	}
}

func InitConfig(dir string) error {
	viper.SetConfigName("aurora-admin")
	viper.SetConfigType("toml")
	viper.AddConfigPath(dir)
	if err := viper.ReadInConfig(); err != nil {
		if err := viper.ReadConfig(strings.NewReader(defaultConfig)); err != nil {
			return fmt.Errorf("viper read config failed: %v", err)
		}
		SaveConfig()
	}
	return nil
}
