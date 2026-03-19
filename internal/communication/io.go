package communication

import (
	"bufio"
	"os"
)


func ReadLineStdin() (string, error) {
	return  bufio.NewReader(os.Stdin).ReadString('\n')
}
