package dontstarvetogether

import (
	"dst-run/internal/core"
	"regexp"
)

func getReportPatterns() []*core.ReportPattern {
	events := []*core.ReportPattern{
		{
			// Shard server started
			PatternString: `Shard server started`,
			Format:        "服务器启动成功",
			Level:         "warning",
			Type:          EventTypeServerActive,
		},
		{
			//
			PatternString: `\[Join Announcement\] (.*)`,
			Format:        "%s加入游戏",
			Level:         "info",
		},
		{
			//
			PatternString: `\[Leave Announcement\] (.*)`,
			Format:        "%s离开游戏",
			Level:         "info",
		},
		{
			//
			PatternString: `\[Death Announcement\] (.*) 死于： (.*)。`,
			Format:        "%s死于：%s",
			Level:         "info",
		},
		{
			//
			PatternString: `\[Resurrect Announcement\] (.*) 复活自： (.*).`,
			Format:        "%s复活自：%s",
			Level:         "info",
		},
		{
			//
			PatternString: `\[Announcement\] (.*)`,
			Format:        "全服宣告：%s",
			Level:         "info",
		},
		{
			//
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
