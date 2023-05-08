package controller

import (
	"dst-run/internal/agent"
	"dst-run/internal/common/logging"
	"dst-run/internal/common/util"
	"dst-run/internal/controller/mod"
	"dst-run/internal/controller/serverconfig"
	"dst-run/internal/report"
	"sync"
	"time"
)

const (
	StatusActive     = "ACTIVE"
	StatusInactive   = "INACTIVE"
	StatusStarting   = "STARTING"
	StatusStopping   = "STOPPING"
	StatusRestarting = "RESTARTING"
	StatusUpdating   = "UPDATING"
)

var log = logging.SugaredLogger()
var Status = StatusInactive
var Agent *agent.Agent
var Lock = sync.Mutex{}

func Start() error {
	Lock.Lock()
	defer Lock.Unlock()
	if err := serverconfig.NewHandler().Deploy(); err != nil {
		return err
	}
	if err := mod.NewHandler().Deploy(); err != nil {
		return err
	}
	return startAgent()
}

func Stop() error {
	Lock.Lock()
	defer Lock.Unlock()
	stopAgent()
	return nil
}

func Restart() error {
	if err := Stop(); err != nil {
		return err
	}
	return Start()
}

func startAgent() error {
	if Agent != nil {
		log.Info("Agent is not nil, no need start")
		return nil
	}
	changeStatus(StatusStarting)
	Agent = agent.NewAgent("", report.R)
	if err := Agent.Start(); err != nil {
		stopAgent()
		return err
	}
	go watchAgentStaringComplete()
	return nil
}

func stopAgent() {
	if Agent == nil {
		log.Info("Agent is nil, no need stop")
		return
	}
	changeStatus(StatusStopping)
	if err := Agent.Stop(); err != nil {
		log.Error("Stop agent failed: ", err)
	}
	Agent = nil
	changeStatus(StatusInactive)
}

func watchAgentStaringComplete() {
	// TODO: Timeout
	log.Info("Begin watch agent starting complete")
	for {
		if Agent == nil {
			log.Info("Agent stopped, stop watch")
			changeStatus(StatusInactive)
			return
		}
		events, err := report.R.GetEvents()
		if err != nil {
			log.Error("Get report events failed: ", err)
			changeStatus(StatusActive)
			return
		}
		for i := range events {
			if events[i].Type == report.TypeServerActive {
				changeStatus(StatusActive)
				return
			}
		}
		time.Sleep(500 * time.Millisecond)
	}
}

func changeStatus(status string) {
	if Status == status {
		return
	}
	log.Warnf("[%s] Status change from %s to %s", util.GetShortFile(1), Status, status)
	Status = status
}
