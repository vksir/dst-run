package usecase

type DontStarveEventUseCase struct {
	DontStarveEventRepo
}

func NewDontStarveEventUseCase(repo DontStarveEventRepo) *DontStarveEventUseCase {
	return &DontStarveEventUseCase{DontStarveEventRepo: repo}
}
