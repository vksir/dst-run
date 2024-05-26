package usecase

import (
	"context"
	"dst-run/assets"
	"dst-run/internal/entity"
	"dst-run/pkg/log"
	"fmt"
	"github.com/google/uuid"
)

type DontStarveClusterUseCase struct {
	repo    DontStarveClusterRepo
	driver  DontStarveClusterDriver
	l       log.Interface
	modRepo DontStarveModRepo
}

func NewDontStarveClusterUseCase(repo DontStarveClusterRepo, driver DontStarveClusterDriver,
	l log.Interface, modRepo DontStarveModRepo) *DontStarveClusterUseCase {
	return &DontStarveClusterUseCase{
		repo:    repo,
		driver:  driver,
		l:       l.WithTag("DontStarveClusterUseCase"),
		modRepo: modRepo,
	}
}

func (u *DontStarveClusterUseCase) GetClusters(ctx context.Context) ([]entity.DontStarveCluster, error) {
	return u.repo.GetClusters(ctx)
}

func (u *DontStarveClusterUseCase) GetCluster(ctx context.Context, id string) (entity.DontStarveCluster, error) {
	return u.repo.GetCluster(ctx, id)
}

func (u *DontStarveClusterUseCase) CreateCluster(ctx context.Context) (entity.DontStarveCluster, error) {
	cluster := entity.DontStarveCluster{
		Model: entity.Model{
			Id: uuid.New().String(),
		},
		ClusterName:        "Aurora",
		ClusterPassword:    "6666",
		ClusterDescription: "Just Have Fun",
		MaxPlayers:         "6",
		Pvp:                "false",
		Worlds: []entity.DontStarveWorld{
			{
				Type:          "Master",
				ServerConfig:  assets.DontStarveMasterServerIni,
				WorldOverride: assets.DontStarveMasterOverride,
			},
			{
				Type:          "Caves",
				ServerConfig:  assets.DontStarveCavesServerIni,
				WorldOverride: assets.DontStarveCavesOverride,
			},
		},
		Mods: make([]entity.DontStarveModInCluster, 0),
	}

	err := u.driver.CreateCluster(ctx, cluster)
	if err != nil {
		return cluster, err
	}

	err = u.repo.CreateClusters(ctx, &cluster)
	if err != nil {
		u.l.ErrorC(ctx, "repo create failed: cluster=%+v, err=%v", cluster, err)
		return cluster, err
	}

	return cluster, nil
}

func (u *DontStarveClusterUseCase) DeleteCluster(ctx context.Context, id string) error {
	err := u.driver.DeleteCluster(ctx, id)
	if err != nil {
		return err
	}

	err = u.repo.DeleteClusters(ctx, id)
	if err != nil {
		u.l.ErrorC(ctx, "repo delete failed: id=%s, err=%v", id, err)
		return err
	}

	return nil
}

func (u *DontStarveClusterUseCase) UpdateCluster(ctx context.Context, id string, cluster entity.DontStarveCluster) (entity.DontStarveCluster, error) {
	err := u.driver.UpdateCluster(ctx, cluster)
	if err != nil {
		return cluster, err
	}

	err = u.repo.UpdateCluster(ctx, id, cluster)
	if err != nil {
		u.l.ErrorC(ctx, "repo update failed: id=%s, cluster=%+v, err=%v", id, cluster, err)
		return cluster, err
	}

	currentCluster, err := u.repo.GetCluster(ctx, id)
	return currentCluster, err
}

