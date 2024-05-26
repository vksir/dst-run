package repo

import (
	"context"
	"dst-run/internal/entity"
	"gorm.io/gorm"
)

type DontStarveEventRepo struct {
	eventRepo *Repo[entity.DontStarveEvent]
}

func NewDontStarveEventRepo(db *gorm.DB) *DontStarveEventRepo {
	return &DontStarveEventRepo{eventRepo: NewRepo[entity.DontStarveEvent](db)}
}

func (r *DontStarveEventRepo) GetEvents(ctx context.Context) ([]entity.DontStarveEvent, error) {
	return r.eventRepo.GetAll(ctx)
}

func (r *DontStarveEventRepo) CreateAdmin(ctx context.Context, events ...*entity.DontStarveEvent) error {
	return r.eventRepo.Creates(ctx, events...)
}
