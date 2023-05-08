package modresp

import (
	"dst-run/internal/common/model"
)

type Response struct {
	Mods []model.Mod `json:"mods"`
}
