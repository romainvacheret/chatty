package utils

import (
	"fmt"
	"os"
)


func WriteErr(msg string, err error) { fmt.Fprintf(os.Stderr, "%s: %s\n", msg, err) }
