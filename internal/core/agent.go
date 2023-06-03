package core

import (
	"context"
	"dst-run/internal/comm"
	"fmt"
	"sync"
	"time"
)

const (
	StatusActive = iota
	StatusInactive

	StatusStarting
	StatusStopping
	StatusRestarting
	StatusInstalling
	StatusUpdating
	StatusWaitingReady
)

var StatusString = []string{
	"Active",
	"Inactive",
	"Staring",
	"Stopping",
	"Restarting",
	"Installing",
	"Updating",
	"WaitingReady",
}

type AgentDriver interface {
	Name() string
	Start(context.Context, *sync.WaitGroup) error
	Stop() error
	Install() error
	Update() error
}

type Agent struct {
	status int
	Driver AgentDriver

	wrCtx    context.Context
	wrCancel context.CancelFunc
}

func NewAgent(a AgentDriver) *Agent {
	return &Agent{
		status: StatusInactive,
		Driver: a,
	}
}

func (a *Agent) Status() int {
	return a.status
}

// Start 仅允许在 Inactive 状态调用
func (a *Agent) Start() error {
	if a.status != StatusInactive {
		return comm.NewErr(fmt.Sprintf("status is %s, could not start", StatusString[a.status]))
	}

	a.status = StatusStarting
	go func() {
		a.startAndWaitReady()
	}()
	return nil
}

// Stop 仅允许在 Active 或 WaitingReady 状态调用
func (a *Agent) Stop() error {
	if a.status != StatusActive && a.status != StatusWaitingReady {
		return nil
	}

	a.status = StatusStopping
	go func() {
		a.inlineStop()
		a.status = StatusInactive
	}()
	return nil
}

// Restart 仅允许在 Active、WaitingReady 或 Inactive 状态调用
func (a *Agent) Restart() error {
	if a.status != StatusActive && a.status != StatusWaitingReady && a.status != StatusInactive {
		return comm.NewErr(fmt.Sprintf("status is %s, could not restart", StatusString[a.status]))
	}

	oldStatus := a.status
	a.status = StatusRestarting
	go func() {
		if oldStatus == StatusActive || oldStatus == StatusWaitingReady {
			a.inlineStop()
		}
		a.startAndWaitReady()
	}()
	return nil
}

// Update 更新后恢复原来的状态，仅允许在 Active、WaitingReady 或 Inactive 状态调用
func (a *Agent) Update() error {
	if a.status != StatusActive && a.status != StatusWaitingReady && a.status != StatusInactive {
		return comm.NewErr(fmt.Sprintf("status is %s, could not update", StatusString[a.status]))
	}

	oldStatus := a.status
	a.status = StatusUpdating
	go func() {
		if oldStatus == StatusActive || oldStatus == StatusWaitingReady {
			a.inlineStop()
		}

		if err := a.Driver.Update(); err != nil {
			log.Errorf("[%s] update failed: %s", a.Driver.Name(), err)
		}

		if oldStatus == StatusActive || oldStatus == StatusWaitingReady {
			a.startAndWaitReady()
		} else {
			a.status = StatusInactive
		}
	}()
	return nil
}

// Install 仅在 Inactive 状态调用
func (a *Agent) Install() error {
	if a.status != StatusInactive {
		return comm.NewErr(fmt.Sprintf("status is %s, could not install", StatusString[a.status]))
	}

	a.status = StatusInstalling
	go func() {
		if err := a.Driver.Install(); err != nil {
			log.Errorf("[%s] install failed: %s", a.Driver.Name(), err)
		}
		a.status = StatusInactive
	}()
	return nil
}

func (a *Agent) startAndWaitReady() {
	a.wrCtx, a.wrCancel = context.WithTimeout(context.Background(), time.Minute*3)
	var wg sync.WaitGroup
	wg.Add(1)

	if err := a.Driver.Start(a.wrCtx, &wg); err != nil {
		log.Errorf("[%s] start failed: %s", a.Driver.Name(), err)
		a.status = StatusInactive
		return
	}

	a.status = StatusWaitingReady

	wg.Wait()
	if err := a.wrCtx.Err(); err == context.DeadlineExceeded {
		log.Errorf("[%s] start timeout", a.Driver.Name())
		a.status = StatusInactive
		return
	} else if err == context.Canceled {
		log.Warnf("[%s] start canceled", a.Driver.Name())
		a.status = StatusInactive
		return
	} else {
		log.Infof("[%s] start completed", a.Driver.Name())
		a.status = StatusActive
	}
}

func (a *Agent) inlineStop() {
	if a.wrCancel != nil {
		a.wrCancel()
		select {
		case <-a.wrCtx.Done():
		}
	}

	if err := a.Driver.Stop(); err != nil {
		log.Panicf("[%s] stop failed: %s", a.Driver.Name(), err)
	}
}
