package process

import (
	"bufio"
	"context"
	"dst-run/pkg/log"
	"io"
	"os/exec"
	"strings"
	"sync"
)

type Process struct {
	name string
	Ctx  context.Context

	Cmd    *exec.Cmd
	Stdin  io.Writer
	Stdout io.Reader
	Stderr io.Reader

	l log.Interface

	outFunc     map[string]func(*string)
	outFuncLock sync.Mutex
}

func NewProcess(name string, exe string, args []string, l log.Interface) *Process {
	ctx := context.Background()
	p := &Process{
		name:    name,
		Ctx:     ctx,
		Cmd:     exec.CommandContext(ctx, exe, args...),
		outFunc: make(map[string]func(*string)),
		l:       l.WithTag("Process:" + name),
	}
	return p
}

func (p *Process) Name() string {
	return p.name
}

func (p *Process) Active() bool {
	return p.Cmd.Process != nil && p.Ctx.Err() == nil
}

func (p *Process) Start() error {
	p.l.Info("start process: %s", strings.Join(p.Cmd.Args, " "))

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

	go p.loopOutput()
	if err = p.Cmd.Start(); err != nil {
		return err
	}
	return nil
}

func (p *Process) Stop() error {
	return p.Cmd.Cancel()
}

func (p *Process) RegisterOutFunc(name string, f func(*string)) {
	p.outFuncLock.Lock()
	defer p.outFuncLock.Unlock()

	p.outFunc[name] = f
}

func (p *Process) UnregisterOutFunc(name string) {
	p.outFuncLock.Lock()
	defer p.outFuncLock.Unlock()

	if _, ok := p.outFunc[name]; ok {
		delete(p.outFunc, name)
	}
}

func (p *Process) loopOutput() {
	p.l.Info("begin loop output")
	defer p.l.Info("exit loop output")

	scanner := bufio.NewScanner(io.MultiReader(p.Stdout, p.Stderr))
	for scanner.Scan() {
		out := scanner.Text()

		p.outFuncLock.Lock()
		for _, f := range p.outFunc {
			f(&out)
		}
		p.outFuncLock.Unlock()

		select {
		case <-p.Ctx.Done():
			return
		default:
		}
	}
}
