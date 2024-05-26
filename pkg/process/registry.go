package process

import (
	"fmt"
	"sync"
)

var processes = make(map[string]*ProcessPPP)
var processesLock = sync.Mutex{}

func GetProcess(name string) (*ProcessPPP, error) {
	processesLock.Lock()
	defer processesLock.Unlock()

	p, ok := processes[name]
	if !ok {
		return nil, fmt.Errorf("process %s not exsits", name)
	}
	return p, nil
}

func RegisterProcess(name string, core Core) (*ProcessPPP, error) {
	processesLock.Lock()
	defer processesLock.Unlock()

	_, ok := processes[name]
	if ok {
		return nil, fmt.Errorf("process %s already exsits", name)
	}

	p := NewManager(core)
	processes[name] = p
	return p, nil
}

func UnRegisterProcess(name string) error {
	processesLock.Lock()
	defer processesLock.Unlock()

	_, ok := processes[name]
	if !ok {
		return fmt.Errorf("process %s not exsits", name)
	}
	delete(processes, name)
	return nil
}
