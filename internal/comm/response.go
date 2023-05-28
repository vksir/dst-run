package comm

import "fmt"

func NewRespOk() *RespOk {
	return &RespOk{}
}

type RespOk struct{}

func NewRespErr(a any) *RespErr {
	r := RespErr{
		Code: ErrSys,
	}

	switch a.(type) {
	case *Err:
		log.Errorf("response err: %s", a.(*Err).Error())

		// 接口不返回 short file
		r.Code = a.(*Err).Code
		r.Detail = a.(*Err).Detail
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
