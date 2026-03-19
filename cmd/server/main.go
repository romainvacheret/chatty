package main

import (
	"chatty/internal/communication"
	"syscall"
)

func main() {
	sock, err := communication.InitSocketDefault()

	if err != nil { return }

	err = communication.SetSocketReusable(sock)

	if err != nil { return }

	defer syscall.Close(sock.Fd)
	communication.ListenForClient(sock)
}
