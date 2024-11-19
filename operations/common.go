package operations

import "github.com/isri-pqc/topcoat/utils"

var ProtocolMessageOK = utils.ProtocolMessage{Message: utils.ProtocolMessageTypeOK}
var ProtocolMessageABORT = utils.ProtocolMessage{Message: utils.ProtocolMessageTypeABORT}
var ProtocolMessageERROR = utils.ProtocolMessage{Message: utils.ProtocolMessageTypeERROR}
var ProtocolMessageRESTART = utils.ProtocolMessage{Message: utils.ProtocolMessageTypeRESTART}
