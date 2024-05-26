package usecase

import (
	"context"
	"dst-run/internal/entity"
)

type (
	DontStarveCluster interface {
		GetClusters(ctx context.Context) ([]entity.DontStarveCluster, error)
		GetCluster(ctx context.Context, id string) (entity.DontStarveCluster, error)
		CreateCluster(ctx context.Context) (entity.DontStarveCluster, error)
		DeleteCluster(ctx context.Context, id string) error
		UpdateCluster(ctx context.Context, id string, cluster entity.DontStarveCluster) (entity.DontStarveCluster, error)

		CreateWorld(ctx context.Context, clusterId, worldType string) (entity.DontStarveWorld, error)
		DeleteWorld(ctx context.Context, clusterId, worldId string) error
		UpdateWorld(ctx context.Context, clusterId, worldId string, world entity.DontStarveWorld) (entity.DontStarveWorld, error)

		CreateMod(ctx context.Context, clusterId string, modId string) (entity.DontStarveModInCluster, error)
		DeleteMod(ctx context.Context, clusterId, modId string) error
		UpdateMod(ctx context.Context, clusterId, modId string, mod entity.DontStarveModInCluster) (entity.DontStarveModInCluster, error)
	}

	DontStarveClusterRepo interface {
		GetClusters(ctx context.Context) ([]entity.DontStarveCluster, error)
		GetCluster(ctx context.Context, id string) (entity.DontStarveCluster, error)
		CreateClusters(ctx context.Context, clusters ...*entity.DontStarveCluster) error
		DeleteClusters(ctx context.Context, ids ...string) error
		UpdateCluster(ctx context.Context, id string, cluster entity.DontStarveCluster) error

		GetWorld(ctx context.Context, id string) (entity.DontStarveWorld, error)
		CreateWorlds(ctx context.Context, clusterId string, worlds ...*entity.DontStarveWorld) error
		DeleteWorlds(ctx context.Context, ids ...string) error
		UpdateWorld(ctx context.Context, id string, world entity.DontStarveWorld) error

		GetMod(ctx context.Context, id string) (entity.DontStarveModInCluster, error)
		CreateMods(ctx context.Context, clusterId string, mods ...*entity.DontStarveModInCluster) error
		DeleteMods(ctx context.Context, ids ...string) error
		UpdateMod(ctx context.Context, id string, mod entity.DontStarveModInCluster) error
	}

	DontStarveClusterDriver interface {
		CreateCluster(ctx context.Context, cluster entity.DontStarveCluster) error
		DeleteCluster(ctx context.Context, id string) error
		UpdateCluster(ctx context.Context, cluster entity.DontStarveCluster) error

		CreateWorld(ctx context.Context, cluster entity.DontStarveCluster) error
		DeleteWorld(ctx context.Context, clusterId string, worldType string) error
		UpdateWorld(ctx context.Context, cluster entity.DontStarveCluster) error

		CreateMod(ctx context.Context, cluster entity.DontStarveCluster) error
		DeleteMod(ctx context.Context, cluster entity.DontStarveCluster) error
		UpdateMod(ctx context.Context, cluster entity.DontStarveCluster) error
	}
)

type (
	DontStarveConfig interface {
		GetConfig(ctx context.Context) (entity.DontStarveConfig, error)
		UpdateConfig(ctx context.Context, config entity.DontStarveConfig) (entity.DontStarveConfig, error)

		GetAdmins(ctx context.Context) ([]entity.DontStarveAdmin, error)
		CreateAdmin(ctx context.Context, admin entity.DontStarveAdmin) (entity.DontStarveAdmin, error)
		DeleteAdmin(ctx context.Context, id string) error
		UpdateAdmin(ctx context.Context, id string, admin entity.DontStarveAdmin) (entity.DontStarveAdmin, error)
	}

	DontStarveConfigRepo interface {
		GetClusterToken(ctx context.Context) (string, error)
		SetClusterToken(ctx context.Context, token string) error

		GetAdmin(ctx context.Context, id string) (entity.DontStarveAdmin, error)
		GetAdmins(ctx context.Context) ([]entity.DontStarveAdmin, error)
		CreateAdmin(ctx context.Context, admins ...*entity.DontStarveAdmin) error
		DeleteAdmin(ctx context.Context, id string) error
		UpdateAdmin(ctx context.Context, id string, admin entity.DontStarveAdmin) error
	}
)

type (
	DontStarveConsole interface {
		DontStarveConsoleDriver
	}

	DontStarveConsoleDriver interface {
		GetPlayers(context.Context) ([]string, error)
		Announce(context.Context, string) error
		Regenerate(context.Context) error
		Rollback(context.Context, int) error
	}
)

type (
	DontStarveControl interface {
		Start(ctx context.Context, clusterId string) error
		Stop(ctx context.Context) error
		Restart(ctx context.Context, clusterId string) error
		Update(ctx context.Context) error
		Install(ctx context.Context) error
	}

	DontStarveControlDriver interface {
		Start(ctx context.Context, cluster entity.DontStarveCluster, admins []entity.DontStarveAdmin, token string) error
		Stop(ctx context.Context) error
		Restart(ctx context.Context, cluster entity.DontStarveCluster, admins []entity.DontStarveAdmin, token string) error
		Update(ctx context.Context) error
		Install(ctx context.Context) error
	}
)

