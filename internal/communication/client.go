package communication

type ClientSender struct {
	serverSocket *SocketInfo
}

func NewClientSender(sock *SocketInfo) *ClientSender {
	return &ClientSender{ serverSocket: sock }
}

func (c *ClientSender) Send(message string) error {
	return WritePadded(c.serverSocket.Fd, []byte(message))
}

func (c *ClientSender) Listen(callback ListenCallbackFunc) error {
	return ListenForMessage(c.serverSocket.Fd, callback)
}

func ExecuteLoopClient(sender *ClientSender) error {
	for {
		line, err := ReadLineStdin()
		if err != nil { return err }

		if err := sender.Send(line); err != nil { 
			return err
		}
	}
}
