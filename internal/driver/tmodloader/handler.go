package tmodloader

import (
	"dst-run/internal/comm"
	"dst-run/internal/core"
	"dst-run/thirdparty/steam"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/spf13/viper"
	"io"
	"net/http"
	"strings"
)

func LoadRouters(g *gin.RouterGroup) {
	g = g.Group("/tmodloader")

	g.GET("/status", getStatus)
	g.POST("/control/:action", control)

	g.GET("/config", getConfig)
	g.PUT("/config", updateConfig)

	g.GET("/mod", getMods)
	g.POST("/mod", addMods)
	g.POST("/mod/mod_id", addModsFromId)
	g.DELETE("/mod", delMods)
	g.PUT("/mod", updateMods)

	g.GET("/runtime/player", getPlayers)

	g.GET("/event", getEvents)
}

// getStatus godoc
// @Summary			获取服务器状态
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Success			200 {object} Status
// @Failure			500 {object} comm.RespErr
// @Router			/api/tmodloader/status [get]
func getStatus(c *gin.Context) {
	c.JSON(http.StatusOK, Status{Agent.Status()})
}

// control godoc
// @Summary			服务器控制
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Param			action path string true "[ start | stop | restart | update | install ]"
// @Success			200 {object} comm.RespOk
// @Failure			500 {object} comm.RespErr
// @Router			/api/tmodloader/control/{action} [post]
func control(c *gin.Context) {
	action := c.Param("action")

	switch action {
	case "start":
		if err := Agent.Start(); err != nil {
			c.JSON(http.StatusInternalServerError, comm.NewRespErr(err))
			return
		}
	case "stop":
		if err := Agent.Stop(); err != nil {
			c.JSON(http.StatusInternalServerError, comm.NewRespErr(err))
			return
		}
	case "restart":
		if err := Agent.Restart(); err != nil {
			c.JSON(http.StatusInternalServerError, comm.NewRespErr(err))
			return
		}
	case "update":
		if err := Agent.Update(); err != nil {
			c.JSON(http.StatusInternalServerError, comm.NewRespErr(err))
			return
		}
	case "install":
		if err := Agent.Install(); err != nil {
			c.JSON(http.StatusInternalServerError, comm.NewRespErr(err))
			return
		}
	default:
		c.JSON(http.StatusBadRequest, comm.NewRespErr(fmt.Sprintf("invalid action: %s", action)))
		return
	}
	c.JSON(http.StatusOK, comm.NewRespOk())
}

// getConfig godoc
// @Summary			获取 Config
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Success			200 {object} Config
// @Failure			500 {object} comm.RespErr
// @Router			/api/tmodloader/config [get]
func getConfig(c *gin.Context) {
	c.JSON(http.StatusOK, Config{
		WorldName:  viper.GetString("tmodloader.world_name"),
		AutoCreate: viper.GetInt("tmodloader.auto_create"),
		Difficulty: viper.GetInt("tmodloader.difficulty"),
		Seed:       viper.GetString("tmodloader.seed"),
		MaxPlayers: viper.GetInt("tmodloader.max_players"),
		Password:   viper.GetString("tmodloader.password"),
		Port:       viper.GetInt("tmodloader.port"),
		EnableMods: comm.ViperGetStringSlice("tmodloader.enable_mods"),
	})
}

// updateConfig godoc
// @Summary			更新 Config
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Param			body body Config true "body"
// @Success			200 {object} comm.RespOk
// @Failure			500 {object} comm.RespErr
// @Router			/api/tmodloader/config [put]
func updateConfig(c *gin.Context) {
	var cfg map[string]any
	if err := c.ShouldBindJSON(&cfg); err != nil {
		c.JSON(http.StatusBadRequest, comm.NewRespErr(err))
		return
	}
	for k, v := range cfg {
		viper.Set(fmt.Sprintf("tmodloader.%s", k), v)
	}
	comm.SaveConfig()
	c.JSON(http.StatusOK, comm.NewRespOk())
}

// getMods godoc
// @Summary			查看 Mods
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Success			200 {object} ModMap
// @Failure			500 {object} comm.RespErr
// @Router			/api/tmodloader/mod [get]
func getMods(c *gin.Context) {
	mods, err := getModsInDB()
	if err != nil {
		c.JSON(http.StatusInternalServerError, comm.NewRespErr(err))
		return
	}
	c.JSON(http.StatusOK, mods)
}

