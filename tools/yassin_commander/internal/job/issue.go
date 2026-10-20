package job

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"strings"
)

type issueEventEnvelope struct {
	Repository struct {
		FullName string `json:"full_name"`
	} `json:"repository"`
	Sender struct {
		Login string `json:"login"`
	} `json:"sender"`
	Issue struct {
		Number int    `json:"number"`
		Body   string `json:"body"`
		Labels []struct {
			Name string `json:"name"`
		} `json:"labels"`
	} `json:"issue"`
}

func ParseIssueEvent(eventBytes []byte) (Request, error) {
	var event issueEventEnvelope
	if err := json.Unmarshal(eventBytes, &event); err != nil {
		return Request{}, fmt.Errorf("decode issue event: %w", err)
	}
	if len(event.Issue.Body) > MaxIssueBodyBytes {
		return Request{}, errors.New("issue body exceeds maximum size")
	}

	block, err := extractSingleJSONBlock(event.Issue.Body)
	if err != nil {
		return Request{}, err
	}

	var req Request
	dec := json.NewDecoder(bytes.NewBufferString(block))
	dec.DisallowUnknownFields()
	if err := dec.Decode(&req); err != nil {
		return Request{}, fmt.Errorf("decode job payload: %w", err)
	}
	var extra any
	if err := dec.Decode(&extra); err != io.EOF {
		if err == nil {
			return Request{}, errors.New("job payload contains multiple JSON values")
		}
		return Request{}, fmt.Errorf("decode trailing job payload: %w", err)
	}

	req.Actor = event.Sender.Login
	req.Repository = event.Repository.FullName
	req.IssueNumber = event.Issue.Number
	req.Labels = make([]string, 0, len(event.Issue.Labels))
	for _, label := range event.Issue.Labels {
		req.Labels = append(req.Labels, label.Name)
	}
	return req, nil
}

func extractSingleJSONBlock(body string) (string, error) {
	lines := strings.Split(body, "\n")
	var blocks []string
	inJSON := false
	var current []string

	for _, line := range lines {
		trimmed := strings.TrimSpace(line)
		if !inJSON {
			if strings.EqualFold(trimmed, "```json") {
				inJSON = true
				current = current[:0]
			}
			continue
		}

		if trimmed == "```" {
			blocks = append(blocks, strings.Join(current, "\n"))
			inJSON = false
			current = nil
			continue
		}
		current = append(current, line)
	}

	if inJSON {
		return "", errors.New("unterminated JSON machine block")
	}
	if len(blocks) != 1 {
		return "", fmt.Errorf("expected exactly one JSON machine block, got %d", len(blocks))
	}
	if strings.TrimSpace(blocks[0]) == "" {
		return "", errors.New("JSON machine block is empty")
	}
	return blocks[0], nil
}
