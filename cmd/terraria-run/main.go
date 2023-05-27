package main

import (
	"dst-run/internal/adapter/tmodloader"
	"dst-run/internal/comm"
	"dst-run/internal/core"
	"time"
)

var log = comm.SugaredLogger()

func main() {
	log.Info("start neutron star")

	var err error

	//config.Read()

	//a := core.NewAgent(dontstarvetogether.NewAgentAdapter())
	//err = a.Start()
	//if err != nil {
	//	panic(err)
	//}

	a := core.NewAgent(tmodloader.NewAgentAdapter())
	err = a.Start()
	if err != nil {
		panic(err)
	}

	//server.Run()
	time.Sleep(1000 * time.Second)
}
