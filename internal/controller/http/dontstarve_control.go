package http

import (
	"dst-run/internal/usecase"
	"dst-run/pkg/log"
	"fmt"
	"github.com/gin-gonic/gin"
)

type dontStarveControlRoute struct {
	u usecase.DontStarveControl
	l log.Interface
}

func newDontStarveControlRoute(handle *gin.RouterGroup, u usecase.DontStarveControl, l log.Interface) {
	r := &dontStarveControlRoute{u, l}

	g := handle.Group("/dontstarve")
	{
		g.GET("/control/:action", r.control)
	}
}

// @Summary			服务器控制
// @Tags			dontstarve_control
// @Accept			json
// @Produce			json
// @Param			action path string true "[ start | stop | restart | update | install ]"
// @Success			200 {object} response
// @Failure			500 {object} response
// @Router			/api/dontstarve/control/{action} [post]
func (r *dontStarveControlRoute) control(c *gin.Context) {
	action := c.Param("action")
	clusterId := c.Query("cluster")

	var err error
	switch action {
	case "start":
		err = r.u.Start(c, clusterId)
	case "stop":
		err = r.u.Stop(c)
	case "restart":
		err = r.u.Restart(c, clusterId)
	case "update":
		err = r.u.Update(c)
	case "install":
		err = r.u.Install(c)
	default:
		autoResp(c, CodeBadRequest, fmt.Errorf("invalid action: %s", action))
	}

	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, nil)
}
