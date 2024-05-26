package http

import (
	"dst-run/internal/usecase"
	"dst-run/pkg/log"
	"github.com/gin-gonic/gin"
	"strconv"
)

type dontStarveConsoleRoute struct {
	u usecase.DontStarveConsole
	l log.Interface
}

func newDontStarveConsoleRoute(handler *gin.RouterGroup, u usecase.DontStarveConsole, l log.Interface) {
	r := &dontStarveConsoleRoute{u, l}

	g := handler.Group("/dontstarve")
	{
		g.GET("/console/player", r.getPlayers)
		g.GET("/console/announce/:msg", r.announce)
		g.GET("/console/regenerate", r.regenerate)
		g.GET("/console/rollback/:days", r.rollback)
	}
}

// @Summary			获取当前玩家
// @Tags			dontstarve_console
// @Accept			json
// @Produce			json
// @Success			200 {object} []string
// @Failure			500 {object} response
// @Router			/api/dontstarve/console/player [get]
func (r *dontStarveConsoleRoute) getPlayers(c *gin.Context) {
	players, err := r.u.GetPlayers(c)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}

	autoResp(c, CodeOk, players)
}

// @Summary			全服宣告
// @Tags			dontstarve_console
// @Accept			json
// @Produce			json
// @Param			msg path string true "msg"
// @Success			200 {object} response
// @Failure			500 {object} response
// @Router			/api/dontstarve/console/announce/{msg} [post]
func (r *dontStarveConsoleRoute) announce(c *gin.Context) {
	msg := c.Param("msg")
	err := r.u.Announce(c, msg)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}

	autoResp(c, CodeOk, nil)
}

// @Summary			重新生成世界
// @Tags			dontstarve_console
// @Accept			json
// @Produce			json
// @Success			200 {object} response
// @Failure			500 {object} response
// @Router			/api/dontstarve/console/regenerate [post]
func (r *dontStarveConsoleRoute) regenerate(c *gin.Context) {
	err := r.u.Regenerate(c)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}

	autoResp(c, CodeOk, nil)
}

// @Summary			回滚
// @Tags			dontstarve_console
// @Accept			json
// @Produce			json
// @Param			times path int true "msg"
// @Success			200 {object} response
// @Failure			500 {object} response
// @Router			/api/dontstarve/console/rollback{days} [post]
func (r *dontStarveConsoleRoute) rollback(c *gin.Context) {
	daysString := c.Param("days")
	days, err := strconv.Atoi(daysString)
	if err != nil {
		autoResp(c, CodeBadRequest, "params days must be int")
		return
	}

	err = r.u.Rollback(c, days)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}

	autoResp(c, CodeOk, nil)
}
