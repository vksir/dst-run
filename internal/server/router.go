package server

import (
	_ "dst-run/docs"
	"dst-run/internal/adapter/tmodloader"
	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
	"net/http"
)

func loadSwaggerRouters(g *gin.RouterGroup) {
	g.GET("/docs", redirectSwagger)
	g.GET("/docs/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
}

func redirectSwagger(c *gin.Context) {
	c.Redirect(http.StatusMovedPermanently, "/docs/index.html")
}

func loadRouters(e *gin.Engine) {
	publicGroup := e.Group("/")
	loadSwaggerRouters(publicGroup)
	tmodloader.LoadRouters(publicGroup)
}
