package http

import (
	"dst-run/internal/comm"
	"dst-run/internal/entity"
	"dst-run/internal/usecase"
	"dst-run/pkg/log"
	"github.com/gin-gonic/gin"
	"net/http"
	"sync"
)

type tModLoaderClusterRoute struct {
	u             usecase.TModLoaderCluster
	l             log.Interface
	transportLock sync.Mutex
}

func newTModLoaderClusterRoute(handler *gin.RouterGroup, u usecase.TModLoaderCluster, l log.Interface) {
	r := &tModLoaderClusterRoute{u: u, l: l}

	g := handler.Group("/tmodloader")
	{
		g.GET("/cluster", r.getClusters)
		g.POST("/cluster", r.createCluster)
		g.DELETE("/cluster", r.deleteCluster)
		g.PUT("/cluster", r.updateCluster)
	}
}

// @Summary			获取存档列表
// @Tags			tmodloader_cluster
// @Accept			json
// @Produce			json
// @Success			200 {object} []entity.TModLoaderCluster
// @Failure			500 {object} response
// @Router			/api/tmodloader/clusters [get]
func (r *tModLoaderClusterRoute) getClusters(c *gin.Context) {
	clusters, err := r.u.GetClusters(c)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, clusters)
}

// @Summary			获取存档信息
// @Tags			tmodloader_cluster
// @Accept			json
// @Produce			json
// @Success			200 {object} entity.TModLoaderCluster
// @Failure			500 {object} response
// @Router			/api/tmodloader/cluster/{id} [get]
func (r *tModLoaderClusterRoute) getCluster(c *gin.Context) {
	id := c.Param("id")
	cluster, err := r.u.GetCluster(c, id)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, cluster)
}

// @Summary			创建存档
// @Tags			tmodloader_cluster
// @Accept			json
// @Produce			json
// @Success			200 {object} entity.TModLoaderCluster
// @Failure			500 {object} response
// @Router			/api/tmodloader/cluster/ [post]
func (r *tModLoaderClusterRoute) createCluster(c *gin.Context) {
	cluster, err := r.u.CreateCluster(c)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, cluster)
}

// @Summary			删除存档
// @Tags			tmodloader_cluster
// @Accept			json
// @Produce			json
// @Success			200 {object} response
// @Failure			500 {object} response
// @Router			/api/tmodloader/cluster/{id} [delete]
func (r *tModLoaderClusterRoute) deleteCluster(c *gin.Context) {
	id := c.Param("id")
	err := r.u.DeleteCluster(c, id)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, nil)
}

// @Summary			更新存档
// @Tags			tmodloader_cluster
// @Accept			json
// @Produce			json
// @Param			request body entity.TModLoaderCluster true "body"
// @Success			200 {object} entity.TModLoaderCluster
// @Failure			500 {object} response
// @Router			/api/tmodloader/cluster/{id} [put]
func (r *tModLoaderClusterRoute) updateCluster(c *gin.Context) {
	var cluster entity.TModLoaderCluster
	if err := c.ShouldBindJSON(&cluster); err != nil {
		autoResp(c, CodeBadRequest, err)
		return
	}

	id := c.Param("id")
	cluster, err := r.u.UpdateCluster(c, id, cluster)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, cluster)
}

// @Summary			下载存档
// @Tags			tmodloader_cluster
// @Accept			json
// @Produce			json
// @Param   		name query string false "name"
// @Success			200 {object} response
// @Failure			500 {object} response
// @Router			/api/tmodloader/archive/download [get]
func (r *tModLoaderClusterRoute) downloadArchive(c *gin.Context) {
	if ok := r.transportLock.TryLock(); !ok {
		c.JSON(http.StatusBadRequest, entity.NewRespErr(comm.ErrBusy))
	}
	defer r.transportLock.Unlock()

	//name := c.Query("name")

	//targetPath := filepath.Join(dataDir, time.Now().Format(time.RFC3339))
	//if err := util.Compress(targetPath, archiveDir, name); err != nil {
	//	http2.autoResp(c, http2.CodeBadRequest, err)
	//	return
	//}
	//defer func(path string) {
	//	if err := util.RmvPath(path); err != nil {
	//		log.Error("rmv failed: %s", path)
	//	}
	//}(targetPath)

	//c.File(targetPath)
}
