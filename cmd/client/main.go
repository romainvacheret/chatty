package main

import (
	"chatty/internal/communication"
	"chatty/internal/utils"
)


func main() {
	sock, err := communication.InitSocketDefault()
	if err != nil { 
		utils.WriteErr("Impossible to initialize default socket", err)
		return
	}

	if err := communication.Connect(sock); err != nil { 
		utils.WriteErr("Error while connecting to server", err)
		return
	}

	sender := communication.NewClientSender(sock)

	if err := communication.ExecuteLoopClient(sender); err != nil {
		utils.WriteErr("Error while executing client loop", err)
		return
	}
	communication.Close(sock)
}
