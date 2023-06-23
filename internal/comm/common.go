package comm

const (
	TimeFmtForPath  = "20060102T150405"
	TimeFmtReadable = "2006-01-02T15:04:05"
)

func init() {
	initPath()
	initLog()
	initConfig()
	initCache()
	initDB()
}
