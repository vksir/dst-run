package comm

import (
	"fmt"
	"os"
	"os/exec"
	"path"
	"runtime"
	"strings"
)

var log = SugaredLogger()

func WriteFile(path string, content []byte) error {
	return os.WriteFile(path, content, 0640)
}

func CopyFile(src, dst string) error {
	cmd := exec.Command("cp", "-rf", src, dst)
	return RunCmd(cmd)
}

func RemoveFile(path string) error {
	cmd := exec.Command("rm", "-rf", path)
	return RunCmd(cmd)
}

func MakeDir(paths ...string) error {
	cmd := exec.Command("mkdir", "-p", strings.Join(paths, " "))
	return RunCmd(cmd)
}

func RunCmd(cmd *exec.Cmd) error {
	out, err := cmd.CombinedOutput()
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
