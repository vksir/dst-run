package handler

import (
	"context"
	"dst-run/internal/common/constant"
	"dst-run/internal/common/util"
	"os"
	"sync/atomic"
)

type Record struct {
	ready   *atomic.Bool
	channel chan *string
}

func NewRecord() *Record {
	r := Record{
		ready:   &atomic.Bool{},
		channel: make(chan *string, bufferSize),
	}
	return &r
}

func (r *Record) Ready() bool {
	return r.ready.Load()
}

func (r *Record) Channel() chan *string {
	return r.channel
}

func (r *Record) Start(ctx context.Context) error {
	w, err := os.OpenFile(constant.TModLoaderLogPath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0640)
	if err != nil {
		return err
	}
	log.Info("Begin output record")
	go func() {
		defer r.ready.Store(false)
		defer util.Close(w)
		for {
			select {
			case <-ctx.Done():
				log.Warn("Output record stopped")
				return
			case s := <-r.channel:
				log.Debugf("[tModLoader] %s", *s)
				_, err = w.Write([]byte(*s + "\n"))
				if err != nil {
					log.Error("Write record failed: ", err)
				}
			}
		}
	}()
	r.ready.Store(true)
	return nil
}
