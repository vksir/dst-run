package gameresp

type Players struct {
	Players []string `json:"players"`
}

type Events struct {
	Events []Event `json:"events"`
}

type Event struct {
	Level string `json:"level"`
	Time  int64  `json:"time"`
	Msg   string `json:"msg"`
	Type  string `json:"type"`
}
