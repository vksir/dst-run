package entity

type TModLoaderCluster struct {
	Model

	AutoCreate int    `json:"auto_create" binding:"oneof=1 2 3"`
	Difficulty int    `json:"difficulty" binding:"oneof=0 1 2 3"`
	MaxPlayers int    `json:"max_players" binding:"gt=0"`
	Password   string `json:"password"`
	Port       int    `json:"port" binding:"gte=1,lte=65535"`
	Seed       string `json:"seed"`
	WorldName  string `json:"world_name"`

	Mods []TModLoaderModInCluster `gorm:"foreignKey:TModLoaderClusterId"`
}

type TModLoaderModInCluster struct {
	Model

	CurrentConfig       string
	TModLoaderClusterId string `gorm:"<-:create"`

	ModId string        `gorm:"<-:create"`
	Mod   TModLoaderMod `gorm:"foreignKey:ModId"`
}

type TModLoaderMod struct {
	Model

	ModId  string `gorm:"unique"`
	Name   string
	Remark string
	Config string
}

type TModLoaderEvent struct {
	Model

	Type string
	Code int
	Msg  string
}
