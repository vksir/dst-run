package process

import (
	"context"
	"fmt"
	"sync"
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

type Core interface {
	Name() string
	Status() string
	BeforeStart(context.Context) error
	Start(context.Context) error
	Stop(context.Context) error
	Install(context.Context) error
	Update(context.Context) error
}

type ProcessPPP struct {
	status int
	Core   Core

	wrCtx    context.Context
	wrCancel context.CancelFunc

	actionLock sync.Mutex
}

func NewManager(a Core) *ProcessPPP {
	return &ProcessPPP{
		status: StatusInactive,
		Core:   a,
	}
}

func (a *ProcessPPP) Start(ctx context.Context) error {
	ok := a.actionLock.TryLock()
	if !ok {
		return fmt.Errorf("process is busy")
	}

	err := a.Core.BeforeStart(ctx)
	if err != nil {
		return fmt.Errorf("call before start failed: %v", err)
	}
	return a.Core.Start(ctx)
}

func (a *ProcessPPP) Stop(ctx context.Context) error {
	ok := a.actionLock.TryLock()
	if !ok {
		return fmt.Errorf("process is busy")
	}

	return a.Core.Stop(ctx)
}

func (a *ProcessPPP) Restart(ctx context.Context) error {
	ok := a.actionLock.TryLock()
	if !ok {
		return fmt.Errorf("process is busy")
	}

	return a.Core.Stop(ctx)
}

func (a *ProcessPPP) Update(ctx context.Context) error {
	ok := a.actionLock.TryLock()
	if !ok {
		return fmt.Errorf("process is busy")
	}

	return a.Core.Update(ctx)
}

func (a *ProcessPPP) Install(ctx context.Context) error {
	ok := a.actionLock.TryLock()
	if !ok {
		return fmt.Errorf("process is busy")
	}

	return a.Core.Install(ctx)
}
