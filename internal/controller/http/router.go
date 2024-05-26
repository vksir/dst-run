package http

import (
	_ "dst-run/docs"
	"dst-run/internal/usecase"
	"dst-run/pkg/log"
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

// NewRouter
// Swagger spec:
// @title           Aurora Admin
// @description 	Aurora Admin API
// @version     	1.0
// @host        	0.0.0.0:5800
// @BasePath    	/api
func NewRouter(handler *gin.Engine, uc *usecase.UseCase, l log.Interface) {
	g := handler.Group("/api")
	{
		loadSwaggerRouters(g)

		newDontStarveClusterRoute(g, uc.DontStarveClusterUseCase, l)
		newDontStarveConfigRoute(g, uc.DontStarveConfigUseCase, l)
		newDontStarveConsoleRoute(g, uc.DontStarveConsoleUseCase, l)
		newDontStarveControlRoute(g, uc.DontStarveControlUseCase, l)
		newDontStarveEventRoute(g, uc.DontStarveEventUseCase, l)
		newDontStarveModRoute(g, uc.DontStarveModUseCase, l)
		newDontStarveStatusRoute(g, uc.DontStarveStatusUseCase, l)
	}
}
