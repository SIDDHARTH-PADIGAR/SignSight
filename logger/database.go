package main

import (
	"database/sql"
	"log"

	_ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./db/isl_logs.db")
	if err != nil {
		log.Fatal(err)
	}

	createTable := `
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        target_letter TEXT,
        predicted_letter TEXT,
        correct INTEGER,
        timestamp TEXT
    );
    `
	_, err = db.Exec(createTable)
	if err != nil {
		log.Fatal(err)
	}

	log.Println("Database initialized")
}

func insertLog(entry LogEntry) error {
	stmt := `INSERT INTO logs (user_id, target_letter, predicted_letter, correct, timestamp)
             VALUES (?, ?, ?, ?, ?)`
	_, err := db.Exec(stmt, entry.UserID, entry.TargetLetter, entry.PredictedLetter, entry.Correct, entry.Timestamp)
	return err
}
