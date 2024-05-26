package http

import (
	"dst-run/internal/entity"
	"dst-run/internal/usecase"
	"dst-run/pkg/log"
	"github.com/gin-gonic/gin"
)

type dontStarveClusterRoute struct {
	u usecase.DontStarveCluster
	l log.Interface
}

func newDontStarveClusterRoute(handler *gin.RouterGroup, u usecase.DontStarveCluster, l log.Interface) {
	r := &dontStarveClusterRoute{u, l}

	g := handler.Group("/dontstarve")
	{
		g.GET("/cluster", r.getClusters)
		g.POST("/cluster", r.createCluster)
		g.DELETE("/cluster", r.deleteCluster)
		g.PUT("/cluster", r.updateCluster)
	}
}

// @Summary			获取存档列表
// @Tags			dontstarve_cluster
// @Accept			json
// @Produce			json
// @Success			200 {object} []entity.DontStarveCluster
// @Failure			500 {object} response
// @Router			/api/dontstarve/clusters [get]
func (r *dontStarveClusterRoute) getClusters(c *gin.Context) {
	clusters, err := r.u.GetClusters(c)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, clusters)
}

// @Summary			获取存档信息
// @Tags			dontstarve_cluster
// @Accept			json
// @Produce			json
// @Success			200 {object} entity.DontStarveCluster
// @Failure			500 {object} response
// @Router			/api/dontstarve/cluster/{id} [get]
func (r *dontStarveClusterRoute) getCluster(c *gin.Context) {
	id := c.Param("id")
	cluster, err := r.u.GetCluster(c, id)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, cluster)
}

// @Summary			创建存档
// @Tags			dontstarve_cluster
// @Accept			json
// @Produce			json
// @Success			200 {object} entity.DontStarveCluster
// @Failure			500 {object} response
// @Router			/api/dontstarve/cluster/ [post]
func (r *dontStarveClusterRoute) createCluster(c *gin.Context) {
	cluster, err := r.u.CreateCluster(c)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, cluster)
}

// @Summary			删除存档
// @Tags			dontstarve_cluster
// @Accept			json
// @Produce			json
// @Success			200 {object} response
// @Failure			500 {object} response
// @Router			/api/dontstarve/cluster/{id} [delete]
func (r *dontStarveClusterRoute) deleteCluster(c *gin.Context) {
	id := c.Param("id")
	err := r.u.DeleteCluster(c, id)
	if err != nil {
		autoResp(c, CodeInternal, err)
		return
	}
	autoResp(c, CodeOk, nil)
}

// @Summary			更新存档
// @Tags			dontstarve_cluster
// @Accept			json
// @Produce			json
// @Param			request body entity.DontStarveCluster true "body"
// @Success			200 {object} entity.DontStarveCluster
// @Failure			500 {object} response
// @Router			/api/dontstarve/cluster/{id} [put]
func (r *dontStarveClusterRoute) updateCluster(c *gin.Context) {
	var cluster entity.DontStarveCluster
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
