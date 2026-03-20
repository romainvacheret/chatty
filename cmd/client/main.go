package main

import (
	"chatty/internal/communication"
	"chatty/internal/logger"
	"chatty/internal/tui"
	"chatty/internal/utils"
)


func main() {
	logger.InitLogger("client")

	sock, err := communication.InitSocketDefault()
	if err != nil { 
		utils.WriteErr("Impossible to initialize default socket", err)
		return
	}

	defer communication.Close(sock)

	if err := communication.Connect(sock); err != nil { 
		utils.WriteErr("Error while connecting to server", err)
		return
	}

	sender := communication.NewClientSender(sock)
	tui, err := tui.NewClientTui(sender)
	
	if err != nil { 
		utils.WriteErr("Error while initializing TUI", err)
		return
	}

	if err := tui.RunMainLoop(); err != nil {
		utils.WriteErr("Error while executing client loop", err)
		return
	}
}
