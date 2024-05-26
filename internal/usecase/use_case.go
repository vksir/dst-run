package usecase

type UseCase struct {
	DontStarveClusterUseCase *DontStarveClusterUseCase
	DontStarveConfigUseCase  *DontStarveConfigUseCase
	DontStarveConsoleUseCase *DontStarveConsoleUseCase
	DontStarveControlUseCase *DontStarveControlUseCase
	DontStarveEventUseCase   *DontStarveEventUseCase
	DontStarveModUseCase     *DontStarveModUseCase
	DontStarveStatusUseCase  *DontStarveStatusUseCase
}
