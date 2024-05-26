package usecase

import (
	"context"
	"dst-run/internal/entity"
	"dst-run/pkg/log"
)

type DontStarveConfigUseCase struct {
	repo DontStarveConfigRepo
	l    log.Interface
}

func NewDontStarveConfigUseCase(repo DontStarveConfigRepo, l log.Interface) *DontStarveConfigUseCase {
	return &DontStarveConfigUseCase{repo, l}
}

func (d *DontStarveConfigUseCase) GetConfig(ctx context.Context) (entity.DontStarveConfig, error) {
	token, err := d.repo.GetClusterToken(ctx)
	if err != nil {
		return entity.DontStarveConfig{}, err
	}

	config := entity.DontStarveConfig{
		ClusterToken: token,
	}
	return config, nil
}

func (d *DontStarveConfigUseCase) UpdateConfig(ctx context.Context, config entity.DontStarveConfig) (entity.DontStarveConfig, error) {
	err := d.repo.SetClusterToken(ctx, config.ClusterToken)
	if err != nil {
		return entity.DontStarveConfig{}, err
	}

	return d.GetConfig(ctx)
}

func (d *DontStarveConfigUseCase) GetAdmins(ctx context.Context) ([]entity.DontStarveAdmin, error) {
	return d.repo.GetAdmins(ctx)
}

func (d *DontStarveConfigUseCase) CreateAdmin(ctx context.Context, admin entity.DontStarveAdmin) (entity.DontStarveAdmin, error) {
	err := d.repo.CreateAdmin(ctx, &admin)
	if err != nil {
		return entity.DontStarveAdmin{}, err
	}

	return admin, nil
}

func (d *DontStarveConfigUseCase) DeleteAdmin(ctx context.Context, id string) error {
	return d.repo.DeleteAdmin(ctx, id)
}

func (d *DontStarveConfigUseCase) UpdateAdmin(ctx context.Context, id string, admin entity.DontStarveAdmin) (entity.DontStarveAdmin, error) {
	err := d.repo.UpdateAdmin(ctx, id, admin)
	if err != nil {
		return entity.DontStarveAdmin{}, err
	}

	currentAdmin, err := d.repo.GetAdmin(ctx, id)
	if err != nil {
		return entity.DontStarveAdmin{}, err
	}

	return currentAdmin, nil
}
