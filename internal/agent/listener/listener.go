package listener

import (
	"bufio"
	"context"
	"dst-run/internal/agent/handler"
	"dst-run/internal/common/logging"
	"io"
	"sync/atomic"
)

var log = logging.SugaredLogger()

type Listener struct {
	ready          *atomic.Bool
	outputChannels []chan *string
}

func NewListener() *Listener {
	l := Listener{
		ready: &atomic.Bool{},
	}
	l.ready.Store(false)
	return &l
}

func (l *Listener) Start(ctx context.Context, r io.Reader) error {
	log.Info("Begin listen output")
	scanner := bufio.NewScanner(r)
	go func() {
		defer l.ready.Store(false)
		for scanner.Scan() {
			out := scanner.Text()
			for _, c := range l.outputChannels {
				c <- &out
			}
			select {
			case <-ctx.Done():
				return
			default:
			}
		}
	}()
	l.ready.Store(true)
	return nil
}

func (l *Listener) RegisterHandler(h handler.Handler) {
	l.outputChannels = append(l.outputChannels, h.Channel())
}
