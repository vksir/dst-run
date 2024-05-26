package usecase

type DontStarveStatusUseCase struct {
	DontStarveStatusDriver
}

func NewDontStarveStatusUseCase(driver DontStarveStatusDriver) *DontStarveStatusUseCase {
	return &DontStarveStatusUseCase{DontStarveStatusDriver: driver}
}
