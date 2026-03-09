package communication

import (
	"fmt"
	"syscall"
)

const BUFF_SIZE = 2048
const SOCK_PORT = 1234 
var SOCK_ADDR = [4]byte{127, 0, 0, 1}

type SocketInfo struct {
	Fd int
	Addr syscall.SockaddrInet4
}

func InitSocket() (*SocketInfo, error) {
	fd, err := syscall.Socket(syscall.AF_INET, syscall.SOCK_STREAM, 0)

	if err != nil {
		return nil, err
	}

	addr := syscall.SockaddrInet4{ Port: SOCK_PORT, Addr: SOCK_ADDR }

	return &SocketInfo{ Fd: fd, Addr: addr }, nil
}

func InitReusableSocket() (*SocketInfo, error) {
	sock, err := InitSocket()

	if err != nil {
		return nil, err
	}

	if err := syscall.SetsockoptInt(
		sock.Fd, 
		syscall.SOL_SOCKET,
		syscall.SO_REUSEADDR,
		1); err != nil {
		return nil, err
	}

	return sock, err
}

func read(fd int) ([]byte, error) {
	totalRead := 0
	buff := make([]byte, BUFF_SIZE)

	for totalRead < len(buff) {
		// message must be 
		nb, err := syscall.Read(fd, buff[totalRead:])
		totalRead += nb

		if err != nil { return nil, err }
	}

	return  buff, nil
}


func write(fd int, buff []byte) error {
	totalWritten := 0

	for totalWritten < len(buff) {
		nb, err := syscall.Write(fd, buff[totalWritten:])
		totalWritten += nb

		if err != nil { return err }
	}
	return nil
}


func Send(sock *SocketInfo, message []byte) error {
	err := syscall.Connect(sock.Fd, &sock.Addr)
	defer syscall.Close(sock.Fd)

	if err != nil { return err }

	return write(sock.Fd, message)
}

func Listen(sock *SocketInfo) error {
	err := syscall.Bind(sock.Fd, &sock.Addr)
	defer syscall.Close(sock.Fd)

	if err != nil { return err }

	err = syscall.Listen(sock.Fd, syscall.SOMAXCONN)

	if err != nil { return err }

	for {
		connfd, _, err := syscall.Accept(sock.Fd)

		if err != nil { return err }

		buff, err := read(connfd)

		if err != nil { return err }
		fmt.Println("Msg", string(buff))
	}
}
