package driver

import (
	"context"
	"dst-run/internal/usecase/driver/donstarve"
	"fmt"
)

type DontStarveConsoleDriver struct {
	dst *donstarve.Dst
}

func NewDontStarveConsoleDriver(dst *donstarve.Dst) *DontStarveConsoleDriver {
	return &DontStarveConsoleDriver{dst: dst}
}

func (d *DontStarveConsoleDriver) GetPlayers(ctx context.Context) ([]string, error) {
	var players []string
	for _, p := range d.dst.Processes {
		out, err := d.dst.RunCmd(p, "c_listallplayers()")
		if err != nil {
			return nil, err
		}
		players = append(players, out)
	}
	return players, nil
}

func (d *DontStarveConsoleDriver) Announce(ctx context.Context, msg string) error {
	cmd := fmt.Sprintf("c_announce(\"%s\")", msg)
	_, err := d.dst.RunCmd(d.dst.Processes["Master"], cmd)
	return err
}

func (d *DontStarveConsoleDriver) Regenerate(ctx context.Context) error {
	_, err := d.dst.RunCmd(d.dst.Processes["Master"], "c_regenerateworld()")
	return err
}

func (d *DontStarveConsoleDriver) Rollback(ctx context.Context, days int) error {
	cmd := fmt.Sprintf("c_rollback(%d)", days)
	_, err := d.dst.RunCmd(d.dst.Processes["Master"], cmd)
	return err
}
