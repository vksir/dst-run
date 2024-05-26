package http

import (
	"dst-run/internal/entity"
	"dst-run/internal/usecase"
	"dst-run/pkg/log"
	"github.com/gin-gonic/gin"
)

type dontStarveConfigRoute struct {
	u usecase.DontStarveConfig
	l log.Interface
}

func newDontStarveConfigRoute(handler *gin.RouterGroup, u usecase.DontStarveConfig, l log.Interface) {
	r := dontStarveConfigRoute{u: u, l: l}

	g := handler.Group("/dontstarve")
	{
		g.GET("/config", r.getConfig)
		g.PUT("/config", r.updateConfig)
	}
}

// @Summary			查看配置
// @Tags			dontstarve_config
// @Accept			json
// @Produce			json
// @Success			200 {object} entity.DontStarveConfig
// @Failure			500 {object} response
// @Router			/api/dontstarve/config [get]
func (r *dontStarveConfigRoute) getConfig(c *gin.Context) {
	config, err := r.u.GetConfig(c)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}

	autoResp(c, CodeOk, config)
}

// updateConfig
// @Summary			更新配置
// @Tags			dontstarve_config
// @Accept			json
// @Produce			json
// @Success			200 {object} entity.DontStarveConfig
// @Failure			500 {object} response
// @Router			/api/dontstarve/config [put]
func (r *dontStarveConfigRoute) updateConfig(c *gin.Context) {
	var config entity.DontStarveConfig
	if err := c.ShouldBindJSON(&config); err != nil {
		autoResp(c, CodeBadRequest, err)
		return
	}

	config, err := r.u.UpdateConfig(c, config)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}

	autoResp(c, CodeOk, config)
}
