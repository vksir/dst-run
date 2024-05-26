package webapi

import (
	"context"
	"dst-run/internal/entity"
	"dst-run/pkg/log"
	"dst-run/thirdparty/steam"
)

type DontStarveModApi struct {
	l log.Interface
}

func NewDontStarveModApi(l log.Interface) *DontStarveModApi {
	return &DontStarveModApi{l.WithTag("DontStarveModApi")}
}

func (a *DontStarveModApi) FetchModsName(ctx context.Context, mods []entity.DontStarveMod) []entity.DontStarveMod {
	var modIds []string
	for _, m := range mods {
		modIds = append(modIds, m.ModId)
	}
	infos, err := steam.GetWorkShopItemInfos(modIds)
	if err != nil {
		a.l.ErrorC(ctx, "steam get work shop item info failed: %v", err)
		return mods
	}

	modMap := make(map[string]entity.DontStarveMod)
	for _, m := range mods {
		modMap[m.ModId] = m
	}

	for _, info := range infos {
		mod := modMap[info.Id]
		mod.Name = info.Name

		modMap[info.Id] = mod
	}

	var newMods []entity.DontStarveMod
	for _, m := range modMap {
		newMods = append(newMods, m)
	}
	return newMods
}
