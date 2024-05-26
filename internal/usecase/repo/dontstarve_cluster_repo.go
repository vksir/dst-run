package repo

import (
	"context"
	"dst-run/internal/entity"
	"gorm.io/gorm"
)

type DontStarveClusterRepo struct {
	*gorm.DB
	clusterRepo *Repo[entity.DontStarveCluster]
	worldRepo   *Repo[entity.DontStarveWorld]
	modRepo     *Repo[entity.DontStarveModInCluster]
}

func NewDontStarveClusterRepo(db *gorm.DB) *DontStarveClusterRepo {
	return &DontStarveClusterRepo{
		db,
		NewRepo[entity.DontStarveCluster](db),
		NewRepo[entity.DontStarveWorld](db),
		NewRepo[entity.DontStarveModInCluster](db),
	}
}

func (r *DontStarveClusterRepo) GetClusters(ctx context.Context) ([]entity.DontStarveCluster, error) {
	return r.clusterRepo.GetAll(ctx)
}

func (r *DontStarveClusterRepo) GetCluster(ctx context.Context, id string) (entity.DontStarveCluster, error) {
	return r.clusterRepo.GetOne(ctx, id)
}

func (r *DontStarveClusterRepo) CreateClusters(ctx context.Context, clusters ...*entity.DontStarveCluster) error {
	return r.clusterRepo.Creates(ctx, clusters...)
}

func (r *DontStarveClusterRepo) DeleteClusters(ctx context.Context, ids ...string) error {
	return r.clusterRepo.Deletes(ctx, ids...)
}

func (r *DontStarveClusterRepo) UpdateCluster(ctx context.Context, id string, cluster entity.DontStarveCluster) error {
	cluster.Id = id
	res := r.WithContext(ctx).Select("*").Omit("Worlds", "Mods").Updates(&cluster)
	return res.Error
}

func (r *DontStarveClusterRepo) GetWorld(ctx context.Context, id string) (entity.DontStarveWorld, error) {
	return r.worldRepo.GetOne(ctx, id)
}

func (r *DontStarveClusterRepo) CreateWorlds(ctx context.Context, clusterId string, worlds ...*entity.DontStarveWorld) error {
	var cluster entity.DontStarveCluster
	cluster.Id = clusterId
	err := r.WithContext(ctx).Model(&cluster).Association("Worlds").Append(&worlds)
	return err
}

func (r *DontStarveClusterRepo) DeleteWorlds(ctx context.Context, ids ...string) error {
	return r.worldRepo.Deletes(ctx, ids...)
}

func (r *DontStarveClusterRepo) UpdateWorld(ctx context.Context, id string, world entity.DontStarveWorld) error {
	return r.worldRepo.Update(ctx, id, world)
}

func (r *DontStarveClusterRepo) GetMod(ctx context.Context, id string) (entity.DontStarveModInCluster, error) {
	return r.modRepo.GetOne(ctx, id)
}

func (r *DontStarveClusterRepo) CreateMods(ctx context.Context, clusterId string, mods ...*entity.DontStarveModInCluster) error {
	var cluster entity.DontStarveCluster
	cluster.Id = clusterId
	err := r.WithContext(ctx).Model(&cluster).Association("Mods").Append(&mods)
	return err
}

func (r *DontStarveClusterRepo) DeleteMods(ctx context.Context, ids ...string) error {
	return r.modRepo.Deletes(ctx, ids...)
}

func (r *DontStarveClusterRepo) UpdateMod(ctx context.Context, id string, mod entity.DontStarveModInCluster) error {
	mod.Id = id
	res := r.WithContext(ctx).Select("*").Omit("Mod").Updates(&mod)
	return res.Error
}
