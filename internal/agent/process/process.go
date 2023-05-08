package process

import (
	"context"
	"dst-run/internal/common/constant"
	"dst-run/internal/common/logging"
	"io"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

var log = logging.SugaredLogger()

type Process struct {
	Name   string
	Stdin  io.Writer
	Stdout io.Reader
	Stderr io.Reader
	cmd    *exec.Cmd
}

func NewProcess(name string) *Process {
	cmd := exec.Command(constant.DotnetPath, "tModLoader.dll", "-server", "-config", constant.ServerConfigPath)
	cmd.Dir = filepath.Join(constant.InstallDir, "tModLoader")
	p := Process{
		Name: name,
		cmd:  cmd,
	}
	log.Infof("New process: %s", strings.Join(p.cmd.Args, " "))
	return &p
}

func (p *Process) Start() error {
	log.Info("Start process")
	var err error
	if p.Stdin, err = p.cmd.StdinPipe(); err != nil {
		return err
	}
	if p.Stdout, err = p.cmd.StdoutPipe(); err != nil {
		return err
	}
	if p.Stderr, err = p.cmd.StderrPipe(); err != nil {
		return err
	}
	if err = p.cmd.Start(); err != nil {
		return err
	}
	return nil
}

func (p *Process) Stop() error {
	if _, err := p.Stdin.Write([]byte("exit\n")); err != nil {
		log.Error("Write exit failed: ", err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	go func() {
		if err := p.cmd.Wait(); err != nil {
			log.Error("Process Wait return error: ", err)
		}
		cancel()
	}()
	select {
	case <-ctx.Done():
		if err := ctx.Err(); err != context.Canceled {
			log.Error("Process exit timeout, been killed: ", err)
			if err := p.cmd.Process.Kill(); err != nil {
				return err
			}
		}
		log.Info("Process exit normally")
	}
	return nil
}
