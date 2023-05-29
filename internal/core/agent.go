package core

type AgentDriver interface {
	Name() string
	Processes() []*Process
	Start() error
	Stop() error
	Install() error
	Update() error
	Config() error
}

type Agent struct {
	Driver AgentDriver
}

func NewAgent(a AgentDriver) *Agent {
	return &Agent{Driver: a}
}

func (a *Agent) Active() bool {
	if len(a.Driver.Processes()) == 0 {
		return false
	}

	for _, p := range a.Driver.Processes() {
		if !p.Active() {
			return false
		}
	}
	return true
}

func (a *Agent) Start() error {
	if a.Active() {
		log.Infof("[%s] already running, no need start", a.Driver.Name())
		return nil
	}

	if err := a.Driver.Config(); err != nil {
		return err
	}
	return a.Driver.Start()
}

func (a *Agent) Stop() error {
	return a.Driver.Stop()
}

func (a *Agent) Restart() error {
	if a.Active() {
		if err := a.Stop(); err != nil {
			return err
		}
	}
	return a.Start()
}

func (a *Agent) Update() error {
	active := a.Active()

	if active {
		if err := a.Stop(); err != nil {
			return err
		}
	}
	if err := a.Driver.Update(); err != nil {
		return err
	}

	if active {
		if err := a.Start(); err != nil {
			return err
		}
	}
	return nil
}

func (a *Agent) Install() error {
	if a.Active() {
		if err := a.Stop(); err != nil {
			return err
		}
	}
	return a.Driver.Install()
}
