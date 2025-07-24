package main

import (
	"encoding/json"
	"log"
	"net/http"
)

type LogEntry struct {
	UserID          string `json:"user_id"`
	TargetLetter    string `json:"target_letter"`
	PredictedLetter string `json:"predicted_letter"`
	Correct         bool   `json:"correct"`
	Timestamp       string `json:"timestamp"`
}

func LogHandler(w http.ResponseWriter, r *http.Request) {
	var logEntry LogEntry

	err := json.NewDecoder(r.Body).Decode(&logEntry)
	if err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		log.Println("[ERROR] JSON Decode failed:", err)
		return
	}

	// Convert bool to int (1 for true, 0 for false)
	correctInt := 0
	if logEntry.Correct {
		correctInt = 1
	}

	_, err = db.Exec(`
		INSERT INTO logs (user_id, target_letter, predicted_letter, correct, timestamp)
		VALUES (?, ?, ?, ?, ?)`,
		logEntry.UserID, logEntry.TargetLetter, logEntry.PredictedLetter, correctInt, logEntry.Timestamp,
	)

	if err != nil {
		http.Error(w, "Database error", http.StatusInternalServerError)
		log.Println("[DB ERROR]", err)
		return
	}

	log.Printf("[LOGGED] user: %s | target: %s | predicted: %s | correct: %v\n",
		logEntry.UserID, logEntry.TargetLetter, logEntry.PredictedLetter, logEntry.Correct,
	)

	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
}