// addMods godoc
// @Summary			添加 Mods
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Param			body body ModMap true "body"
// @Success			200 {object} comm.RespOk
// @Failure			500 {object} comm.RespErr
// @Router			/api/tmodloader/mod [post]
func addMods(c *gin.Context) {
	mods := make(map[string]*Mod)
	if err := c.ShouldBindJSON(&mods); err != nil {
		c.JSON(http.StatusBadRequest, comm.NewRespErr(err))
		return
	}

	var modIds []string
	for id := range mods {
		modIds = append(modIds, id)
	}
	if wl, err := steam.GetWorkShopItemInfos(modIds); err == nil {
		for _, w := range wl {
			mods[w.Id].Name = w.Name
		}
	}

	if err := addModsInDB(mods); err != nil {
		c.JSON(http.StatusBadRequest, comm.NewRespErr(err))
		return
	}
	c.JSON(http.StatusOK, comm.NewRespOk())
}

// addModsFromId godoc
// @Summary			通过 Mod ID 添加 Mods
// @Tags			tmodloader
// @Accept			plain
// @Produce			json
// @Param			body body string true "多个 Mod ID 一行一个"
// @Success			200 {object} comm.RespOk
// @Failure			500 {object} comm.RespErr
// @Router			/api/tmodloader/mod/mod_id [post]
func addModsFromId(c *gin.Context) {
	bytes, err := io.ReadAll(c.Request.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, comm.NewRespErr(err))
		return
	}

	var modIds []string
	rawModIds := strings.Split(string(bytes), "\n")
	for _, id := range rawModIds {
		if id != "" {
			modIds = append(modIds, id)
		}
	}

	mods := make(map[string]*Mod)
	for _, id := range rawModIds {
		mods[id] = &Mod{Id: id}
	}

	if wl, err := steam.GetWorkShopItemInfos(modIds); err == nil {
		for _, w := range wl {
			mods[w.Id].Name = w.Name
		}
	}

	if err := addModsInDB(mods); err != nil {
		c.JSON(http.StatusBadRequest, comm.NewRespErr(err))
		return
	}
	c.JSON(http.StatusOK, comm.NewRespOk())
}

// delMods godoc
// @Summary			删除 Mods
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Param			body body ModIdList true "body"
// @Success			200 {object} comm.RespOk
// @Failure			500 {object} comm.RespErr
// @Router			/api/tmodloader/mod [delete]
func delMods(c *gin.Context) {
	var modIds []string
	if err := c.ShouldBindJSON(&modIds); err != nil {
		c.JSON(http.StatusBadRequest, comm.NewRespErr(err))
		return
	}

	if err := delModsInDB(modIds); err != nil {
		c.JSON(http.StatusBadRequest, comm.NewRespErr(err))
		return
	}
	c.JSON(http.StatusOK, comm.NewRespOk())
}

// updateMods godoc
// @Summary			更新 Mods
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Param   		update_mod_info query string false "[ true | false ]"
// @Param			body body ModMap true "body"
// @Success			200 {object} comm.RespOk
// @Failure			500 {object} comm.RespErr
// @Router			/api/tmodloader/mod [put]
func updateMods(c *gin.Context) {
	mods := make(map[string]*Mod)
	if err := c.ShouldBindJSON(&mods); err != nil {
		c.JSON(http.StatusBadRequest, comm.NewRespErr(err))
		return
	}

	updateModInfo := c.Query("update_mod_info")
	if updateModInfo == "true" {
		var modIds []string
		for id := range mods {
			modIds = append(modIds, id)
		}
		if wl, err := steam.GetWorkShopItemInfos(modIds); err == nil {
			for _, w := range wl {
				mods[w.Id].Name = w.Name
			}
		}
	}

	if err := updateModsInDB(mods); err != nil {
		c.JSON(http.StatusBadRequest, comm.NewRespErr(err))
		return
	}
	c.JSON(http.StatusOK, comm.NewRespOk())
}

// getPlayers godoc
// @Summary			获取当前玩家
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Success			200 {object} PlayerList
// @Failure			500 {object} comm.RespErr
// @Router			/api/tmodloader/runtime/player [get]
func getPlayers(c *gin.Context) {
	if Agent.Status() != core.StatusActive {
		c.JSON(http.StatusBadRequest, comm.NewRespErr("server is not active"))
	}

	a := Agent.Driver.(*AgentDriver)
	out, err := a.RunCmd(0, "playing")
	if err != nil {
		c.JSON(http.StatusInternalServerError, comm.NewRespErr(err))
		return
	}

	c.JSON(http.StatusOK, []string{out})
}

// getEvents godoc
// @Summary			获取最近事件
// @Description		ReportEvent Type: [ SERVER_ACTIVE ]
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Success			200 {object} core.ReportEventList
// @Failure			500 {object} comm.RespErr
// @Router			/api/tmodloader/event [get]
func getEvents(c *gin.Context) {
	events, err := R.GetEvents()
	if err != nil {
		c.JSON(http.StatusInternalServerError, comm.NewRespErr(err))
		return
	}

	c.JSON(http.StatusOK, events)
}
