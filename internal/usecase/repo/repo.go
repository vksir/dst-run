package repo

import (
	"context"
	"dst-run/internal/entity"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
	"reflect"
)

type Repo[T entity.Constraint] struct {
	Db *gorm.DB
}

func NewRepo[T entity.Constraint](db *gorm.DB) *Repo[T] {
	return &Repo[T]{Db: db}
}

// Get 查询多个数据，预加载所有关联表
func (r *Repo[T]) Get(ctx context.Context, us []string) ([]T, error) {
	if len(us) == 0 {
		return []T{}, nil
	}

	var ts []T
	res := r.Db.WithContext(ctx).Preload(clause.Associations).
		Where("id IN ?", us).Find(&ts)
	return ts, res.Error
}

// GetOne 查询单个数据，预加载所有关联表
func (r *Repo[T]) GetOne(ctx context.Context, id string) (T, error) {
	var t T
	res := r.Db.WithContext(ctx).Preload(clause.Associations).
		Where("id = ?", id).Take(&t)
	return t, res.Error
}

// GetAll 查询所有数据，预加载所有关联表
func (r *Repo[T]) GetAll(ctx context.Context) ([]T, error) {
	var ts []T
	res := r.Db.WithContext(ctx).Preload(clause.Associations).
		Find(&ts)
	return ts, res.Error
}

// Creates 创建完后，ts 中会携带最新数据
func (r *Repo[T]) Creates(ctx context.Context, ts ...*T) error {
	if len(ts) == 0 {
		return nil
	}
	res := r.Db.WithContext(ctx).Create(&ts)
	return res.Error
}

// Deletes 删除多个数据，删除所有关联关系，并且删除所有关联数据
func (r *Repo[T]) Deletes(ctx context.Context, ids ...string) error {
	if len(ids) == 0 {
		return nil
	}
	var t T
	res := r.Db.WithContext(ctx).Select(clause.Associations).Unscoped().
		Where("id IN ?", ids).Delete(&t)
	return res.Error
}

// Update 全量更新所有值（包括零值），更新完后，t 中数据保持不变
// 注意：当 T 中存在关联项时，更新会创建新的关联项，而不是替换它们
func (r *Repo[T]) Update(ctx context.Context, id string, t T) error {
	v := reflect.ValueOf(&t).Elem()
	v.FieldByName("Id").SetString(id)
	res := r.Db.WithContext(ctx).Select("*").Updates(v.Addr().Interface())
	return res.Error
}
