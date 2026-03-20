package main

import (
	"chatty/internal/communication"
	"chatty/internal/logger"
	"chatty/internal/utils"
)


func main() {
	logger.InitLogger("server")

	sock, err := communication.InitSocketDefault()
	if err != nil { 
		utils.WriteErr("Impossible to initialize default socket", err)
		return
	}

	
	if err := communication.SetSocketReusable(sock); err != nil { 
		utils.WriteErr("Error while changing socket status", err)
		return
	}

	defer communication.Close(sock)

	if err := communication.ListenForClient(sock, communication.NewConnectionManager()); err != nil { 
		utils.WriteErr("Error while listening to new clients", err)
		return
	}
}
