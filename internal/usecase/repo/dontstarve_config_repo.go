package repo

import (
	"context"
	"dst-run/internal/entity"
	"gorm.io/gorm"
)

type DontStarveConfigRepo struct {
	*gorm.DB
	adminRepo *Repo[entity.DontStarveAdmin]
}

func NewDontStarveConfigRepo(db *gorm.DB) *DontStarveConfigRepo {
	return &DontStarveConfigRepo{
		DB:        db,
		adminRepo: NewRepo[entity.DontStarveAdmin](db),
	}
}

func (r *DontStarveConfigRepo) getValue(ctx context.Context, key string) (string, error) {
	var kv entity.DontStarveKv
	kv.Key = key
	res := r.WithContext(ctx).Take(&kv)
	if res.Error != nil {
		return "", res.Error
	}
	return kv.Value, nil
}

func (r *DontStarveConfigRepo) setValue(ctx context.Context, key string, value string) error {
	var kv entity.DontStarveKv
	kv.Key = key
	kv.Value = value
	res := r.WithContext(ctx).Create(&kv)
	if res.Error != nil {
		return res.Error
	}
	return nil
}

func (r *DontStarveConfigRepo) GetClusterToken(ctx context.Context) (string, error) {
	return r.getValue(ctx, "cluster_token")
}

func (r *DontStarveConfigRepo) SetClusterToken(ctx context.Context, token string) error {
	return r.setValue(ctx, "cluster_token", token)
}

func (r *DontStarveConfigRepo) GetAdmin(ctx context.Context, id string) (entity.DontStarveAdmin, error) {
	return r.adminRepo.GetOne(ctx, id)
}

func (r *DontStarveConfigRepo) GetAdmins(ctx context.Context) ([]entity.DontStarveAdmin, error) {
	return r.adminRepo.GetAll(ctx)
}

func (r *DontStarveConfigRepo) CreateAdmin(ctx context.Context, admins ...*entity.DontStarveAdmin) error {
	return r.adminRepo.Creates(ctx, admins...)
}

func (r *DontStarveConfigRepo) DeleteAdmin(ctx context.Context, id string) error {
	return r.adminRepo.Deletes(ctx, id)
}

func (r *DontStarveConfigRepo) UpdateAdmin(ctx context.Context, id string, admin entity.DontStarveAdmin) error {
	return r.adminRepo.Update(ctx, id, admin)
}
