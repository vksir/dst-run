package http

import (
	"dst-run/internal/entity"
	"dst-run/internal/usecase"
	"dst-run/pkg/log"
	"github.com/gin-gonic/gin"
	"io"
	"strings"
)

type dontStarveModRoute struct {
	u usecase.DontStarveMod
	l log.Interface
}

func newDontStarveModRoute(handler *gin.RouterGroup, u usecase.DontStarveMod, l log.Interface) {
	r := &dontStarveModRoute{u, l}

	g := handler.Group("/dontstarve")
	{
		g.GET("/mod", r.getMods)
		g.POST("/mod/mod_id", r.addModsFromId)
		g.DELETE("/mod", r.delMods)
		g.PUT("/mod", r.updateMods)
	}
}

// @Summary			查看 Mods
// @Tags			dontstarve_mod
// @Accept			json
// @Produce			json
// @Success			200 {object} []entity.DontStarveMod
// @Failure			500 {object} response
// @Router			/api/dontstarve/mod [get]
func (r *dontStarveModRoute) getMods(c *gin.Context) {
	mods, err := r.u.GetMods(c)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, mods)
}

// @Summary			通过 Mod ID 添加 Mods
// @Tags			dontstarve_mod
// @Accept			plain
// @Produce			json
// @Param			request body string true "多个 Mod ID 一行一个"
// @Success			200 {object} response
// @Failure			500 {object} response
// @Router			/api/dontstarve/mod/mod_id [post]
func (r *dontStarveModRoute) addModsFromId(c *gin.Context) {
	bytes, err := io.ReadAll(c.Request.Body)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}

	var mods []entity.DontStarveMod
	rawModIds := strings.Split(string(bytes), "\n")
	for _, id := range rawModIds {
		if id != "" {
			mods = append(mods, entity.DontStarveMod{ModId: id})
		}
	}

	mods = r.u.FetchModsName(c, mods)
	err = r.u.CreateMods(c, mods)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, nil)
}

// @Summary			删除 Mods
// @Tags			dontstarve_mod
// @Accept			json
// @Produce			json
// @Param			request body []string true "body"
// @Success			200 {object} response
// @Failure			500 {object} response
// @Router			/api/dontstarve/mod [delete]
func (r *dontStarveModRoute) delMods(c *gin.Context) {
	var modIds []string
	if err := c.ShouldBindJSON(&modIds); err != nil {
		autoResp(c, CodeBadRequest, err)
		return
	}

	err := r.u.DeleteModsByModIds(c, modIds)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, nil)
}

// @Summary			更新 Mods
// @Tags			dontstarve_mod
// @Accept			json
// @Produce			json
// @Param   		update_mod_info query string false "[ true | false ]"
// @Param			request body []entity.DontStarveMod true "body"
// @Success			200 {object} response
// @Failure			500 {object} response
// @Router			/api/dontstarve/mod [put]
func (r *dontStarveModRoute) updateMods(c *gin.Context) {
	var mods []entity.DontStarveMod
	if err := c.ShouldBindJSON(&mods); err != nil {
		autoResp(c, CodeBadRequest, err)
		return
	}

	updateModInfo := c.Query("update_mod_info")
	if updateModInfo == "true" {
		mods = r.u.FetchModsName(c, mods)
	}

	err := r.u.UpdateMods(c, mods)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, nil)
}
