package http

import (
	"dst-run/internal/usecase"
	"dst-run/pkg/log"
	"github.com/gin-gonic/gin"
)

type dontStarveEventRoute struct {
	u usecase.DontStarveEvent
	l log.Interface
}

func newDontStarveEventRoute(handle *gin.RouterGroup, u usecase.DontStarveEvent, l log.Interface) {
	r := &dontStarveEventRoute{u, l}

	g := handle.Group("/dontstarve")
	{
		g.GET("/event", r.getEvents)
	}
}

// @Summary			获取最近事件
// @Description		ReportEvent Type: [ SERVER_ACTIVE ]
// @Tags			dontstarve_event
// @Accept			json
// @Produce			json
// @Success			200 {object} []entity.DontStarveEvent
// @Failure			500 {object} response
// @Router			/api/dontstarve/event [get]
func (r *dontStarveEventRoute) getEvents(c *gin.Context) {
	events, err := r.u.GetEvents(c)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}

	autoResp(c, CodeOk, events)
}
