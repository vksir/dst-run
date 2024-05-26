package driver

import (
	"context"
	"dst-run/internal/entity"
	"dst-run/internal/usecase/driver/donstarve"
	"dst-run/pkg/log"
	"dst-run/pkg/util"
	"fmt"
	"strings"
)

type DontStarveControlDriver struct {
	dst *donstarve.Dst
	l   log.Interface
}

func NewDontStarveControlDriver(dst *donstarve.Dst, l log.Interface) *DontStarveControlDriver {
	return &DontStarveControlDriver{l: l, dst: dst}
}

func (d *DontStarveControlDriver) Start(ctx context.Context, cluster entity.DontStarveCluster,
	admins []entity.DontStarveAdmin, token string) error {

	err := d.deploy(ctx, cluster, admins, token)
	if err != nil {
		return err
	}

	return d.dst.Start(ctx, cluster)
}

func (d *DontStarveControlDriver) Stop(ctx context.Context) error {
	return d.dst.Stop(ctx)
}

func (d *DontStarveControlDriver) Restart(ctx context.Context, cluster entity.DontStarveCluster,
	admins []entity.DontStarveAdmin, token string) error {

	err := d.deploy(ctx, cluster, admins, token)
	if err != nil {
		return err
	}

	return d.dst.Restart(ctx, cluster)
}

func (d *DontStarveControlDriver) Update(ctx context.Context) error {
	return d.dst.Update(ctx)
}

func (d *DontStarveControlDriver) Install(ctx context.Context) error {
	return d.dst.Install(ctx)
}

func (d *DontStarveControlDriver) deploy(ctx context.Context, cluster entity.DontStarveCluster,
	admins []entity.DontStarveAdmin, token string) error {

	err := d.deployModSetup(ctx, cluster.Mods)
	if err != nil {
		return err
	}

	err = d.deployAdminList(ctx, cluster.Id, admins)
	if err != nil {
		return err
	}

	err = d.deployClusterToken(ctx, cluster.Id, token)
	if err != nil {
		return err
	}

	return nil
}

func (d *DontStarveControlDriver) deployAdminList(ctx context.Context, clusterId string, admins []entity.DontStarveAdmin) error {
	cp := donstarve.NewClusterPath(clusterId)

	var contentLines []string
	for _, admin := range admins {
		contentLines = append(contentLines, admin.KleiId)
	}

	content := strings.Join(contentLines, "\n")
	return util.WriteFile(cp.AdminListFile, []byte(content))
}

func (d *DontStarveControlDriver) deployClusterToken(ctx context.Context, clusterId, token string) error {
	cp := donstarve.NewClusterPath(clusterId)
	return util.WriteFile(cp.TokenFile, []byte(token))
}

func (d *DontStarveControlDriver) deployModSetup(ctx context.Context, mods []entity.DontStarveModInCluster) error {
	content := d.genModSetupContent(mods)

	err := util.WriteFile(donstarve.ModSetupPath, []byte(content))
	if err != nil {
		return err
	}

	return nil
}

func (d *DontStarveControlDriver) genModSetupContent(mods []entity.DontStarveModInCluster) string {
	var enableModSetupConfigs []string
	for _, mod := range mods {
		enableModSetupConfigs = append(enableModSetupConfigs,
			fmt.Sprintf("ServerModSetup(\"%s\")", mod.ModId))
	}
	content := strings.Join(enableModSetupConfigs, "\n")
	return content
}
