package main

import (
	"context"
	"dst-run/internal/adapter/tmodloader"
	"dst-run/internal/comm"
	"dst-run/internal/core"
	"dst-run/internal/report"
	"time"
)

var log = comm.SugaredLogger()

func main() {
	log.Info("start neutron star")
	//config.Read()
	err := report.R.Start(context.Background())
	if err != nil {
		panic(err)
	}

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
