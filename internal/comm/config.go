package comm

import (
	"dst-run/assets"
	"github.com/spf13/viper"
)

func ViperGetStringSlice(key string) []string {
	s := viper.GetStringSlice(key)
	if s == nil {
		s = make([]string, 0)
	}
	return s
}

func SaveConfig() {
	if err := viper.WriteConfigAs(NSConfigPath); err != nil {
		panic(err)
	}
}

func initConfig() {
	viper.SetConfigName("neutron-star")
	viper.SetConfigType("toml")
	viper.AddConfigPath(ConfigDir)
	if err := viper.ReadInConfig(); err != nil {
		r, err := assets.FS.Open("assets/config.toml")
		if err != nil {
			panic(err)
		}
		if err := viper.ReadConfig(r); err != nil {
			panic(err)
		}
		SaveConfig()
	}
}