type (
	DontStarveEvent interface {
		DontStarveEventRepo
	}

	DontStarveEventRepo interface {
		GetEvents(ctx context.Context) ([]entity.DontStarveEvent, error)
		CreateAdmin(ctx context.Context, events ...*entity.DontStarveEvent) error
	}
)

type (
	DontStarveMod interface {
		DontStarveModRepo
		DontStarveModApi
	}

	DontStarveModRepo interface {
		GetMod(ctx context.Context, id string) (entity.DontStarveMod, error)
		GetMods(context.Context) ([]entity.DontStarveMod, error)
		GetModsByModIds(context.Context, []string) ([]entity.DontStarveMod, error)
		CreateMods(context.Context, []entity.DontStarveMod) error
		DeleteModsByModIds(context.Context, []string) error
		UpdateMods(context.Context, []entity.DontStarveMod) error
	}

	DontStarveModApi interface {
		FetchModsName(context.Context, []entity.DontStarveMod) []entity.DontStarveMod
	}
)

type (
	DontStarveStatus interface {
		DontStarveStatusDriver
	}

	DontStarveStatusDriver interface {
		GetStatus(context.Context) (entity.DontStarveStatus, error)
	}
)

type (
	TModLoaderCluster interface {
		GetClusters(ctx context.Context) ([]entity.TModLoaderCluster, error)
		GetCluster(ctx context.Context, id string) (entity.TModLoaderCluster, error)
		CreateCluster(ctx context.Context) (entity.TModLoaderCluster, error)
		DeleteCluster(ctx context.Context, id string) error
		UpdateCluster(ctx context.Context, id string, cluster entity.TModLoaderCluster) (entity.TModLoaderCluster, error)

		CreateMod(ctx context.Context, clusterId string, modId string) (entity.TModLoaderModInCluster, error)
		DeleteMod(ctx context.Context, clusterId, modId string) error
		UpdateMod(ctx context.Context, clusterId, modId string, mod entity.TModLoaderModInCluster) (entity.TModLoaderModInCluster, error)
	}

	TModLoaderClusterRepo interface {
		GetClusters(ctx context.Context) ([]entity.TModLoaderCluster, error)
		GetCluster(ctx context.Context, id string) (entity.TModLoaderCluster, error)
		CreateClusters(ctx context.Context, clusters ...*entity.TModLoaderCluster) error
		DeleteClusters(ctx context.Context, ids ...string) error
		UpdateCluster(ctx context.Context, id string, cluster entity.TModLoaderCluster) error

		GetMod(ctx context.Context, id string) (entity.TModLoaderModInCluster, error)
		CreateMods(ctx context.Context, clusterId string, mods ...*entity.TModLoaderModInCluster) error
		DeleteMods(ctx context.Context, ids ...string) error
		UpdateMod(ctx context.Context, id string, mod entity.TModLoaderModInCluster) error
	}

	TModLoaderClusterDriver interface {
		CreateCluster(ctx context.Context, cluster entity.TModLoaderCluster) error
		DeleteCluster(ctx context.Context, id string) error
		UpdateCluster(ctx context.Context, cluster entity.TModLoaderCluster) error

		CreateWorld(ctx context.Context, cluster entity.TModLoaderCluster) error
		DeleteWorld(ctx context.Context, clusterId string, worldType string) error
		UpdateWorld(ctx context.Context, cluster entity.TModLoaderCluster) error

		CreateMod(ctx context.Context, cluster entity.TModLoaderCluster) error
		DeleteMod(ctx context.Context, cluster entity.TModLoaderCluster) error
		UpdateMod(ctx context.Context, cluster entity.TModLoaderCluster) error
	}
)

type (
	TModLoaderConsole interface {
		TModLoaderConsoleDriver
	}

	TModLoaderConsoleDriver interface {
		GetPlayers(context.Context) ([]string, error)
		Announce(context.Context, string) error
		Regenerate(context.Context) error
		Rollback(context.Context, int) error
	}
)

type (
	TModLoaderControl interface {
		Start(ctx context.Context, clusterId string) error
		Stop(ctx context.Context) error
		Restart(ctx context.Context, clusterId string) error
		Update(ctx context.Context) error
		Install(ctx context.Context) error
	}

	TModLoaderControlDriver interface {
		Start(ctx context.Context, cluster entity.TModLoaderCluster) error
		Stop(ctx context.Context) error
		Restart(ctx context.Context, cluster entity.TModLoaderCluster) error
		Update(ctx context.Context) error
		Install(ctx context.Context) error
	}
)

type (
	TModLoaderStatus interface {
		TModLoaderStatusDriver
	}

	TModLoaderStatusDriver interface {
		GetStatus(context.Context) (entity.TModLoaderStatus, error)
	}
)

type (
	TModLoaderMod interface {
		TModLoaderModRepo
		TModLoaderModApi
	}

	TModLoaderModRepo interface {
		GetMod(ctx context.Context, id string) (entity.TModLoaderMod, error)
		GetMods(context.Context) ([]entity.TModLoaderMod, error)
		GetModsByModIds(context.Context, []string) ([]entity.TModLoaderMod, error)
		CreateMods(context.Context, []entity.TModLoaderMod) error
		DeleteModsByModIds(context.Context, []string) error
		UpdateMods(context.Context, []entity.TModLoaderMod) error
	}

	TModLoaderModApi interface {
		FetchModsName(context.Context, []entity.TModLoaderMod) []entity.TModLoaderMod
	}
)
