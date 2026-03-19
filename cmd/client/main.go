package main

import (
	"chatty/internal/communication"
)


func main() {
	sock, err := communication.InitSocketDefault()
	if err != nil { return }

	err = communication.Connect(sock)
	if err != nil { return }

	sender := communication.NewClientSender(sock)

	communication.ExecuteLoopClient(sender)
	communication.Close(sock)
}
