package driver

import (
	"context"
	"dst-run/assets"
	"dst-run/internal/entity"
	"dst-run/internal/usecase/driver/donstarve"
	"dst-run/pkg/util"
	_ "embed"
	"gopkg.in/ini.v1"
	"strings"
)

const iconEye = "󰀅"

type DontStarveClusterDriver struct {
}

func NewDontStarveClusterDriver() *DontStarveClusterDriver {
	return &DontStarveClusterDriver{}
}

func (d *DontStarveClusterDriver) DeployCluster(ctx context.Context, cluster entity.DontStarveCluster) error {
	cp := donstarve.NewClusterPath(cluster.Id)

	err := util.MkDir(cp.Root)
	if err != nil {
		return err
	}

	err = d.deployClusterIni(ctx, cluster)
	if err != nil {
		return err
	}

	for _, world := range cluster.Worlds {
		err = d.deployWorld(ctx, cluster, world)
		if err != nil {
			return err
		}
	}

	return nil
}

func (d *DontStarveClusterDriver) deployClusterIni(ctx context.Context, cluster entity.DontStarveCluster) error {
	cp := donstarve.NewClusterPath(cluster.Id)

	cfg, err := ini.Load([]byte(assets.DontStarveClusterIni))
	if err != nil {
		return err
	}

	cfg.Section("NETWORK").Key("cluster_name").
		SetValue(iconEye + cluster.ClusterName + iconEye)
	cfg.Section("NETWORK").Key("cluster_password").
		SetValue(cluster.ClusterPassword)
	cfg.Section("NETWORK").Key("cluster_description").
		SetValue(cluster.ClusterDescription)

	cfg.Section("GAMEPLAY").Key("max_players").SetValue(cluster.MaxPlayers)
	cfg.Section("GAMEPLAY").Key("Pvp").SetValue(cluster.Pvp)

	return cfg.SaveTo(cp.ClusterIni)
}

func (d *DontStarveClusterDriver) deployWorld(ctx context.Context, cluster entity.DontStarveCluster,
	world entity.DontStarveWorld) error {

	cp := donstarve.NewClusterPath(cluster.Id)
	sp, err := cp.GetShardPath(world.Type)
	if err != nil {
		return err
	}

	err = util.MkDir(sp.Root)
	if err != nil {
		return err
	}

	err = util.WriteFile(sp.ServerFile, []byte(world.ServerConfig))
	if err != nil {
		return err
	}

	err = util.WriteFile(sp.WorldOverrideFile, []byte(world.WorldOverride))
	if err != nil {
		return err
	}

	content := d.genModOverrideContent(cluster.Mods)
	err = util.WriteFile(sp.ModOverrideFile, []byte(content))
	if err != nil {
		return err
	}

	return nil
}

func (d *DontStarveClusterDriver) CreateCluster(ctx context.Context, cluster entity.DontStarveCluster) error {
	return d.DeployCluster(ctx, cluster)
}

func (d *DontStarveClusterDriver) DeleteCluster(ctx context.Context, id string) error {
	cp := donstarve.NewClusterPath(id)
	return util.RmvPath(cp.Root)
}

func (d *DontStarveClusterDriver) UpdateCluster(ctx context.Context, cluster entity.DontStarveCluster) error {
	return d.DeployCluster(ctx, cluster)
}

func (d *DontStarveClusterDriver) CreateWorld(ctx context.Context, cluster entity.DontStarveCluster) error {
	return d.DeployCluster(ctx, cluster)
}

func (d *DontStarveClusterDriver) DeleteWorld(ctx context.Context, clusterId string, worldType string) error {
	cp := donstarve.NewClusterPath(clusterId)
	shard, err := cp.GetShardPath(worldType)
	if err != nil {
		return err
	}

	err = util.RmvPath(shard.Root)
	if err != nil {
		return err
	}

	return nil
}

func (d *DontStarveClusterDriver) UpdateWorld(ctx context.Context, cluster entity.DontStarveCluster) error {
	return d.DeployCluster(ctx, cluster)
}

func (d *DontStarveClusterDriver) CreateMod(ctx context.Context, cluster entity.DontStarveCluster) error {
	return d.DeployCluster(ctx, cluster)
}

func (d *DontStarveClusterDriver) DeleteMod(ctx context.Context, cluster entity.DontStarveCluster) error {
	return d.DeployCluster(ctx, cluster)
}

func (d *DontStarveClusterDriver) UpdateMod(ctx context.Context, cluster entity.DontStarveCluster) error {
	return d.DeployCluster(ctx, cluster)
}

func (d *DontStarveClusterDriver) genModOverrideContent(mods []entity.DontStarveModInCluster) string {
	var enableModConfigs []string
	for _, m := range mods {
		enableModConfigs = append(enableModConfigs, m.CurrentConfig)
	}

	content := "return {" + strings.Join(enableModConfigs, ",") + "}"
	return content
}
