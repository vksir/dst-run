package log

import (
	"context"
	"fmt"
	"github.com/sirupsen/logrus"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"strings"
)

var Log = New()

var (
	Debug    = Log.Debug
	Info     = Log.Info
	Warn     = Log.Warn
	Error    = Log.Error
	Fatal    = Log.Fatal
	SetLevel = Log.SetLevel
)

type Interface interface {
	WithTag(tag string) Interface

	Debug(format string, args ...any)
	Info(format string, args ...any)
	Warn(format string, args ...any)
	Error(format string, args ...any)
	Fatal(format string, args ...any)

	DebugC(ctx context.Context, format string, args ...any)
	InfoC(ctx context.Context, format string, args ...any)
	WarnC(ctx context.Context, format string, args ...any)
	ErrorC(ctx context.Context, format string, args ...any)
	FatalC(ctx context.Context, format string, args ...any)
}

func New() *Logger {
	return &Logger{logger: logrus.New()}
}

type Logger struct {
	logger *logrus.Logger
	tag    string
}

func (l *Logger) WithTag(tag string) Interface {
	return &Logger{logger: l.logger, tag: tag}
}

func (l *Logger) Debug(format string, args ...any) {
	l.log(l.logger.Logf, logrus.DebugLevel, format, args...)
}

func (l *Logger) Info(format string, args ...any) {
	l.log(l.logger.Logf, logrus.InfoLevel, format, args...)
}

func (l *Logger) Warn(format string, args ...any) {
	l.log(l.logger.Logf, logrus.WarnLevel, format, args...)
}

func (l *Logger) Error(format string, args ...any) {
	l.log(l.logger.Logf, logrus.ErrorLevel, format, args...)
}

func (l *Logger) Fatal(format string, args ...any) {
	l.log(l.logger.Logf, logrus.FatalLevel, format, args...)
}

func (l *Logger) DebugC(ctx context.Context, format string, args ...any) {
	l.log(l.logger.WithContext(ctx).Logf, logrus.DebugLevel, format, args...)
}

func (l *Logger) InfoC(ctx context.Context, format string, args ...any) {
	l.log(l.logger.WithContext(ctx).Logf, logrus.InfoLevel, format, args...)
}

func (l *Logger) WarnC(ctx context.Context, format string, args ...any) {
	l.log(l.logger.WithContext(ctx).Logf, logrus.WarnLevel, format, args...)
}

func (l *Logger) ErrorC(ctx context.Context, format string, args ...any) {
	l.log(l.logger.WithContext(ctx).Logf, logrus.ErrorLevel, format, args...)
}

func (l *Logger) FatalC(ctx context.Context, format string, args ...any) {
	l.log(l.logger.WithContext(ctx).Logf, logrus.FatalLevel, format, args...)
}

func (l *Logger) log(logf func(level logrus.Level, format string, args ...interface{}), level logrus.Level, format string, args ...any) {
	format = fmt.Sprintf("[%s] [%s] %s", getCallerShort(3), l.tag, format)
	logf(level, format, args...)
}

func (l *Logger) Init(output io.Writer, formatter logrus.Formatter) {
	l.logger.SetOutput(output)
	l.logger.SetFormatter(formatter)
}

func (l *Logger) SetLevel(level logrus.Level) {
	l.logger.SetLevel(level)
}

type formatter struct{}

func (f *formatter) Format(entry *logrus.Entry) ([]byte, error) {
	pid := os.Getpid()
	time := entry.Time.Format("2006-01-02T15:04:05.000000")
	level := strings.ToUpper(entry.Level.String())
	traceId := getTraceIdFromCtx(entry.Context)

	content := fmt.Sprintf("%s %s %d %s %s\n", time, level, pid, traceId, entry.Message)
	return []byte(content), nil
}

// getCallerShort 获取调用点文件名 + 行号
func getCallerShort(skip int) string {
	_, file, line, ok := runtime.Caller(skip + 1)
	if !ok {
		return ""
	}
	_, file = filepath.Split(file)
	return fmt.Sprintf("%s:%d", file, line)
}

// CtxSetTraceId 在 ctx 中设置 trace id
func CtxSetTraceId(ctx context.Context) context.Context {
	return context.WithValue(ctx, "trace_id", "id1")
}

// getTraceIdFromCtx 打印日志时，从 ctx 中获取 trace id 打印
func getTraceIdFromCtx(ctx context.Context) string {
	if ctx == nil {
		return "-"
	}

	val := ctx.Value("trace_id")
	if traceId, ok := val.(string); ok {
		return fmt.Sprintf("trace-%s", traceId)
	} else {
		return "-"
	}
}

func InitLog(path string, level string) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0o640)
	if err != nil {
		return fmt.Errorf("open log file failed: %v", err)
	}

	Log.Init(io.MultiWriter(os.Stdout, f), &formatter{})

	lv, err := logrus.ParseLevel(level)
	if err != nil {
		return fmt.Errorf("parse log level failed: %v", err)
	}
	Log.SetLevel(lv)
	return nil
}
