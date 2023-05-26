package serverconfig

import (
	"dst-run/internal/comm/config"
	"dst-run/internal/server/model/common/commonresp"
	"dst-run/internal/server/model/serverconfig/serverconfigreq"
	"dst-run/internal/server/model/serverconfig/serverconfigresp"
	"github.com/gin-gonic/gin"
	"net/http"
)

func LoadRouters(g *gin.RouterGroup) {
	g.GET("/server_config", get)
	g.PUT("/server_config", put)
}

// get godoc
// @Summary			查看 Server Config
// @Tags			server_config
// @Accept			json
// @Produce			json
// @Success			200 {object} serverconfigresp.ServerConfig
// @Failure			500 {object} commonresp.Err
// @Router			/server_config [get]
func get(c *gin.Context) {
	c.JSON(http.StatusOK, serverconfigresp.ServerConfig{
		ServerConfig: config.CFG.ServerConfig,
	})
}

// put godoc
// @Summary			更新 Server Config
// @Tags			server_config
// @Accept			json
// @Produce			json
// @Param			body body serverconfigreq.ServerConfig true "body"
// @Success			200 {object} commonresp.Ok
// @Failure			500 {object} commonresp.Err
// @Router			/server_config [put]
func put(c *gin.Context) {
	var serverConfig serverconfigreq.ServerConfig
	if err := c.ShouldBindJSON(&serverConfig); err != nil {
		c.JSON(http.StatusBadRequest, commonresp.Err{Detail: err.Error()})
		return
	}
	config.CFG.ServerConfig = serverConfig.ServerConfig
	config.Write()
	c.JSON(http.StatusOK, commonresp.Ok{})
}
