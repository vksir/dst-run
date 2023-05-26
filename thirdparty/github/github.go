package github

import (
	"encoding/json"
	"fmt"
	"github.com/go-resty/resty/v2"
	"github.com/spf13/viper"
)

func GetLatestRelease(author, repo string) (string, error) {
	url := fmt.Sprintf("https://api.github.com/repos/%s/%s/releases/latest", author, repo)

	c := resty.New()
	if proxy := viper.GetString("proxy"); proxy != "" {
		c.SetProxy(proxy)
	}

	resp, err := c.R().Get(url)
	if err != nil {
		return "", err
	}
	var v LatestReleaseResp
	if err := json.Unmarshal(resp.Body(), &v); err != nil {
		return "", err
	}

	return v.TagName, nil
}

func DownLoadRelease(tag, downloadFile, outputPath string) error {
	url := fmt.Sprintf("https://github.com/tModLoader/tModLoader/releases/download/%s/%s", tag, downloadFile)

	c := resty.New()
	if proxy := viper.GetString("proxy"); proxy != "" {
		c.SetProxy(proxy)
	}

	_, err := c.R().SetOutput(outputPath).Get(url)
	return err
}
