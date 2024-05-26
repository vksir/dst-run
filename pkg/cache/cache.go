package cache

import (
	"dst-run/pkg/log"
	"dst-run/pkg/util"
	"dst-run/pkg/workspace"
	"encoding/json"
	"os"
)

var cache = make(map[string]any)

func GetCache(key string) any {
	return cache[key]
}

func GetCacheSafe(key string) (any, bool) {
	value, ok := cache[key]
	return value, ok
}

func SetCache(key string, value any) {
	cache[key] = value
	if err := SaveCache(); err != nil {
		log.Error("save cache failed: %s", err)
	}
}

func SaveCache() error {
	bytes, err := json.Marshal(&cache)
	if err != nil {
		return err
	}
	return util.WriteFile(workspace.CachePath, bytes)
}

func InitCache() {
	cacheBytes, err := os.ReadFile(workspace.CachePath)
	if os.IsNotExist(err) {
		return
	}

	if err != nil {
		panic(err)
	}

	if err := json.Unmarshal(cacheBytes, &cache); err != nil {
		if err := util.RmvPath(workspace.CachePath); err != nil {
			panic(err)
		}
	}
}
