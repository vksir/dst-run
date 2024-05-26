package http

import (
	"dst-run/pkg/log"
	"fmt"
	"github.com/gin-gonic/gin"
	"net/http"
)

const (
	CodeOk = iota
)

const (
	CodeBadRequest    = iota + 4000
	codeBadRequestMax = 5000
)

const (
	CodeInternal    = iota + 5000
	codeInternalMax = 6000
)

type response struct {
	code  int
	error string
}

// autoResp
// 1. 成功时，返回空 json 或 结构体
// 2. 失败时，自动选择 HttpStatus，返回 response
func autoResp(c *gin.Context, code int, data any) {
	if code == CodeOk {
		if data == nil {
			data = response{CodeOk, ""}
		}
		c.JSON(http.StatusOK, data)
		return
	}

	var msg string
	switch data.(type) {
	case string:
		msg = data.(string)
	case error:
		msg = data.(error).Error()
	default:
		msg = fmt.Sprintf("invalid msg type: %T", data)
		log.Error(msg)
		c.AbortWithStatusJSON(http.StatusInternalServerError, response{CodeInternal, msg})
		return
	}

	var httpCode int
	if code >= CodeBadRequest && code < codeBadRequestMax {
		httpCode = http.StatusBadRequest
	} else if code >= CodeInternal && code < codeInternalMax {
		httpCode = http.StatusInternalServerError
	} else {
		msg := fmt.Sprintf("invalid response code: %d", code)
		log.Error(msg)
		c.AbortWithStatusJSON(http.StatusInternalServerError, response{CodeInternal, msg})
		return
	}

	c.AbortWithStatusJSON(httpCode, response{code, msg})
}
