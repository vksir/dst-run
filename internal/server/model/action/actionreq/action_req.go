package actionreq

type Params struct {
	Action string `uri:"action" binding:"required"`
}
