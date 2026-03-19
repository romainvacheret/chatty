package communication

import (
	"bytes"
	"fmt"
	"strings"
	"syscall"
	"unicode"
)

const BUFF_SIZE = 2048
const SOCK_PORT = 1234 
var SOCK_ADDR = [4]byte{127, 0, 0, 1}

type SocketInfo struct {
	Fd int
	Addr syscall.SockaddrInet4
}

func InitSocket(port int, addr [4]byte) (*SocketInfo, error) {
	fd, err := syscall.Socket(syscall.AF_INET, syscall.SOCK_STREAM, 0)

	if err != nil {
		return nil, err
	}

	sockAddr := syscall.SockaddrInet4{ Port: port, Addr: addr }

	return &SocketInfo{ Fd: fd, Addr: sockAddr }, nil
}

func InitSocketDefault() (*SocketInfo, error) {
	return InitSocket(SOCK_PORT, SOCK_ADDR)
}

func SetSocketReusable(sock *SocketInfo) error {
	return syscall.SetsockoptInt(
		sock.Fd, 
		syscall.SOL_SOCKET,
		syscall.SO_REUSEADDR,
		1,
	);
}

func read(fd int) ([]byte, error) {
	totalRead := 0
	buff := make([]byte, BUFF_SIZE)

	for totalRead < len(buff) {
		nb, err := syscall.Read(fd, buff[totalRead:])
		totalRead += nb

		if err != nil { return nil, err }
	}

	return  buff, nil
}


func Write(fd int, buff []byte) error {
	totalWritten := 0

	for totalWritten < len(buff) {
		nb, err := syscall.Write(fd, buff[totalWritten:])
		totalWritten += nb

		if err != nil { return err }
	}
	return nil
}

func WritePadded(fd int, buff []byte) error {
	padding := bytes.Repeat([]byte(" "), BUFF_SIZE - len(buff))
	return Write(fd, append(buff, padding...))
}

func Connect(sock *SocketInfo) error {
	return syscall.Connect(sock.Fd, &sock.Addr)
}

func Close(sock *SocketInfo) error {
	return syscall.Close(sock.Fd)
}

func ListenForMessage(connfd int, callback func ([]byte)) {
	for {
		buff, err := read(connfd)

		if err != nil { return }

		// remove padding
		str := strings.TrimRightFunc(string(buff), unicode.IsSpace)

		// TODO: add indentification with names instead of fd
		fmt.Printf("--%d: %s--\n", connfd, str)
		callback(buff)
	}
}

func ListenForClient(sock *SocketInfo, connectionManager *ConnectionManager) error {
	err := syscall.Bind(sock.Fd, &sock.Addr)
	defer syscall.Close(sock.Fd)

	if err != nil { return err }

	err = syscall.Listen(sock.Fd, syscall.SOMAXCONN)

	if err != nil { return err }

	for {
		connfd, _, err := syscall.Accept(sock.Fd)
		connectionManager.AddClient(connfd)

		if err != nil { return err }

		go ListenForMessage(connfd, func(msg []byte) {
			WritePadded(connfd, []byte("ack"))
			connectionManager.WriteToClients(msg, connfd)
		})
	}
}
