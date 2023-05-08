package mod

import (
	"bufio"
	"dst-run/internal/common/config"
	"dst-run/internal/common/constant"
	"dst-run/internal/common/logging"
	"dst-run/internal/common/model"
	"dst-run/internal/common/util"
	"dst-run/internal/report"
	"encoding/json"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

var log = logging.SugaredLogger()

type Handler struct {
	mods          []model.Mod
	modEnableData []string
}

func NewHandler() *Handler {
	h := Handler{}
	for id := range config.CFG.IdToMod {
		if config.CFG.IdToMod[id].Enable {
			h.mods = append(h.mods, config.CFG.IdToMod[id])
		}
	}
	return &h
}

func (h *Handler) Deploy() error {
	if len(h.mods) == 0 {
		return nil
	}
	log.Infof("Begin deploy %d mods", len(h.mods))
	if err := h.downloadMods(); err != nil {
		log.Error("Download mods failed", err)
		return err
	}
	if err := h.copyMods(); err != nil {
		log.Error("Copy mods failed", err)
		return err
	}
	if err := h.writeEnableJson(); err != nil {
		log.Error("Write enable.json failed", err)
		return err
	}
	log.Info("Deploy mods success")
	return nil
}

func (h *Handler) downloadMods() error {
	reportUpdateMod()
	cmd := exec.Command("steamcmd", "+login", "anonymous")
	for i := range h.mods {
		cmd.Args = append(cmd.Args, "+workshop_download_item", "1281930", h.mods[i].Id)
	}
	cmd.Args = append(cmd.Args, "+quit")
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return err
	}
	stderr, err := cmd.StderrPipe()
	if err != nil {
		return err
	}
	r := io.MultiReader(stdout, stderr)
	go func(r io.Reader) {
		scanner := bufio.NewScanner(r)
		for scanner.Scan() {
			log.Debug("[SteamCMD] ", scanner.Text())
		}
	}(r)
	return cmd.Run()
}

func (h *Handler) copyMods() error {
	if err := util.Remove(constant.ModDir); err != nil {
		return err
	}
	if err := os.Mkdir(constant.ModDir, 0755); err != nil {
		return err
	}
	for i := range h.mods {
		if err := h.copyMod(h.mods[i].Id); err != nil {
			return err
		}
	}
	return nil
}

func (h *Handler) writeEnableJson() error {
	bytes, err := json.MarshalIndent(h.modEnableData, "", "    ")
	if err != nil {
		return err
	}
	return os.WriteFile(constant.EnableJson, bytes, 0644)
}

func (h *Handler) copyMod(id string) error {
	latestModDir, err := getLatestModDir(id)
	if err != nil {
		return err
	}
	files, err := os.ReadDir(latestModDir)
	for _, file := range files {
		if strings.HasSuffix(file.Name(), ".tmod") {
			if err := util.Copy(filepath.Join(latestModDir, file.Name()), constant.ModDir); err != nil {
				return err
			}
			h.modEnableData = append(h.modEnableData, strings.TrimSuffix(file.Name(), ".tmod"))
			log.Infof("Copy mod from %s to %s", filepath.Join(latestModDir, file.Name()), constant.ModDir)
		}
	}
	return nil
}

type sorter []struct {
	dirname string
	time    time.Time
}

func (s sorter) Len() int {
	return len(s)
}

func (s sorter) Less(i, j int) bool {
	return s[i].time.Unix() < s[j].time.Unix()
}

func (s sorter) Swap(i, j int) {
	s[i], s[j] = s[j], s[i]
}

func getLatestModDir(id string) (string, error) {
	modDir := filepath.Join(constant.SteamModDir, id)
	if _, err := os.Stat(modDir); os.IsNotExist(err) {
		return "", err
	}
	files, err := os.ReadDir(modDir)
	if err != nil {
		return "", err
	}
	var s sorter
	for _, file := range files {
		if file.IsDir() {
			t, err := time.Parse("2006.2", file.Name())
			if err != nil {
				return "", err
			}
			s = append(s, sorter{{
				dirname: file.Name(),
				time:    t,
			}}...)
		}
	}
	sort.Sort(s)
	return filepath.Join(modDir, s[len(s)-1].dirname), nil
}

func reportUpdateMod() {
	report.R.ReportEvent(&report.Event{
		Level: "info",
		Time:  time.Now().Unix(),
		Msg:   "正在更新 Mod",
	})
}
