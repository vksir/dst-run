package swagger

import (
	_ "dst-run/docs"
	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
	"net/http"
)

func LoadRouters(g *gin.RouterGroup) {
	g.GET("/docs", redirect)
	g.GET("/docs/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
}

func redirect(c *gin.Context) {
	c.Redirect(http.StatusMovedPermanently, "/docs/index.html")
}
