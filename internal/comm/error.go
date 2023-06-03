package comm

import (
	"fmt"
	"github.com/go-resty/resty/v2"
)

const (
	ErrOk = iota
	ErrSys
	ErrHttp
	ErrLocked
	ErrMax
)

func NewErr(args ...any) *Err {
	e := Err{
		Code:  ErrSys,
		Short: GetShortFile(1),
	}

	for _, a := range args {
		switch a.(type) {
		case int:
			if a.(int) < 0 || a.(int) >= ErrMax {
				panic(fmt.Sprintf("invalid error code: %d", a.(int)))
			}
			e.Code = a.(int)
		case string:
			e.Detail = a.(string)
		case error:
			e.Detail = a.(error).Error()
		case *resty.Response:
			e.Code = ErrHttp
			e.Detail = fmt.Sprintf("%d: %s", a.(*resty.Response).StatusCode(), a.(*resty.Response).String())
		default:
			panic(fmt.Sprintf("invalid error type: %T", a))
		}
	}

	return &e
}

type Err struct {
	Code   int
	Short  string
	Detail string
}

func (e *Err) Error() string {
	return fmt.Sprintf("[%s]%s", e.Short, e.Detail)
}
