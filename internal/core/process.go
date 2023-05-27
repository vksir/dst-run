package core

import (
	"bufio"
	"context"
	"dst-run/internal/comm"
	"io"
	"os"
	"os/exec"
	"strings"
	"time"
)

var log = comm.SugaredLogger()

type Process struct {
	Name string

	Cmd    *exec.Cmd
	Stdin  io.Writer
	Stdout io.Reader
	Stderr io.Reader

	Ctx  context.Context
	stop context.CancelFunc

	handlers []Handler
}

func NewProcess(name string, cmd *exec.Cmd) *Process {
	return &Process{Name: name, Cmd: cmd}
}

func (p *Process) Active() bool {
	if p.Ctx == nil {
		return false
	}
	select {
	case <-p.Ctx.Done():
		return false
	default:
		return true
	}
}

func (p *Process) Start() error {
	log.Infof("start process: %s, %s", p.Name, strings.Join(p.Cmd.Args, " "))

	var err error
	if p.Stdin, err = p.Cmd.StdinPipe(); err != nil {
		return err
	}
	if p.Stdout, err = p.Cmd.StdoutPipe(); err != nil {
		return err
	}
	if p.Stderr, err = p.Cmd.StderrPipe(); err != nil {
		return err
	}

	p.Ctx, p.stop = context.WithCancel(context.Background())
	for _, h := range p.handlers {
		if err := h.Start(p.Ctx); err != nil {
			return err
		}
	}
	p.loopOutput()

	if err = p.Cmd.Start(); err != nil {
		return err
	}
	p.loopHealthCheck()
	return nil
}

func (p *Process) Stop(timeout time.Duration) error {
	log.Infof("begin stop process: %s", p.Name)
	if err := p.Cmd.Process.Signal(os.Interrupt); err != nil {
		return err
	}

	go func() {
		ctx, cancel := context.WithTimeout(p.Ctx, timeout)
		defer cancel()

		select {
		case <-ctx.Done():
			if err := ctx.Err(); err == context.DeadlineExceeded {
				log.Errorf("process exit timeout, begin kill: %s", err)
				if err := p.Cmd.Process.Kill(); err != nil {
					log.Errorf("process kill failed: %s", err)
				}
			}
		}
	}()
	return nil
}

func (p *Process) RegisterHandler(h Handler) {
	p.handlers = append(p.handlers, h)
}

func (p *Process) loopHealthCheck() {
	log.Infof("begin loop health check: %s", p.Name)
	go func() {
		err := p.Cmd.Wait()
		log.Infof("exit loop health check: %s, %s", p.Name, err)
		p.stop()
	}()
}

func (p *Process) loopOutput() {
	log.Infof("begin loop output: %s", p.Name)
	go func() {
		defer log.Infof("exit loop output: %s", p.Name)

		scanner := bufio.NewScanner(io.MultiReader(p.Stdout, p.Stderr))
		for scanner.Scan() {
			out := scanner.Text()
			for _, h := range p.handlers {
				h.Channel() <- &out
			}
			select {
			case <-p.Ctx.Done():
				return
			default:
			}
		}
	}()
}