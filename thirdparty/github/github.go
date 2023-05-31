package github

import (
	"dst-run/internal/comm"
	"encoding/json"
	"fmt"
	"net/http"
)

func GetLatestRelease(author, repo string) (string, error) {
	url := fmt.Sprintf("https://api.github.com/repos/%s/%s/releases/latest", author, repo)

	resp, err := comm.ProxyClient().R().Get(url)
	if err != nil {
		return "", comm.NewErr(err)
	}
	if resp.StatusCode() != http.StatusOK {
		return "", comm.NewErr(resp)
	}
	var v LatestReleaseResp
	if err := json.Unmarshal(resp.Body(), &v); err != nil {
		return "", err
	}

	return v.TagName, nil
}

func DownLoadRelease(tag, downloadFile, outputPath string) error {
	url := fmt.Sprintf("https://github.com/tModLoader/tModLoader/releases/download/%s/%s", tag, downloadFile)

	_, err := comm.ProxyClient().R().SetOutput(outputPath).Get(url)
	return err
}