func (u *DontStarveClusterUseCase) CreateWorld(ctx context.Context, clusterId string, worldType string) (entity.DontStarveWorld, error) {
	var serverConfig string
	var worldOverride string
	if worldType == "Master" {
		serverConfig = assets.DontStarveMasterServerIni
		worldOverride = assets.DontStarveMasterOverride
	} else if worldType == "Caves" {
		serverConfig = assets.DontStarveCavesServerIni
		worldOverride = assets.DontStarveCavesOverride
	} else {
		return entity.DontStarveWorld{}, fmt.Errorf("invlid world type: %s", worldType)
	}

	world := entity.DontStarveWorld{
		Model:               entity.Model{},
		Type:                worldType,
		ServerConfig:        serverConfig,
		WorldOverride:       worldOverride,
		DontStarveClusterId: clusterId,
	}

	err := u.repo.CreateWorlds(ctx, clusterId, &world)
	if err != nil {
		return entity.DontStarveWorld{}, err
	}

	cluster, err := u.repo.GetCluster(ctx, clusterId)
	if err != nil {
		return entity.DontStarveWorld{}, err
	}

	err = u.driver.CreateWorld(ctx, cluster)
	if err != nil {
		return entity.DontStarveWorld{}, err
	}

	return world, nil
}

func (u *DontStarveClusterUseCase) DeleteWorld(ctx context.Context, clusterId, worldId string) error {
	world, err := u.repo.GetWorld(ctx, worldId)
	if err != nil {
		return err
	}

	err = u.driver.DeleteWorld(ctx, clusterId, world.Type)
	if err != nil {
		return err
	}

	err = u.repo.DeleteWorlds(ctx, worldId)
	if err != nil {
		return err
	}

	return nil
}

func (u *DontStarveClusterUseCase) UpdateWorld(ctx context.Context, clusterId, worldId string, world entity.DontStarveWorld) (entity.DontStarveWorld, error) {
	err := u.repo.UpdateWorld(ctx, worldId, world)
	if err != nil {
		return world, err
	}

	cluster, err := u.repo.GetCluster(ctx, clusterId)
	if err != nil {
		return entity.DontStarveWorld{}, err
	}

	err = u.driver.UpdateWorld(ctx, cluster)
	if err != nil {
		return world, err
	}

	currentWorld, err := u.repo.GetWorld(ctx, worldId)
	return currentWorld, err
}

func (u *DontStarveClusterUseCase) CreateMod(ctx context.Context, clusterId string, modId string) (entity.DontStarveModInCluster, error) {
	mod, err := u.modRepo.GetMod(ctx, modId)
	if err != nil {
		return entity.DontStarveModInCluster{}, err
	}

	modInCluster := entity.DontStarveModInCluster{
		Model:               entity.Model{},
		CurrentConfig:       mod.Config,
		DontStarveClusterId: clusterId,
		ModId:               modId,
	}

	err = u.repo.CreateMods(ctx, clusterId, &modInCluster)
	if err != nil {
		return entity.DontStarveModInCluster{}, err
	}

	cluster, err := u.repo.GetCluster(ctx, clusterId)
	if err != nil {
		return entity.DontStarveModInCluster{}, err
	}

	err = u.driver.CreateMod(ctx, cluster)
	if err != nil {
		return entity.DontStarveModInCluster{}, err
	}

	return modInCluster, nil
}

func (u *DontStarveClusterUseCase) DeleteMod(ctx context.Context, clusterId, modId string) error {
	err := u.repo.DeleteMods(ctx, modId)
	if err != nil {
		return err
	}

	cluster, err := u.repo.GetCluster(ctx, clusterId)
	if err != nil {
		return err
	}

	err = u.driver.DeleteMod(ctx, cluster)
	if err != nil {
		return err
	}

	return nil
}

func (u *DontStarveClusterUseCase) UpdateMod(ctx context.Context, clusterId, modId string, mod entity.DontStarveModInCluster) (entity.DontStarveModInCluster, error) {
	err := u.repo.UpdateMod(ctx, modId, mod)
	if err != nil {
		return entity.DontStarveModInCluster{}, err
	}

	cluster, err := u.repo.GetCluster(ctx, clusterId)
	if err != nil {
		return entity.DontStarveModInCluster{}, err
	}

	err = u.driver.UpdateMod(ctx, cluster)
	if err != nil {
		return entity.DontStarveModInCluster{}, err
	}

	currentMod, err := u.repo.GetMod(ctx, modId)
	return currentMod, err
}
