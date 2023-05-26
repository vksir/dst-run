package model

type Config struct {
	ServerConfig ServerConfig   `json:"server_config"`
	IdToMod      map[string]Mod `json:"mod"`
}

type ServerConfig struct {
	AutoCreate int    `json:"auto_create" binding:"oneof=1 2 3"`
	Difficulty int    `json:"difficulty" binding:"oneof=0 1 2 3"`
	MaxPlayers int    `json:"max_players" binding:"gt=0"`
	Password   string `json:"password"`
	Port       int    `json:"port" binding:"gte=1,lte=65535"`
	Seed       string `json:"seed"`
	WorldName  string `json:"world_name"`
}

type Mod struct {
	Id     string `json:"id" binding:"required"`
	Name   string `json:"name" binding:"required"`
	Enable bool   `json:"enable" binding:"required"`
}
