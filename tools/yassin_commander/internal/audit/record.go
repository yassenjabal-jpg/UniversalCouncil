package audit

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"time"
)

type Record struct {
	RequestID     string    `json:"request_id"`
	IssueNumber   int       `json:"issue_number"`
	Actor         string    `json:"actor"`
	Action        string    `json:"action"`
	ArgsDigest    string    `json:"args_digest"`
	PolicyVerdict string    `json:"policy_verdict"`
	StartedAt     time.Time `json:"started_at"`
	EndedAt       time.Time `json:"ended_at"`
	Status        string    `json:"status"`
	ResultDigest  string    `json:"result_digest"`
	PreviousHash  string    `json:"previous_hash"`
	EntryHash     string    `json:"entry_hash"`
}

func MarshalLine(record Record) ([]byte, error) {
	return json.Marshal(record)
}

func hashRecord(record Record) (string, error) {
	record.EntryHash = ""
	payload, err := json.Marshal(record)
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256(payload)
	return hex.EncodeToString(sum[:]), nil
}
