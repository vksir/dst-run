package main

import (
	"dst-run/internal/comm"
	"dst-run/internal/server"
)

var log = comm.GetSugaredLogger()

func main() {
	log.Info("start neutron star")
	server.Run()
}
