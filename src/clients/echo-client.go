package main

import (
	"fmt"

	"github.com/cocaine/cocaine-framework-go/cocaine"
)

func main() {
	service, err := cocaine.NewService("echo")
	if err != nil {
		fmt.Printf("Unable to create service: %s\n", err)
		return
	}

	res, isOpened := <-service.Call("enqueue", "ping", "Hello, World!!!")
	if !isOpened {
		fmt.Println("Stream closed")
		return
	}

	if res.Err() != nil {
		fmt.Printf("Calling error: %s\n", res.Err())
		return
	}

	var result string
	err = res.Extract(&result)
	if err != nil {
		fmt.Printf("Extraction error: %s", err)
		return
	}

	fmt.Println(result)
}
