package communication

import "fmt"

type ClientSender struct {
	serverSocket *SocketInfo
}

func NewClientSender(sock *SocketInfo) *ClientSender {
	sender := ClientSender{ serverSocket: sock }
	go sender.Listen()

	return &sender
}

func (c *ClientSender) Send(message string) error {
	// buffer := []byte(message)
	// padding := bytes.Repeat([]byte(" "), BUFF_SIZE - len(buffer))
	// buffer = append(buffer, padding...)
	//
	// return Write(c.serverSocket.Fd, buffer)
	return WritePadded(c.serverSocket.Fd, []byte(message))
}

func (c *ClientSender) Listen() {
	ListenForMessage(c.serverSocket.Fd, func() {} )
}

func ExecuteLoopClient(sender *ClientSender) {
	for {
		line, err := ReadLineStdin()

		if err != nil { return }

		err = sender.Send(line)

		if err != nil { 
			fmt.Println(err)
			return
		}
	}
}
