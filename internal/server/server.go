package server

import (
	"dst-run/internal/server/router/control"
	"dst-run/internal/server/router/game"
	"dst-run/internal/server/router/mod"
	"dst-run/internal/server/router/serverconfig"
	"dst-run/internal/server/swagger"
	"github.com/gin-gonic/gin"
	"github.com/spf13/viper"
	"log"
)

// @title           Terraria Run
// @version         1.0

func Run() {
	e := gin.Default()
	loadRouters(e)
	err := e.Run(viper.GetString("ns.listen"))
	if err != nil {
		log.Panic(err)
	}
}

func loadRouters(e *gin.Engine) {
	publicGroup := e.Group("")
	control.LoadRouters(publicGroup)
	mod.LoadRouters(publicGroup)
	swagger.LoadRouters(publicGroup)
	game.LoadRouters(publicGroup)
	serverconfig.LoadRouters(publicGroup)
}
