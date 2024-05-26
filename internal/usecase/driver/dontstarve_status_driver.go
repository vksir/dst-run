package driver

import (
	"context"
	"dst-run/internal/entity"
	"dst-run/internal/usecase/driver/donstarve"
)

type DontStarveStatusDriver struct {
	dst *donstarve.Dst
}

func NewDontStarveStatusDriver(dst *donstarve.Dst) *DontStarveStatusDriver {
	return &DontStarveStatusDriver{dst: dst}
}

func (d *DontStarveStatusDriver) GetStatus(ctx context.Context) (entity.DontStarveStatus, error) {
	var status entity.DontStarveStatus
	status.StatusString = d.dst.Status()
	return status, nil
}
