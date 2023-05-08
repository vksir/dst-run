package handler

import (
	"context"
	"dst-run/internal/common/logging"
)

const (
	bufferSize = 128
)

var log = logging.SugaredLogger()

type Handler interface {
	Ready() bool
	Channel() chan *string
	Start(context.Context) error
}
