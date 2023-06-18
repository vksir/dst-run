package dontstarvetogether

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

type Config struct {
	ClusterName        string   `json:"cluster_name"`
	ClusterPassword    string   `json:"cluster_password"`
	ClusterDescription string   `json:"cluster_description"`
	GameMode           string   `json:"game_mode"`
	MaxPlayers         int      `json:"max_players"`
	Pvp                bool     `json:"pvp"`
	AdminList          []string `json:"admin_list"`
	ClusterToken       string   `json:"cluster_token"`
	EnableMods         []string `json:"enable_mods"`
	ArchiveName        string   `json:"archive_name"`
}

type WorldOverrides struct {
	Master string `json:"master"`
	Caves  string `json:"caves"`
}

type ShardPath struct {
	Root              string
	WorldOverrideFile string
	ModOverrideFile   string
}
type ClusterPath struct {
	Root          string
	SettingFile   string
	AdminListFile string
	TokenFile     string

	Master ShardPath
	Caves  ShardPath
}
