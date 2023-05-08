package util

import (
	"dst-run/internal/common/logging"
	"fmt"
	"os/exec"
	"path"
	"runtime"
	"strings"
)

var log = logging.SugaredLogger()

func Copy(src, dst string) error {
	return RunCmd(fmt.Sprintf("cp -rf %s %s", src, dst))
}

func Remove(path string) error {
	return RunCmd(fmt.Sprintf("rm -rf %s", path))
}

func RunCmd(cmd string) error {
	if cmd == "" {
		return fmt.Errorf("empty cmd")
	}
	cmdLst := strings.Split(cmd, " ")
	c := exec.Command(cmdLst[0])
	if len(cmdLst) > 1 {
		c.Args = append(c.Args, cmdLst[1:]...)
	}
	out, err := c.CombinedOutput()
	if err != nil {
		log.Error("Run cmd failed", err, "cmd", cmd, "out", out)
		return err
	}
	return nil
}

type Closeable interface {
	Close() error
}

func Close(c Closeable) {
	if err := c.Close(); err != nil {
		log.Errorf("[%s] Close failed", GetShortFile(1))
	}
}

func GetShortFile(skip int) string {
	_, filePath, line, _ := runtime.Caller(skip + 1)
	_, filename := path.Split(filePath)
	return fmt.Sprintf("%s:%d", filename, line)
}
