package server

import (
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
