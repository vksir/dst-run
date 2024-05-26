package app

import (
	"dst-run/internal/controller/http"
	"dst-run/internal/usecase"
	"dst-run/internal/usecase/driver"
	"dst-run/internal/usecase/driver/donstarve"
	"dst-run/internal/usecase/repo"
	"dst-run/internal/usecase/webapi"
	"dst-run/pkg/database"
	"dst-run/pkg/log"
	"github.com/gin-gonic/gin"
	"github.com/spf13/viper"
)

func Run() {
	e := gin.Default()

	dst := donstarve.NewDst(log.Log)

	useCase := usecase.UseCase{
		DontStarveClusterUseCase: usecase.NewDontStarveClusterUseCase(
			repo.NewDontStarveClusterRepo(database.DB),
			driver.NewDontStarveClusterDriver(),
			log.Log,
			repo.NewDontStarveModRepo(database.DB),
		),

		DontStarveConfigUseCase: usecase.NewDontStarveConfigUseCase(
			repo.NewDontStarveConfigRepo(database.DB),
			log.Log,
		),

		DontStarveConsoleUseCase: usecase.NewDontStarveConsoleUseCase(
			driver.NewDontStarveConsoleDriver(dst),
			log.Log,
		),

		DontStarveControlUseCase: usecase.NewDontStarveControlUseCase(
			driver.NewDontStarveControlDriver(dst, log.Log),
			repo.NewDontStarveClusterRepo(database.DB),
			repo.NewDontStarveConfigRepo(database.DB),
		),

		DontStarveEventUseCase: usecase.NewDontStarveEventUseCase(
			repo.NewDontStarveEventRepo(database.DB),
		),

		DontStarveModUseCase: usecase.NewDontStarveModUseCase(
			repo.NewDontStarveModRepo(database.DB),
			webapi.NewDontStarveModApi(log.Log),
		),

		DontStarveStatusUseCase: usecase.NewDontStarveStatusUseCase(
			driver.NewDontStarveStatusDriver(dst),
		),
	}

	http.NewRouter(e, &useCase, log.Log)
	err := e.Run(viper.GetString("ns.listen"))
	if err != nil {
		log.Fatal("gin run failed: %v", err)
	}
}
