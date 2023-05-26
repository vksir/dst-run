package modresp

import (
	"dst-run/internal/comm/model"
)

type Response struct {
	Mods []model.Mod `json:"mods"`
}
