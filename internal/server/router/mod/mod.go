package mod

import (
	"dst-run/internal/comm/config"
	"dst-run/internal/comm/model"
	"dst-run/internal/server/model/common/commonresp"
	"dst-run/internal/server/model/mod/modreq"
	"dst-run/internal/server/model/mod/modresp"
	"fmt"
	"github.com/gin-gonic/gin"
	"net/http"
)

func LoadRouters(g *gin.RouterGroup) {
	g.GET("/mod", get)
	g.POST("/mod", post)
	g.DELETE("/mod", del)
	g.PUT("/mod", put)
}

// get godoc
// @Summary			查看 Mods
// @Tags			mod
// @Accept			json
// @Produce			json
// @Success			200 {object} modresp.Response
// @Failure			500 {object} commonresp.Err
// @Router			/mod [get]
func get(c *gin.Context) {
	resp := modresp.Response{Mods: []model.Mod{}}
	for id := range config.CFG.IdToMod {
		resp.Mods = append(resp.Mods, config.CFG.IdToMod[id])
	}
	c.JSON(http.StatusOK, resp)
}

// post godoc
// @Summary			添加 Mods
// @Tags			mod
// @Accept			json
// @Produce			json
// @Param			body body modreq.ModIds true "body"
// @Success			200 {object} commonresp.Ok
// @Failure			500 {object} commonresp.Err
// @Router			/mod [post]
func post(c *gin.Context) {
	body := modreq.ModIds{}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, commonresp.Err{Detail: err.Error()})
		return
	}
	for _, modId := range body.ModIds {
		if _, in := config.CFG.IdToMod[modId]; in {
			c.JSON(http.StatusBadRequest, commonresp.Err{Detail: fmt.Sprintf("Mod %s exsit", modId)})
			return
		}
	}
	var mods []model.Mod
	for _, modId := range body.ModIds {
		mod := model.Mod{
			Id:     modId,
			Enable: true,
		}
		mods = append(mods, mod)
	}
	for i := range mods {
		config.CFG.IdToMod[mods[i].Id] = mods[i]
	}
	config.Write()
	c.JSON(http.StatusOK, commonresp.Ok{})
}

// del godoc
// @Summary			删除 Mods
// @Tags			mod
// @Accept			json
// @Produce			json
// @Param			body body modreq.ModIds true "body"
// @Success			200 {object} commonresp.Ok
// @Failure			500 {object} commonresp.Err
// @Router			/mod [delete]
func del(c *gin.Context) {
	body := modreq.ModIds{}
	if err := c.ShouldBindJSON(&body); err != nil {
		c.JSON(http.StatusBadRequest, commonresp.Err{Detail: err.Error()})
		return
	}
	for _, modId := range body.ModIds {
		delete(config.CFG.IdToMod, modId)
	}
	config.Write()
	c.JSON(http.StatusOK, commonresp.Ok{})
}

// put godoc
// @Summary			更新 Mods
// @Tags			mod
// @Accept			json
// @Produce			json
// @Param			body body modreq.Mods true "body"
// @Success			200 {object} commonresp.Ok
// @Failure			500 {object} commonresp.Err
// @Router			/mod [put]
func put(c *gin.Context) {
	var mods modreq.Mods
	if err := c.ShouldBindJSON(&mods); err != nil {
		c.JSON(http.StatusBadRequest, commonresp.Err{Detail: err.Error()})
		return
	}
	for i := range mods.Mods {
		if _, in := config.CFG.IdToMod[mods.Mods[i].Id]; !in {
			c.JSON(http.StatusBadRequest, commonresp.Err{Detail: fmt.Sprintf("Mod not exsit")})
			return
		}
	}
	for i := range mods.Mods {
		config.CFG.IdToMod[mods.Mods[i].Id] = mods.Mods[i]
	}
	config.Write()
	c.JSON(http.StatusOK, commonresp.Ok{})
}
