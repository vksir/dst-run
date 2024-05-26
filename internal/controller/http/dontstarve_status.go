package http

import (
	"dst-run/internal/usecase"
	"dst-run/pkg/log"
	"github.com/gin-gonic/gin"
)

type dontStarveStatusRoute struct {
	u usecase.DontStarveStatus
	l log.Interface
}

func newDontStarveStatusRoute(handle *gin.RouterGroup, u usecase.DontStarveStatus, l log.Interface) {
	r := &dontStarveStatusRoute{u, l}

	g := handle.Group("/dontstarve")
	{
		g.GET("/status", r.getStatus)
	}
}

// @Summary			获取服务器状态
// @Tags			dontstarve_status
// @Accept			json
// @Produce			json
// @Success			200 {object} entity.DontStarveStatus
// @Failure			500 {object} response
// @Router			/api/dontstarve/status [get]
func (r *dontStarveStatusRoute) getStatus(c *gin.Context) {
	status, err := r.u.GetStatus(c)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}

	autoResp(c, CodeOk, status)
}
