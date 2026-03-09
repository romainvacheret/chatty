package main

import (
	"chatty/internal/communication"
	"syscall"
)

func main() {
	sock, err := communication.InitReusableSocket()
	defer syscall.Close(sock.Fd)
	if err != nil { return }
	communication.Listen(sock)
}
