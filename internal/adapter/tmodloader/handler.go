package tmodloader

import (
	"dst-run/internal/comm"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/spf13/viper"
	"net/http"
)

func LoadRouters(g *gin.RouterGroup) {
	g = g.Group("/tmodloader")

	g.POST("/control/:action", control)

	g.GET("/server_config", getServerConfig)
	g.PUT("/server_config", updateServerConfig)

	g.GET("/mod", getMods)
	g.POST("/mod", addMods)
	g.DELETE("/mod", delMods)
	g.PUT("/mod", updateMods)

	g.GET("/runtime/players", getPlayers)

	g.GET("/events", getEvents)
}

// control godoc
// @Summary			服务器控制
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Param			action path string true "[ start | stop | restart | update | install ]"
// @Success			200 {object} comm.RespOk
// @Failure			500 {object} comm.RespErr
// @Router			/tmodloader/control/{action} [post]
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

// get godoc
// @Summary			获取 ServerConfig
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Success			200 {object} ServerConfig
// @Failure			500 {object} comm.RespErr
// @Router			/tmodloader/server_config [get]
func getServerConfig(c *gin.Context) {
	c.JSON(http.StatusOK, ServerConfig{
		WorldName:  viper.GetString("tmodloader.world_name"),
		AutoCreate: viper.GetInt("tmodloader.auto_create"),
		Difficulty: viper.GetInt("tmodloader.difficulty"),
		Seed:       viper.GetString("tmodloader.seed"),
		MaxPlayers: viper.GetInt("tmodloader.max_players"),
		Password:   viper.GetString("tmodloader.password"),
		Port:       viper.GetInt("tmodloader.port"),
	})
}

// TODO: enable mod

// put godoc
// @Summary			更新 ServerConfig
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Param			body body ServerConfig true "body"
// @Success			200 {object} comm.RespOk
// @Failure			500 {object} comm.RespErr
// @Router			/tmodloader/server_config [put]
func updateServerConfig(c *gin.Context) {
	var s ServerConfig
	if err := c.ShouldBindJSON(&s); err != nil {
		c.JSON(http.StatusBadRequest, comm.NewRespErr(err))
		return
	}
	viper.Set("tmodloader.world_name", s.WorldName)
	viper.Set("tmodloader.auto_create", s.AutoCreate)
	viper.Set("tmodloader.difficulty", s.Difficulty)
	viper.Set("tmodloader.seed", s.Seed)
	viper.Set("tmodloader.max_players", s.MaxPlayers)
	viper.Set("tmodloader.password", s.Password)
	viper.Set("tmodloader.port", s.Port)
	comm.SaveConfig()
	c.JSON(http.StatusOK, comm.NewRespOk())
}

// get godoc
// @Summary			查看 Mods
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Success			200 {object} ModMap
// @Failure			500 {object} comm.RespErr
// @Router			/tmodloader/mod [get]
func getMods(c *gin.Context) {
	mods, err := getModsInDB()
	if err != nil {
		c.JSON(http.StatusInternalServerError, comm.NewRespErr(err))
		return
	}
	c.JSON(http.StatusOK, mods)
}

// post godoc
// @Summary			添加 Mods
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Param			body body ModMap true "body"
// @Success			200 {object} comm.RespOk
// @Failure			500 {object} comm.RespErr
// @Router			/tmodloader/mod [post]
func addMods(c *gin.Context) {
	mods := make(map[string]*Mod)
	if err := c.ShouldBindJSON(&mods); err != nil {
		c.JSON(http.StatusBadRequest, comm.NewRespErr(err))
		return
	}

	if err := addModsInDB(mods); err != nil {
		c.JSON(http.StatusBadRequest, comm.NewRespErr(err))
		return
	}
	c.JSON(http.StatusOK, comm.NewRespOk())
}

// del godoc
// @Summary			删除 Mods
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Param			body body ModIdList true "body"
// @Success			200 {object} comm.RespOk
// @Failure			500 {object} comm.RespErr
// @Router			/tmodloader/mod [delete]
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

// put godoc
// @Summary			更新 Mods
// @Tags			tmodloader
// @Accept			json
// @Produce			json
// @Param			body body ModMap true "body"
// @Success			200 {object} comm.RespOk
// @Failure			500 {object} comm.RespErr
// @Router			/tmodloader/mod [put]
func updateMods(c *gin.Context) {
	mods := make(map[string]*Mod)
	if err := c.ShouldBindJSON(&mods); err != nil {
		c.JSON(http.StatusBadRequest, comm.NewRespErr(err))
		return
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
// @Success			200 {object} ModIdList
// @Failure			500 {object} comm.RespErr
// @Router			/tmodloader/runtime/players [get]
func getPlayers(c *gin.Context) {
	if !Agent.Active() {
		c.JSON(http.StatusBadRequest, comm.NewRespErr("server not running"))
	}

	a := Agent.Adapter.(*AgentAdapter)
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
// @Router			/tmodloader/events [get]
func getEvents(c *gin.Context) {
	events, err := R.GetEvents()
	if err != nil {
		c.JSON(http.StatusInternalServerError, comm.NewRespErr(err))
		return
	}

	c.JSON(http.StatusOK, events)
}
