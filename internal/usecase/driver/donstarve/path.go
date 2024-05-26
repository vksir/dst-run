package donstarve

import (
	"dst-run/pkg/util"
	"dst-run/pkg/workspace"
	"fmt"
	"path/filepath"
)

const (
	name = "dontstarve"
)

var programDir = filepath.Join(workspace.ProgramDir, name)
var clusterDir = filepath.Join(workspace.Home(), ".klei/DoNotStarveTogether")

var dstServPath = filepath.Join(programDir, "bin64/dontstarve_dedicated_server_nullrenderer_x64")
var ModSetupPath = filepath.Join(programDir, "mods/dedicated_server_mods_setup.lua")

type ClusterPath struct {
	Root          string
	ClusterIni    string
	AdminListFile string
	TokenFile     string

	Master ShardPath
	Caves  ShardPath
}

type ShardPath struct {
	Root              string
	WorldOverrideFile string
	ModOverrideFile   string
	ServerFile        string
}

func NewClusterPath(archiveName string) *ClusterPath {
	var cp ClusterPath

	cp.Root = filepath.Join(clusterDir, archiveName)
	cp.ClusterIni = filepath.Join(cp.Root, "cluster.ini")
	cp.AdminListFile = filepath.Join(cp.Root, "adminlist.txt")
	cp.TokenFile = filepath.Join(cp.Root, "cluster_token.txt")

	cp.Master.Root = filepath.Join(cp.Root, "Master")
	cp.Master.WorldOverrideFile = filepath.Join(cp.Master.Root, "leveldataoverride.lua")
	cp.Master.ModOverrideFile = filepath.Join(cp.Master.Root, "modoverrides.lua")
	cp.Master.ServerFile = filepath.Join(cp.Master.Root, "server.ini")

	cp.Caves.Root = filepath.Join(cp.Root, "Caves")
	cp.Caves.WorldOverrideFile = filepath.Join(cp.Caves.Root, "leveldataoverride.lua")
	cp.Caves.ModOverrideFile = filepath.Join(cp.Caves.Root, "modoverrides.lua")
	cp.Caves.ServerFile = filepath.Join(cp.Master.Root, "server.ini")

	return &cp
}

func (p *ClusterPath) Dirs() []string {
	return []string{
		p.Root, p.Master.Root, p.Caves.Root,
	}
}

func (p *ClusterPath) GetShardPath(shard string) (*ShardPath, error) {
	if shard == "Master" {
		return &p.Master, nil
	} else if shard == "Caves" {
		return &p.Caves, nil
	} else {
		return nil, fmt.Errorf("invalid shard: %s", shard)
	}
}

func init() {
	if err := util.MkDir(clusterDir); err != nil {
		panic(err)
	}
}
