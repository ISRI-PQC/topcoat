package utils

type ProtocolMessage struct {
	Message string
}

const (
	ProtocolMessageTypeOK      = "OK"
	ProtocolMessageTypeABORT   = "ABORT"
	ProtocolMessageTypeRESTART = "RESTART"
	ProtocolMessageTypeERROR   = "ERROR"
)

type Comms interface {
	Send(message any)
	Get() any
}

func checkReturnValue(data any) any {
	ret := data

	switch t := ret.(type) {
	case ProtocolMessage:
		if t.Message == ProtocolMessageTypeABORT || t.Message == ProtocolMessageTypeERROR {
			panic("The other side send " + t.Message)
		} else {
			return t
		}
	default:
		return ret
	}
}

type ChanComms struct {
	ToOtherParty   chan any
	FromOtherParty chan any
}

func (c ChanComms) Send(message any) {
	c.ToOtherParty <- message
}

func (c ChanComms) Get() any {
	return checkReturnValue(<-c.FromOtherParty)
}