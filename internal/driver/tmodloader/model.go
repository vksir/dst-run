package tmodloader

type Status struct {
	Status int `json:"status"`
}

type PlayerList []string

type ModMap map[string]*Mod
type ModIdList []string
type Mod struct {
	Id     string `json:"id" binding:"required"`
	Name   string `json:"name"`
	Remark string `json:"remark"`
	Config string `json:"config"`
}

type ArchiveMap map[string]*Archive
type ArchiveNameList []string
type Archive struct {
	Name     string `json:"name" binding:"required"`
	CreateAt string `json:"create_at"`
	UpdateAt string `json:"update_at"`
}

type Config struct {
	AutoCreate int      `json:"auto_create" binding:"oneof=1 2 3"`
	Difficulty int      `json:"difficulty" binding:"oneof=0 1 2 3"`
	MaxPlayers int      `json:"max_players" binding:"gt=0"`
	Password   string   `json:"password"`
	Port       int      `json:"port" binding:"gte=1,lte=65535"`
	Seed       string   `json:"seed"`
	WorldName  string   `json:"world_name"`
	EnableMods []string `json:"enable_mods"`
}

type ArchivePath struct {
	Root    string
	WldPath string
}
