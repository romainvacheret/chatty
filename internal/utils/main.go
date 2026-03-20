package utils

import (
	"fmt"
	"os"
	"strings"
	"unicode"
)


func WriteErr(msg string, err error) {
	fmt.Fprintf(os.Stderr, "%s: %s\n", msg, err)
}

func RemovePadding(buff []byte) string {
	return strings.TrimRightFunc(string(buff), unicode.IsSpace) 
}

