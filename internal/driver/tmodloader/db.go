package tmodloader

import (
	"dst-run/internal/comm"
)

func getModsInDB() (map[string]*Mod, error) {
	sql := `select * from t_tmodloader_mod`
	rows, err := db.Query(sql)
	if err != nil {
		return nil, comm.NewErr(err)
	}

	mods := make(map[string]*Mod)
	for rows.Next() {
		var m Mod
		if err := rows.Scan(&m.Id, &m.Name, &m.Remark, &m.Config); err != nil {
			return nil, comm.NewErr(err)
		}
		mods[m.Id] = &m
	}
	return mods, nil
}

func addModsInDB(mods map[string]*Mod) error {
	sql := `insert into t_tmodloader_mod 
(id, name, remark, config) 
values (?, ?, ?, ?)`

	for _, mod := range mods {
		if _, err := db.Exec(sql, mod.Id, mod.Name, mod.Remark, mod.Config); err != nil {
			return comm.NewErr(err)
		}
	}
	return nil
}

func delModsInDB(modIds []string) error {
	sql := `delete from t_tmodloader_mod where id = ?`

	for _, modId := range modIds {
		if _, err := db.Exec(sql, modId); err != nil {
			return comm.NewErr(err)
		}
	}
	return nil
}

func updateModsInDB(mods map[string]*Mod) error {
	sql := `update t_tmodloader_mod
set name = ?, remark = ?, config = ?
where id = ?`

	for _, mod := range mods {
		if _, err := db.Exec(sql, mod.Name, mod.Remark, mod.Config, mod.Id); err != nil {
			return comm.NewErr(err)
		}
	}
	return nil
}

func initModsTable() {
	sql := `create table if not exists t_tmodloader_mod
(
	id text primary key not null,
	name text,
	remark text,
	config text
)`

	if _, err := db.Exec(sql); err != nil {
		panic(err)
	}
}

func initDB() {
	initModsTable()
}
