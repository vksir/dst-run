package donstarve

import (
	"context"
	"dst-run/internal/entity"
	"dst-run/pkg/log"
	"dst-run/pkg/process"
	"dst-run/pkg/registry"
	"errors"
	"fmt"
	"github.com/spf13/viper"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

var R = process.NewReport("DST", getReportPatterns())

type Dst struct {
	Processes map[string]*process.Process
	l         log.Interface
}

func NewDst(l log.Interface) *Dst {
	return &Dst{
		l: l.WithTag("DST"),
	}
}

func (d *Dst) Name() string {
	return "DST"
}

func (d *Dst) Status() string {
	// TODO
	return ""
}

func (d *Dst) Start(ctx context.Context, cluster entity.DontStarveCluster) error {
	d.Processes = make(map[string]*process.Process)

	for _, shard := range []string{"Master", "Caves"} {
		args := []string{"-console", "-cluster", cluster.Id, "-shard", shard}
		p := process.NewProcess(shard, dstServPath, args, d.l)
		p.Cmd.Dir = filepath.Join(programDir, "bin64")

		l := d.l.WithTag(shard)
		p.RegisterOutFunc(shard, func(line *string) {
			l.Debug(*line)
			registry.Notify(p.Ctx, shard+":Log", line)
		})

		if err := p.Start(); err != nil {
			return err
		}

		d.Processes[shard] = p
	}
	return nil
}

func (d *Dst) Stop(ctx context.Context) error {
	d.l.InfoC(ctx, "begin stop process")
	for _, p := range d.Processes {
		if err := p.Cmd.Process.Signal(os.Interrupt); err != nil {
			log.Error("[%s] process signal interrupt failed: %s", p.Name(), err)
		}
	}

	ctx, cancel := context.WithTimeout(ctx, time.Second*15)
	defer cancel()

	for _, p := range d.Processes {
		select {
		case <-p.Ctx.Done():
		case <-ctx.Done():
		}
	}

	if err := ctx.Err(); errors.Is(err, context.DeadlineExceeded) {
		d.l.InfoC(ctx, "stop process timeout, begin kill")
		for _, p := range d.Processes {
			if err := p.Cmd.Process.Signal(os.Kill); err != nil {
				d.l.ErrorC(ctx, "process kill failed: %s", err)
				return err
			}
		}
	}

	registry.Notify(ctx, d.Name()+"Event", EventServerStopped)

	d.Processes = make(map[string]*process.Process)
	return nil
}

func (d *Dst) Restart(ctx context.Context, cluster entity.DontStarveCluster) error {
	err := d.Stop(ctx)
	if err != nil {
		return err
	}
	return d.Start(ctx, cluster)
}

func (d *Dst) Install(ctx context.Context) error {
	registry.Notify(ctx, d.Name()+"Event", EventServerInstalling)
	return d.installOrUpdate(ctx)
}

func (d *Dst) Update(ctx context.Context) error {
	registry.Notify(ctx, d.Name()+"Event", EventServerUpdating)
	return d.installOrUpdate(ctx)
}

func (d *Dst) installOrUpdate(ctx context.Context) error {
	exe := viper.GetString("ns.steamcmd")
	args := []string{"+force_install_dir", programDir,
		"+login", "anonymous",
		"+app_update", "343050", "validate",
		"+quit"}

	p := process.NewProcess("Steam", exe, args, d.l)

	l := d.l.WithTag("Steam:Dst")
	p.RegisterOutFunc("log", func(line *string) {
		l.Debug(*line)
	})

	if err := p.Start(); err != nil {
		return err
	}

	select {
	case <-p.Ctx.Done():
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func (d *Dst) RunCmd(p *process.Process, cmd string) (string, error) {
	var out string
	p.RegisterOutFunc("run_cmd", func(line *string) {
		out += *line
	})

	cmd = strings.TrimRight(cmd, "\n")
	if _, err := p.Stdin.Write([]byte(fmt.Sprintf("[BEGIN_CMD]\n%s\n[END_CMD]\n", cmd))); err != nil {
		p.UnregisterOutFunc("run_cmd")
		return "", err
	}
	time.Sleep(500 * time.Millisecond)
	p.UnregisterOutFunc("run_cmd")

	pattern := regexp.MustCompile(`(?ms)BEGIN_CMD(.*?)END_CMD`)
	res := pattern.FindStringSubmatch(out)
	if len(res) == 0 {
		return "", fmt.Errorf("regex cmd out failed: %s", out)
	}
	log.Info("run cmd %s success: %s", cmd, res[1])
	return res[1], nil
}
