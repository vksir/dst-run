package handler

import (
	"context"
	"fmt"
	"strings"
	"sync/atomic"
)

type Cut struct {
	ready      *atomic.Bool
	flag       *atomic.Bool
	channel    chan *string
	cutContent []string
}

func NewCut() *Cut {
	c := Cut{
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
