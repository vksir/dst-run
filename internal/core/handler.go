package core

import (
	"context"
	"dst-run/internal/comm"
	"fmt"
	"os"
	"regexp"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

const (
	bufferSize = 128
	reportSize = 64
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

type ReportPattern struct {
	PatternString string // required
	Format        string // required
	Level         string // required
	Type          string // optional
	Pattern       *regexp.Regexp
}

type ReportEvent struct {
	Time  int64
	Msg   string
	Level string
	Type  string
}

type Report struct {
	Name    string
	channel chan *string

	patterns []*ReportPattern
	lock     *sync.Mutex
	events   []*ReportEvent
}

func NewReport(name string, patterns []*ReportPattern) *Report {
	r := Report{
		Name:     name,
		lock:     &sync.Mutex{},
		channel:  make(chan *string, bufferSize),
		patterns: patterns,
	}
	return &r
}

func (r *Report) Channel() chan *string {
	return r.channel
}

func (r *Report) Start(ctx context.Context) error {
	log.Info("begin output report")
	go func() {
		for {
			select {
			case s := <-r.channel:
				if e := r.parseEvent(s); e != nil {
					r.CacheEvent(e)
				}
			}
		}
	}()
	return nil
}

func (r *Report) GetEvents() ([]*ReportEvent, error) {
	r.lock.Lock()
	events := make([]*ReportEvent, len(r.events))
	copy(events, r.events)
	r.lock.Unlock()
	return events, nil
}

func (r *Report) CacheEvent(e *ReportEvent) {
	r.lock.Lock()
	r.events = append(r.events, e)
	if len(r.events) > reportSize {
		r.events = r.events[len(r.events)-reportSize:]
	}
	r.lock.Unlock()
	log.Infof("report event: %+v", *e)
}

// parseEvent 传入 Process 输出，根据预定义事件规则，从中解析事件
func (r *Report) parseEvent(s *string) *ReportEvent {
	for i := range r.patterns {
		if res := r.patterns[i].Pattern.FindStringSubmatch(*s); res != nil {
			var args []any
			res = res[1:]
			for i := range res {
				args = append(args, res[i])
			}
			e := ReportEvent{
				Level: r.patterns[i].Level,
				Time:  time.Now().Unix(),
				Msg:   fmt.Sprintf(r.patterns[i].Format, args...),
				Type:  r.patterns[i].Type,
			}
			return &e
		}
	}
	return nil
}
