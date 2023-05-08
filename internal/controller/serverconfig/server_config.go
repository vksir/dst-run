package serverconfig

import (
	"dst-run/assets"
	"dst-run/internal/common/config"
	"dst-run/internal/common/constant"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
)

type Handler struct {
	content string
}

func NewHandler() *Handler {
	bytes, err := assets.FS.ReadFile("assets/serverconfig.txt")
	if err != nil {
		panic(err)
	}
	s := Handler{content: string(bytes)}
	s.setRequiredOptions()
	s.setOptionalOptions()
	return &s
}

func (h *Handler) Deploy() error {
	return os.WriteFile(constant.ServerConfigPath, []byte(h.content), 0644)
}

func (h *Handler) setRequiredOptions() {
	h.set("world", filepath.Join(constant.WorldDir, fmt.Sprintf("%s.wld", config.CFG.ServerConfig.WorldName)))
	h.set("autocreate", strconv.Itoa(config.CFG.ServerConfig.AutoCreate))
	h.set("worldname", config.CFG.ServerConfig.WorldName)
	h.set("difficulty", strconv.Itoa(config.CFG.ServerConfig.Difficulty))
	h.set("worldpath", constant.WorldDir)
}

func (h *Handler) setOptionalOptions() {
	h.setIfNotEmpty("seed", config.CFG.ServerConfig.Seed)
	h.setIfNotEmpty("maxplayers", strconv.Itoa(config.CFG.ServerConfig.MaxPlayers))
	h.setIfNotEmpty("password", config.CFG.ServerConfig.Password)
}

func (h *Handler) set(key, value string) {
	pattern := regexp.MustCompile(fmt.Sprintf(`(?m)^#%s=.*$`, key))
	h.content = pattern.ReplaceAllString(h.content, fmt.Sprintf("%s=%s", key, value))
}

func (h *Handler) setIfNotEmpty(key, value string) {
	if value == "" {
		return
	}
	h.set(key, value)
}
