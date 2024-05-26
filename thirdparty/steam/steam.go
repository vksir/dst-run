package steam

import (
	"dst-run/internal/comm"
	"dst-run/pkg/log"
	"dst-run/pkg/util"
	"fmt"
	"github.com/antchfx/htmlquery"
	"net/http"
	"strings"
	"sync"
	"time"
)

func GetWorkShopItemInfos(ids []string) ([]*WorkShopItem, error) {
	log.Debug("get workshop item info: %v", ids)

	c := util.ProxyClient().SetTimeout(5 * time.Second)

	var w sync.WaitGroup
	w.Add(len(ids))

	var wl []*WorkShopItem
	var lock sync.Mutex

	for _, id := range ids {
		go func(id string) {
			defer w.Done()

			resp, err := c.R().Get(fmt.Sprintf("https://steamcommunity.com/sharedfiles/filedetails/?id=%s", id))
			if err != nil {
				log.Error("connect failed: %s", comm.NewErr(err))
				return
			}
			if resp.StatusCode() != http.StatusOK {
				log.Error("request failed: %s", comm.NewErr(resp))
				return
			}

			doc, err := htmlquery.Parse(strings.NewReader(resp.String()))
			if err != nil {
				log.Error("parse html failed: %s", comm.NewErr(err))
				return
			}
			res := htmlquery.FindOne(doc, "//div[@class='workshopItemTitle']")
			if res == nil {
				log.Error("xpath failed: %s", id)
				return
			}

			i := WorkShopItem{
				Id:   id,
				Name: htmlquery.InnerText(res),
			}
			lock.Lock()
			defer lock.Unlock()
			wl = append(wl, &i)
		}(id)
	}

	w.Wait()
	return wl, nil
}
