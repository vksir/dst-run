package usecase

import (
	"dst-run/pkg/log"
)

type DontStarveConsoleUseCase struct {
	DontStarveConsoleDriver
	l log.Interface
}

func NewDontStarveConsoleUseCase(driver DontStarveConsoleDriver, l log.Interface) *DontStarveConsoleUseCase {
	return &DontStarveConsoleUseCase{DontStarveConsoleDriver: driver, l: l}
}
