package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", HelloServer)
    fmt.Println("Auth API server running at http://localhost:8081/\nClick the URL to test the welcome message.")
    http.ListenAndServe(":8081", nil)
}

func HelloServer(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello at Auth!")
}


// Hello world example from https://yourbasic.org/golang/http-server-example/