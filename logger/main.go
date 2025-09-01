package main

import (
	"log"
	"net/http"
)

func main() {
	initDB()

	http.HandleFunc("/log", LogHandler)
	log.Println("Server running at :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
