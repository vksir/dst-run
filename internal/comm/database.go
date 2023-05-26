package comm

import (
	"database/sql"
	_ "modernc.org/sqlite"
)

var db *sql.DB

func GetDB() *sql.DB {
	return db
}

func initDB() {
	var err error
	db, err = sql.Open("sqlite", DBPath)
	if err != nil {
		panic(err)
	}
}
