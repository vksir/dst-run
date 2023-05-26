package core

import (
	"context"
	"dst-run/internal/comm"
	"fmt"
	"os"
	"strings"
	"sync/atomic"
)

const (
	bufferSize = 128
)

type Handler interface {
	Channel() chan *string
	Start(context.Context) error
}

type Record struct {
	Name       string
	recordPath string
	channel    chan *string
}

func NewRecord(name, recordPath string) *Record {
	r := Record{
		Name:       name,
		recordPath: recordPath,
		channel:    make(chan *string, bufferSize),
	}
	return &r
}

func (r *Record) Channel() chan *string {
	return r.channel
}

func (r *Record) Start(ctx context.Context) error {
	w, err := os.OpenFile(r.recordPath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0640)
	if err != nil {
		return err
	}

	log.Info("begin record handler")
	go func() {
		defer comm.Close(w)
		for {
			select {
			case <-ctx.Done():
				log.Warn("exit record handler")
				return
			case s := <-r.channel:
				log.Debugf("[%s] %s", r.Name, *s)
				_, err = w.Write([]byte(fmt.Sprintf("[%s] %s\n", r.Name, *s)))
				if err != nil {
					log.Error("write record failed: ", err)
				}
			}
		}
	}()
	return nil
}

// Cut TODO: more simple
type Cut struct {
	Name       string
	ready      *atomic.Bool
	flag       *atomic.Bool
	channel    chan *string
	cutContent []string
}

func NewCut(name string) *Cut {
	c := Cut{
		Name:    name,
		ready:   &atomic.Bool{},
		flag:    &atomic.Bool{},
		channel: make(chan *string, bufferSize),
	}
	c.flag.Store(false)
	return &c
}

func (c *Cut) Ready() bool {
	return c.ready.Load()
}

func (c *Cut) Channel() chan *string {
	return c.channel
}

func (c *Cut) Start(ctx context.Context) error {
	log.Info("Begin output cut")
	go func() {
		defer c.ready.Store(false)
		for {
			select {
			case <-ctx.Done():
				log.Warn("Output cut stopped")
				return
			case s := <-c.channel:
				if c.flag.Load() {
					c.cutContent = append(c.cutContent, *s)
				}
			}
		}
	}()
	c.ready.Store(true)
	return nil
}

func (c *Cut) BeginCut() error {
	if !c.ready.Load() {
		return fmt.Errorf("cut is not ready, begin cut failed")
	}
	if c.flag.Load() {
		return fmt.Errorf("cutting now, begin cut failed")
	}
	c.flag.Store(true)
	return nil
}

func (c *Cut) StopCut() (string, error) {
	if !c.flag.Load() {
		return "", fmt.Errorf("not cutting, stop cut failed")
	}
	c.flag.Store(false)
	content := strings.Join(c.cutContent, "\n")
	log.Debug("Cut success: ", content)
	return content, nil
}
