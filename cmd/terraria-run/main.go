package main

import (
	"dst-run/internal/common/config"
	_ "dst-run/internal/common/config"
	"dst-run/internal/common/logging"
	_ "dst-run/internal/common/logging"
	"dst-run/internal/server"
)

var log = logging.SugaredLogger()

func main() {
	log.Info("Start terraria run")
	config.Read()

	//a
	//:= agent.NewAgent("")
	//err := a.Start()
	//if err != nil {
	//	panic(err)
	//}
	//time.Sleep(10 * time.Second)
	//err = a.Stop()
	//if err != nil {
	//	logging.Error("Stop agent failed", err)
	//}

	//serverConfigHandler := serverconfig.NewHandler()
	//if err := serverConfigHandler.Deploy(); err != nil {
	//	panic(err)
	//}
	//
	//modHandler := mod.NewHandler()
	//err := modHandler.Deploy()
	//if err != nil {
	//	panic(err)
	//}
	//if err := controller.Start(); err != nil {
	//	panic(err)
	//}
	server.Run()
}
