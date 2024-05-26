package usecase

import "context"

type DontStarveControlUseCase struct {
	driver      DontStarveControlDriver
	clusterRepo DontStarveClusterRepo
	configRepo  DontStarveConfigRepo
}

func NewDontStarveControlUseCase(driver DontStarveControlDriver, clusterRepo DontStarveClusterRepo, configRepo DontStarveConfigRepo) *DontStarveControlUseCase {
	return &DontStarveControlUseCase{driver: driver, clusterRepo: clusterRepo, configRepo: configRepo}
}

func (d *DontStarveControlUseCase) Start(ctx context.Context, clusterId string) error {
	cluster, err := d.clusterRepo.GetCluster(ctx, clusterId)
	if err != nil {
		return err
	}

	admins, err := d.configRepo.GetAdmins(ctx)
	if err != nil {
		return err
	}

	token, err := d.configRepo.GetClusterToken(ctx)
	if err != nil {
		return err
	}

	return d.driver.Start(ctx, cluster, admins, token)
}

func (d *DontStarveControlUseCase) Stop(ctx context.Context) error {
	return d.Stop(ctx)
}

func (d *DontStarveControlUseCase) Restart(ctx context.Context, clusterId string) error {
	cluster, err := d.clusterRepo.GetCluster(ctx, clusterId)
	if err != nil {
		return err
	}

	admins, err := d.configRepo.GetAdmins(ctx)
	if err != nil {
		return err
	}

	token, err := d.configRepo.GetClusterToken(ctx)
	if err != nil {
		return err
	}

	return d.driver.Restart(ctx, cluster, admins, token)
}

func (d *DontStarveControlUseCase) Update(ctx context.Context) error {
	return d.Update(ctx)
}

func (d *DontStarveControlUseCase) Install(ctx context.Context) error {
	return d.Install(ctx)
}
