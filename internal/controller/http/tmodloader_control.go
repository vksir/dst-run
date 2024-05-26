package http

import (
	"dst-run/internal/usecase"
	"dst-run/pkg/log"
	"fmt"
	"github.com/gin-gonic/gin"
)

type tModLoaderControlRoute struct {
	u usecase.TModLoaderControl
	l log.Interface
}

func newTModLoaderControlRoute(handle *gin.RouterGroup, u usecase.TModLoaderControl, l log.Interface) {
	r := &tModLoaderControlRoute{u, l}

	g := handle.Group("/tmodloader")
	{
		g.GET("/control/:action", r.control)
	}
}

// @Summary			服务器控制
// @Tags			tmodloader_control
// @Accept			json
// @Produce			json
// @Param			action path string true "[ start | stop | restart | update | install ]"
// @Success			200 {object} response
// @Failure			500 {object} response
// @Router			/api/tmodloader/control/{action} [post]
func (r *tModLoaderControlRoute) control(c *gin.Context) {
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
