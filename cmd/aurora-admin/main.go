package main

import (
	"dst-run/bootstrap"
	_ "dst-run/bootstrap"
	"dst-run/internal/app"
	"dst-run/pkg/log"
	"fmt"
	"os"
)

func main() {
	if err := bootstrap.Init(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	log.Warn("start aurora admin")
	app.Run()
}
