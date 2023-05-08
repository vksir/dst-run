package config

import (
	"dst-run/assets"
	"dst-run/internal/common/constant"
	"dst-run/internal/common/model"
	"encoding/json"
	"os"
)

const (
	SizeSmall  = 1
	SizeMedium = 2
	SizeLarge  = 3

	DifficultyClassic = 0
	DifficultyExpert  = 1
	DifficultyMaster  = 2
	DifficultyJourney = 3
)

var CFG *model.Config

func Read() {
	if _, err := os.Stat(constant.ConfigPath); os.IsNotExist(err) {
		panic(err)
	}
	bytes, err := os.ReadFile(constant.ConfigPath)
	if err != nil {
		panic(err)
	}
	CFG = &model.Config{}
	if err := json.Unmarshal(bytes, &CFG); err != nil {
		panic(err)
	}
}

func Write() {
	bytes, err := json.MarshalIndent(CFG, "", "    ")
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile(constant.ConfigPath, bytes, 0644); err != nil {
		panic(err)
	}
}

func init() {
	setDefault()
}

func setDefault() {
	if f, _ := os.Stat(constant.ConfigPath); f != nil {
		return
	}
	bytes, err := assets.FS.ReadFile("assets/config.json")
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile(constant.ConfigPath, bytes, 0644); err != nil {
		panic(err)
	}
}
