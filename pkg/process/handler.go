package process

import (
	"context"
	"dst-run/pkg/log"
	"dst-run/pkg/util"
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
	name       string
	recordPath string
	channel    chan *string
}

func NewRecord(name, recordPath string) *Record {
	r := Record{
		name:       name,
		recordPath: recordPath,
		channel:    make(chan *string, bufferSize),
	}
	return &r
}

func (r *Record) Name() string {
	return r.name
}

func (r *Record) Channel() chan *string {
	return r.channel
}

func (r *Record) Start(ctx context.Context) error {
	w, err := os.OpenFile(r.recordPath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0640)
	if err != nil {
		return err
	}

	log.Info("[%s] begin record handler", r.name)
	go func() {
		defer util.Close(w)
		for {
			select {
			case <-ctx.Done():
				log.Warn("[%s] exit record handler", r.name)
				return
			case s := <-r.channel:
				log.Debug("[%s] %s", r.name, *s)
				_, err = w.Write([]byte(fmt.Sprintf("[%s] %s\n", r.name, *s)))
				if err != nil {
					log.Error("[%s] write record failed: %s", r.name, err)
				}
			}
		}
	}()
	return nil
}

type Cut struct {
	name       string
	channel    chan *string
	flag       *atomic.Bool
	cutContent []string
}

func NewCut(name string) *Cut {
	c := Cut{
		name:    name,
		channel: make(chan *string, bufferSize),
		flag:    &atomic.Bool{},
	}
	return &c
}

func (c *Cut) Name() string {
	return c.name
}

func (c *Cut) Channel() chan *string {
	return c.channel
}

func (c *Cut) Start(ctx context.Context) error {
	log.Info("[%s] begin output cut", c.name)

	go func() {
		for {
			select {
			case <-ctx.Done():
				log.Warn("[%s] exit output cut", c.name)
				return
			case s := <-c.channel:
				if c.flag.Load() {
					c.cutContent = append(c.cutContent, *s)
				}
			}
		}
	}()
	return nil
}

func (c *Cut) BeginCut() error {
	if c.flag.Load() {
		return fmt.Errorf("[%s] cutting now, begin cut failed", c.name)
	}
	c.flag.Store(true)
	return nil
}

func (c *Cut) StopCut() (string, error) {
	if !c.flag.Load() {
		return "", fmt.Errorf("[%s] not cutting, stop cut failed", c.name)
	}
	c.flag.Store(false)
	content := strings.Join(c.cutContent, "\n")
	log.Debug("[%s] cut success: %s", c.name, content)
	return content, nil
}

type ReportPattern struct {
	PatternString string // required
	Format        string // required
	Level         string // required
	Type          string // optional
	Pattern       *regexp.Regexp
}

type ReportEventList []*ReportEvent
type ReportEvent struct {
	Time  int64
	Msg   string
	Level string
	Type  string
}

type Report struct {
	name    string
	channel chan *string

	patterns []*ReportPattern
	lock     *sync.Mutex
	events   []*ReportEvent

	weLock     *sync.Mutex
	weChannels []chan *ReportEvent
}

func NewReport(name string, patterns []*ReportPattern) *Report {
	r := Report{
		name:     name,
		lock:     &sync.Mutex{},
		channel:  make(chan *string, bufferSize),
		patterns: patterns,

		weLock: &sync.Mutex{},
	}
	return &r
}

func (r *Report) Name() string {
	return r.name
}

func (r *Report) Channel() chan *string {
	return r.channel
}

func (r *Report) Start(_ context.Context) error {
	log.Info("[%s] begin output report", r.name)

	go func() {
		for {
			select {
			case s := <-r.channel:
				if e := r.parseEvent(s); e != nil {
					r.CacheEvent(e)
					r.putInfoWaitEventChan(e)

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
	log.Info("[%s] report event: %+v", r.name, *e)
}

func (r *Report) WaitEvent(ctx context.Context, eventType string) {
	c := make(chan *ReportEvent, reportSize)

	r.weLock.Lock()
	r.weChannels = append(r.weChannels, c)
	r.weLock.Unlock()

continueSelect:
	select {
	case e := <-c:
		if e.Type != eventType {
			goto continueSelect
		}
	case <-ctx.Done():
	}

	r.weLock.Lock()
	r.weChannels, _ = util.List[chan *ReportEvent](r.weChannels).Remove(c)
	r.weLock.Unlock()
}

func (r *Report) putInfoWaitEventChan(e *ReportEvent) {
	r.weLock.Lock()
	defer r.weLock.Unlock()

	for _, c := range r.weChannels {
		c <- e
	}
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
