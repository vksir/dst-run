package entity

type DontStarveKv struct {
	Model

	Key   string `gorm:"uniqueIndex"`
	Value string
}

type DontStarveAdmin struct {
	Model

	Remark string
	KleiId string `gorm:"unique"`
	Enable bool
}

type DontStarveCluster struct {
	Model

	ClusterName        string
	ClusterPassword    string
	ClusterDescription string
	MaxPlayers         string
	Pvp                string

	Worlds []DontStarveWorld        `gorm:"foreignKey:DontStarveClusterId"`
	Mods   []DontStarveModInCluster `gorm:"foreignKey:DontStarveClusterId"`
}

type DontStarveWorld struct {
	Model

	Type                string
	ServerConfig        string
	WorldOverride       string
	DontStarveClusterId string `gorm:"<-:create"`
}

type DontStarveModInCluster struct {
	Model

	CurrentConfig       string
	DontStarveClusterId string `gorm:"<-:create"`

	ModId string        `gorm:"<-:create"`
	Mod   DontStarveMod `gorm:"foreignKey:ModId"`
}

type DontStarveMod struct {
	Model

	ModId  string `gorm:"unique"`
	Name   string
	Remark string
	Config string
}

type DontStarveEvent struct {
	Model

	Type string
	Code int
	Msg  string
}
