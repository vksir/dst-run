package http

import (
	"dst-run/internal/usecase"
	"dst-run/pkg/log"
	"github.com/gin-gonic/gin"
)

type tModLoaderConsoleRoute struct {
	u usecase.TModLoaderConsole
	l log.Interface
}

func newTModLoaderConsoleRoute(handler *gin.RouterGroup, u usecase.TModLoaderConsole, l log.Interface) {
	r := &tModLoaderConsoleRoute{u, l}

	g := handler.Group("/tmodloader")
	{
		g.GET("/console/player", r.getPlayers)
	}
}

// @Summary			获取当前玩家
// @Tags			tmodloader_console
// @Accept			json
// @Produce			json
// @Success			200 {object} []string
// @Failure			500 {object} response
// @Router			/api/tmodloader/console/player [get]
func (r *tModLoaderConsoleRoute) getPlayers(c *gin.Context) {
	// "playing"
	players, err := r.u.GetPlayers(c)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}

	autoResp(c, CodeOk, players)
}
