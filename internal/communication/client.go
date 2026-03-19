package communication

type ClientSender struct {
	serverSocket *SocketInfo
}

func NewClientSender(sock *SocketInfo) *ClientSender {
	sender := ClientSender{ serverSocket: sock }
	go sender.Listen()

	return &sender
}

func (c *ClientSender) Send(message string) error {
	return WritePadded(c.serverSocket.Fd, []byte(message))
}

func (c *ClientSender) Listen() {
	ListenForMessage(c.serverSocket.Fd, func([]byte) {} )
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
