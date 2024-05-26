package util

import (
	"dst-run/pkg/log"
	"fmt"
	"github.com/go-resty/resty/v2"
	"github.com/spf13/viper"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"runtime"
)

func ExistPath(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

func ReadFile(path string) ([]byte, error) {
	return os.ReadFile(path)
}

func WriteFile(path string, content []byte) error {
	return os.WriteFile(path, content, 0640)
}

func CopyFile(src, dst string) error {
	cmd := exec.Command("cp", "-rf", src, dst)
	return RunCmd(cmd)
}

func RmvPath(path string) error {
	return os.RemoveAll(path)
}

func MkDir(paths ...string) error {
	for _, p := range paths {
		if err := os.MkdirAll(p, 0o755); err != nil {
			return err
		}
	}
	return nil
}

func ClearDir(path string) error {
	cmdString := fmt.Sprintf("rm -rf %s", filepath.Join(path, "*"))
	cmd := exec.Command("bash", "-c", cmdString)
	return RunCmd(cmd)
}

func Compress(targetPath string, workingDir string, compressPath ...string) error {
	args := append([]string{"-qr", targetPath}, compressPath...)
	cmd := exec.Command("zip", args...)
	cmd.Dir = workingDir
	return RunCmd(cmd)
}

func UnCompress(workingDir, unCompressPath string) error {
	cmd := exec.Command("unzip", unCompressPath)
	cmd.Dir = workingDir
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
		log.Error("[%s] Close failed", GetShortFile(1))
	}
}

func GetShortFile(skip int) string {
	_, filePath, line, _ := runtime.Caller(skip + 1)
	_, filename := path.Split(filePath)
	return fmt.Sprintf("%s:%d", filename, line)
}

func ProxyClient() *resty.Client {
	c := resty.New()
	if proxy := viper.GetString("ns.proxy"); proxy != "" {
		c.SetProxy(proxy)
	}
	return c
}

type List[T comparable] []T

func (l List[T]) Remove(ele T) ([]T, error) {
	var pos int
	for pos = 0; pos < len(l); pos++ {
		if (l)[pos] == ele {
			break
		}
	}

	if pos >= len(l) {
		return nil, fmt.Errorf("element not exist")
	}

	if pos == len(l)-1 {
		return l[:pos], nil
	} else {
		return append(l[:pos], l[pos+1:]...), nil
	}
}
