package tmodloader

import (
	"bufio"
	comm2 "dst-run/internal/comm"
	"dst-run/pkg/cache"
	"encoding/binary"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

/*
tmod file format:
https://gist.github.com/Trivaxy/a6f3550030f220894beaabc01d3bf8aa
*/

type TMod struct {
	Name            string
	Path            string
	BuildForVersion string // The version of tModLoader that the mod has been built for
}

func getCompatibleTmod(id string) (*TMod, error) {
	singleModDir := filepath.Join(steamModDir, id)
	if _, err := os.Stat(singleModDir); os.IsNotExist(err) {
		return nil, err
	}

	// 获取 Steam Mod 目录下，单个 Mod 目录下所有 tmod 文件
	var tmods []*TMod
	err := filepath.Walk(singleModDir, func(path string, info os.FileInfo, err error) error {
		if strings.HasSuffix(info.Name(), ".tmod") {
			name := strings.Split(info.Name(), ".tmod")[0]
			tmods = append(tmods, &TMod{
				Name: name,
				Path: path,
			})
		}
		return nil
	})
	if err != nil {
		return nil, err
	}

	// 解析 tmod 文件构建版本
	for _, t := range tmods {
		fd, err := os.Open(t.Path)
		if err != nil {
			return nil, err
		}
		r := bufio.NewReader(fd)

		buf := make([]byte, 4)
		if _, err := r.Read(buf); err != nil {
			return nil, err
		}
		if string(buf) != "TMOD" {
			return nil, fmt.Errorf("invalid tmod file: %s", t.Path)
		}

		buildForVersion, err := binaryReaderReadString(r)
		if err != nil {
			return nil, err
		}
		t.BuildForVersion = buildForVersion
	}

	// 找到兼容性最好的 tmod 文件
	// 1. 构建版本尽量新
	// 2. 构建版本早于 tModLoader 版本
	tModLoaderVersionAny, ok := cache.GetCacheSafe("tml_version")
	if !ok {
		return nil, comm2.NewErr("cache key not found: tml_version")
	}
	tModLoaderVersion := tModLoaderVersionAny.(string)

	tModLoaderVersion = strings.Split(tModLoaderVersion, "v")[1]
	var latestTmod *TMod
	for _, t := range tmods {
		res, err := compareVersion(t.BuildForVersion, tModLoaderVersion)
		if err != nil {
			return nil, err
		}
		if res == compareGreater {
			continue
		}

		if latestTmod == nil {
			latestTmod = t
			continue
		}

		res, err = compareVersion(t.BuildForVersion, latestTmod.BuildForVersion)
		if err != nil {
			return nil, err
		}
		if res == compareGreater {
			latestTmod = t
		}
	}

	return latestTmod, nil
}

// binaryReaderReadString work as BinaryReader.ReadString() in C#
func binaryReaderReadString(reader *bufio.Reader) (string, error) {
	length, err := binary.ReadUvarint(reader)
	if err != nil {
		return "", err
	}

	bytes := make([]byte, length)
	_, err = reader.Read(bytes)
	if err != nil {
		return "", err
	}

	return string(bytes), nil
}

const (
	compareLess = iota
	compareGreater
	compareEqual
)

func compareVersion(a, b string) (int, error) {
	aIntList, err := conventVerStringToVerIntList(a)
	if err != nil {
		return 0, err
	}
	bIntList, err := conventVerStringToVerIntList(b)
	if err != nil {
		return 0, err
	}

	// 补齐两个列表到相同长度，末尾补 0
	var l int
	if len(aIntList) < len(bIntList) {
		l = len(bIntList)
		for j := 0; j < l-len(aIntList); j++ {
			aIntList = append(aIntList, 0)
		}
	} else {
		l = len(aIntList)
		for j := 0; j < l-len(bIntList); j++ {
			bIntList = append(bIntList, 0)
		}
	}

	for i := 0; i < l; i++ {
		if aIntList[i] > bIntList[i] {
			return compareGreater, nil
		} else if aIntList[i] < bIntList[i] {
			return compareLess, nil
		}
	}
	return compareEqual, nil
}

func conventVerStringToVerIntList(v string) ([]int, error) {
	vStringList := strings.Split(v, ".")

	var vIntList []int
	for _, s := range vStringList {
		i, err := strconv.Atoi(s)
		if err != nil {
			return nil, comm2.NewErr(err)
		}
		vIntList = append(vIntList, i)
	}
	return vIntList, nil
}
