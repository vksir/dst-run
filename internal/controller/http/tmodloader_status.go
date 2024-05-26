package http

import (
	"dst-run/internal/usecase"
	"dst-run/pkg/log"
	"github.com/gin-gonic/gin"
)

type tModLoaderStatusRoute struct {
	u usecase.TModLoaderStatus
	l log.Interface
}

func newTModLoaderStatusRoute(handle *gin.RouterGroup, u usecase.TModLoaderStatus, l log.Interface) {
	r := &tModLoaderStatusRoute{u, l}

	g := handle.Group("/tmodloader")
	{
		g.GET("/status", r.getStatus)
	}
}

// @Summary			获取服务器状态
// @Tags			tmodloader_status
// @Accept			json
// @Produce			json
// @Success			200 {object} entity.TModLoaderStatus
// @Failure			500 {object} response
// @Router			/api/tmodloader/status [get]
func (r *tModLoaderStatusRoute) getStatus(c *gin.Context) {
	status, err := r.u.GetStatus(c)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}

	autoResp(c, CodeOk, status)
}
