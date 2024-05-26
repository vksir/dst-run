package usecase

type DontStarveModUseCase struct {
	DontStarveModRepo
	DontStarveModApi
}

func NewDontStarveModUseCase(repo DontStarveModRepo, api DontStarveModApi) *DontStarveModUseCase {
	return &DontStarveModUseCase{repo, api}
}
