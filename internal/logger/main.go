package logger

import (
	"chatty/internal/utils"
	"fmt"
	"log"
	"os"
)


var Logger *log.Logger

func InitLogger(name string) {
	file, err := os.OpenFile(fmt.Sprintf("%s.log", name), os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)

	if err != nil {
		utils.WriteErr("Error while initializing logger", err)
		return
	}

	Logger = log.New(file, "DEBUG: ", log.LstdFlags|log.Lshortfile)
}
