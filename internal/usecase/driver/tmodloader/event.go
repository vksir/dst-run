package tmodloader

import (
	"dst-run/pkg/process"
	"regexp"
)

func getReportPatterns() []*process.ReportPattern {
	events := []*process.ReportPattern{
		{
			// Finding ModMap...
			PatternString: `Finding ModMap`,
			Format:        "正在加载 Mod",
			Level:         "info",
		},
		{
			// Creating world
			PatternString: `Creating world`,
			Format:        "正在生成世界",
			Level:         "info",
		},
		{
			// Loading world data: 1%
			PatternString: `Loading world data: 1%`,
			Format:        "正在加载世界",
			Level:         "info",
		},
		{
			// Server started
			PatternString: `Server started`,
			Format:        "服务器启动成功",
			Level:         "warning",
			Type:          EventTypeServerActive,
		},
		{
			// Villkiss has joined.
			PatternString: `(.*) has joined\.`,
			Format:        "%s加入游戏",
			Level:         "info",
		},
		{
			// Villkiss has left.
			PatternString: `(.*) has left\.`,
			Format:        "%s离开游戏",
			Level:         "info",
		},
		{
			// <Villkiss> hello
			PatternString: `<(.*)> (.*)`,
			Format:        "%s说：%s",
			Level:         "info",
		},
	}
	for i := range events {
		events[i].Pattern = regexp.MustCompile(events[i].PatternString)
	}
	return events
}
