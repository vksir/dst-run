package control

import (
	"dst-run/internal/controller"
	"dst-run/internal/server/model/action/actionreq"
	"dst-run/internal/server/model/common/commonresp"
	"fmt"
	"github.com/gin-gonic/gin"
	"net/http"
)

func LoadRouters(g *gin.RouterGroup) {
	g.POST("/control/:action", control)
}

// control godoc
// @Summary			服务器控制
// @Tags			control
// @Accept			json
// @Produce			json
// @Param			action path string true "[ start | stop | restart ]"
// @Success			200 {object} commonresp.Ok
// @Failure			500 {object} commonresp.Err
// @Router			/control/{action} [post]
func control(c *gin.Context) {
	params := actionreq.Params{}
	if err := c.ShouldBindUri(&params); err != nil {
		c.JSON(http.StatusBadRequest, commonresp.Err{Detail: err.Error()})
		return
	}
	switch params.Action {
	case "start":
		if err := controller.Start(); err != nil {
			c.JSON(http.StatusInternalServerError, commonresp.Err{Detail: err.Error()})
			return
		}
	case "stop":
		if err := controller.Stop(); err != nil {
			c.JSON(http.StatusInternalServerError, commonresp.Err{Detail: err.Error()})
			return
		}
	case "restart":
		if err := controller.Restart(); err != nil {
			c.JSON(http.StatusInternalServerError, commonresp.Err{Detail: err.Error()})
			return
		}
	default:
		c.JSON(http.StatusBadRequest, commonresp.Err{Detail: fmt.Sprintf("Invalid action: %s", params.Action)})
		return
	}
	c.JSON(http.StatusOK, commonresp.Ok{})
}
