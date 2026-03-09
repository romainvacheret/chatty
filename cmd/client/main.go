package main

import (
	"bytes"
	"chatty/internal/communication"
	"syscall"
)


func main() {
	sock, err := communication.InitSocket()
	defer syscall.Close(sock.Fd)
	buffer := []byte("client message")
	length := len(buffer)
	padding := bytes.Repeat([]byte(" "), communication.BUFF_SIZE - length)
	buffer = append(buffer, padding...)

	if err != nil { return }

	communication.Send(sock, buffer)
}
