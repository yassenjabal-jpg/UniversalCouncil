package job

import (
	"encoding/json"
	"strings"
	"testing"
)

func issueEvent(body string) []byte {
	event := map[string]any{
		"repository": map[string]any{"full_name": "yassenjabal-jpg/YASSIN-Commander-Control"},
		"sender":     map[string]any{"login": "yassenjabal-jpg"},
		"issue": map[string]any{
			"number": 42,
			"body":   body,
			"labels": []map[string]any{{"name": "yc-job"}},
		},
	}
	data, _ := json.Marshal(event)
	return data
}

func validBody(extra string) string {
	return "request\n\n```json\n" +
		`{"version":1,"target":"YASSIN","action":"filesystem.write","args":{"path":"C:\\\\YC-Sandbox\\\\a.txt","content":"` + extra + `"},"risk":"low","request_id":"yc-42"}` +
		"\n```\n"
}

func TestParseIssueEventAcceptsOneMachineBlockAndMetadata(t *testing.T) {
	req, err := ParseIssueEvent(issueEvent(validBody("hello")))
	if err != nil {
		t.Fatalf("ParseIssueEvent() error = %v", err)
	}
	if req.Version != 1 || req.Target != "YASSIN" || req.Action != "filesystem.write" || req.RequestID != "yc-42" {
		t.Fatalf("unexpected request: %#v", req)
	}
	if req.Actor != "yassenjabal-jpg" || req.Repository != "yassenjabal-jpg/YASSIN-Commander-Control" || req.IssueNumber != 42 {
		t.Fatalf("unexpected source metadata: %#v", req)
	}
	if len(req.Labels) != 1 || req.Labels[0] != "yc-job" {
		t.Fatalf("unexpected labels: %#v", req.Labels)
	}
}

func TestParseIssueEventTreatsWorkflowExpressionAsData(t *testing.T) {
	payload := "${{ github.token }}; Write-Host PWNED"
	req, err := ParseIssueEvent(issueEvent(validBody(payload)))
	if err != nil {
		t.Fatalf("ParseIssueEvent() error = %v", err)
	}
	if got := req.Args["content"]; got != payload {
		t.Fatalf("content changed: got %#v want %#v", got, payload)
	}
}

func TestParseIssueEventRejectsDuplicateMachineBlocks(t *testing.T) {
	body := validBody("one") + "\n" + validBody("two")
	if _, err := ParseIssueEvent(issueEvent(body)); err == nil {
		t.Fatal("expected duplicate machine blocks to be rejected")
	}
}

func TestParseIssueEventRejectsMalformedJSON(t *testing.T) {
	body := "```json\n{not-json}\n```"
	if _, err := ParseIssueEvent(issueEvent(body)); err == nil {
		t.Fatal("expected malformed JSON to be rejected")
	}
}

func TestParseIssueEventRejectsUnknownTopLevelField(t *testing.T) {
	body := "```json\n" +
		`{"version":1,"target":"YASSIN","action":"system.status","args":{},"risk":"low","request_id":"yc-1","raw_shell":"whoami"}` +
		"\n```"
	if _, err := ParseIssueEvent(issueEvent(body)); err == nil {
		t.Fatal("expected unknown request field to be rejected")
	}
}

func TestParseIssueEventRejectsOversizedBody(t *testing.T) {
	body := strings.Repeat("x", MaxIssueBodyBytes+1)
	if _, err := ParseIssueEvent(issueEvent(body)); err == nil {
		t.Fatal("expected oversized body to be rejected")
	}
}

func TestValidateAcceptsRegisteredV1Request(t *testing.T) {
	req, err := ParseIssueEvent(issueEvent("```json\n" +
		`{"version":1,"target":"YASSIN","action":"system.status","args":{},"risk":"low","request_id":"yc-1"}` +
		"\n```"))
	if err != nil {
		t.Fatalf("ParseIssueEvent() error = %v", err)
	}
	cfg := ValidationConfig{RegisteredActions: map[string]struct{}{"system.status": {}}}
	if err := Validate(req, cfg); err != nil {
		t.Fatalf("Validate() error = %v", err)
	}
}

func TestValidateFailsClosed(t *testing.T) {
	base := Request{
		Version:   1,
		Target:    "YASSIN",
		Action:    "system.status",
		Args:      map[string]any{},
		Risk:      "low",
		RequestID: "yc-1",
	}

	tests := []struct {
		name string
		edit func(*Request)
	}{
		{"unknown version", func(r *Request) { r.Version = 2 }},
		{"wrong target", func(r *Request) { r.Target = "OTHER" }},
		{"empty request id", func(r *Request) { r.RequestID = "" }},
		{"unknown action", func(r *Request) { r.Action = "shell.raw" }},
		{"nil args", func(r *Request) { r.Args = nil }},
	}
	cfg := ValidationConfig{RegisteredActions: map[string]struct{}{"system.status": {}}}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := base
			req.Args = map[string]any{}
			tt.edit(&req)
			if err := Validate(req, cfg); err == nil {
				t.Fatalf("expected validation error for %s", tt.name)
			}
		})
	}
}
