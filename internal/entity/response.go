package entity

import (
	"dst-run/internal/comm"
	"dst-run/pkg/log"
	"fmt"
)

func NewRespOk() *RespOk {
	return &RespOk{}
}

type RespOk struct{}

func NewRespErr(a any) *RespErr {
	r := RespErr{
		Code: comm.ErrSys,
	}

	switch a.(type) {
	case *comm.Err:
		log.Error("response err: %s", a.(*comm.Err).Error())

		// 接口不返回 short file
		r.Code = a.(*comm.Err).Code
		r.Detail = a.(*comm.Err).Detail
	case string:
		r.Detail = a.(string)
	case error:
		r.Detail = a.(error).Error()
	default:
		panic(fmt.Sprintf("invalid type: %T", a))
	}

	return &r
}

type RespErr struct {
	Code   int
	Detail string
}
