package comm

import (
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
		log.Errorf("save cache failed: %s", err)
	}
}

func SaveCache() error {
	bytes, err := json.Marshal(&cache)
	if err != nil {
		return err
	}
	return WriteFile(CachePath, bytes)
}

func initCache() {
	cacheBytes, err := os.ReadFile(CachePath)
	if os.IsNotExist(err) {
		return
	}

	if err != nil {
		panic(err)
	}

	if err := json.Unmarshal(cacheBytes, &cache); err != nil {
		if err := RmvPath(CachePath); err != nil {
			panic(err)
		}
	}
}
