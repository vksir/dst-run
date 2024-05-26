package entity

import (
	"github.com/google/uuid"
	"gorm.io/gorm"
	"time"
)

type Constraint interface {
	DontStarveCluster | DontStarveWorld |
		DontStarveMod | DontStarveModInCluster |
		DontStarveAdmin | DontStarveEvent
}

type Model struct {
	Id        string `gorm:"primarykey;size:36"`
	CreatedAt time.Time
	UpdatedAt time.Time
}

func (u *Model) BeforeCreate(tx *gorm.DB) error {
	if u.Id == "" {
		u.Id = uuid.New().String()
	}
	return nil
}
