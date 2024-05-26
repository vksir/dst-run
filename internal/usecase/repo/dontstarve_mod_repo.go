package repo

import (
	"context"
	"dst-run/internal/entity"
	"gorm.io/gorm"
)

type DontStarveModRepo struct {
	*gorm.DB
}

func NewDontStarveModRepo(db *gorm.DB) *DontStarveModRepo {
	return &DontStarveModRepo{db}
}

func (r *DontStarveModRepo) GetMod(ctx context.Context, id string) (entity.DontStarveMod, error) {
	var e entity.DontStarveMod
	e.Id = id
	res := r.WithContext(ctx).Take(&e)
	return e, res.Error
}

func (r *DontStarveModRepo) GetMods(ctx context.Context) ([]entity.DontStarveMod, error) {
	var entities []entity.DontStarveMod
	res := r.WithContext(ctx).Find(&entities)
	return entities, res.Error
}

func (r *DontStarveModRepo) GetModsByModIds(ctx context.Context, modIds []string) ([]entity.DontStarveMod, error) {
	if len(modIds) == 0 {
		return []entity.DontStarveMod{}, nil
	}

	var mods []entity.DontStarveMod
	res := r.WithContext(ctx).
		Where("mod_id IN ?", modIds).Find(&mods)
	return mods, res.Error
}

func (r *DontStarveModRepo) CreateMods(ctx context.Context, mods []entity.DontStarveMod) error {
	res := r.WithContext(ctx).Create(&mods)
	return res.Error
}

func (r *DontStarveModRepo) DeleteModsByModIds(ctx context.Context, modIds []string) error {
	if len(modIds) == 0 {
		return nil
	}

	res := r.WithContext(ctx).
		Where("mod_id IN ?", modIds).Delete(&entity.DontStarveMod{})
	return res.Error
}

func (r *DontStarveModRepo) UpdateMods(ctx context.Context, mods []entity.DontStarveMod) error {
	res := r.WithContext(ctx).Updates(&mods)
	return res.Error
}
