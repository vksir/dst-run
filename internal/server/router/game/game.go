package game

import (
	"dst-run/internal/controller"
	"dst-run/internal/report"
	"dst-run/internal/server/model/common/commonresp"
	"dst-run/internal/server/model/game/gameresp"
	"fmt"
	"github.com/gin-gonic/gin"
	"net/http"
)

func LoadRouters(g *gin.RouterGroup) {
	g.GET("/game/players", getPlayers)
	g.GET("/game/events", getEvents)
}

// getPlayers godoc
// @Summary			查看当前玩家
// @Tags			game
// @Accept			json
// @Produce			json
// @Success			200 {object} gameresp.Players
// @Failure			500 {object} commonresp.Err
// @Router			/game/players [get]
func getPlayers(c *gin.Context) {
	if controller.Status != controller.StatusActive {
		c.JSON(http.StatusBadRequest, commonresp.Err{
			Detail: fmt.Sprintf("Status is %s, cannot get players", controller.Status),
		})
		return
	}
	out, err := controller.Agent.RunCmd("playing")
	if err != nil {
		c.JSON(http.StatusInternalServerError, commonresp.Err{Detail: err.Error()})
		return
	}
	c.JSON(http.StatusOK, gameresp.Players{Players: []string{out}})
}

// getEvents godoc
// @Summary			查看当前事件
// @Description		Event Type: [ SERVER_ACTIVE ]
// @Tags			game
// @Accept			json
// @Produce			json
// @Success			200 {object} gameresp.Events
// @Failure			500 {object} commonresp.Err
// @Router			/game/events [get]
func getEvents(c *gin.Context) {
	events, err := report.R.GetEvents()
	if err != nil {
		c.JSON(http.StatusInternalServerError, commonresp.Err{Detail: err.Error()})
		return
	}
	respEvents := gameresp.Events{
		Events: []gameresp.Event{},
	}
	for i := range events {
		respEvents.Events = append(respEvents.Events, gameresp.Event{
			Level: events[i].Level,
			Time:  events[i].Time,
			Msg:   events[i].Msg,
			Type:  events[i].Type,
		})
	}
	c.JSON(http.StatusOK, respEvents)
}
