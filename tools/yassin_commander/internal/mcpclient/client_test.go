package mcpclient

import (
	"context"
	"errors"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

type helperArgs struct {
	Mode string `json:"mode"`
	Text string `json:"text,omitempty"`
}

func helperTool(ctx context.Context, _ *mcp.CallToolRequest, args helperArgs) (*mcp.CallToolResult, any, error) {
	switch args.Mode {
	case "text":
		return &mcp.CallToolResult{Content: []mcp.Content{&mcp.TextContent{Text: args.Text}}}, nil, nil
	case "env":
		return &mcp.CallToolResult{Content: []mcp.Content{&mcp.TextContent{Text: os.Getenv("YC_ALLOWED") + "|" + os.Getenv("SHOULD_NOT_LEAK")}}}, nil, nil
	case "tool-error":
		return &mcp.CallToolResult{Content: []mcp.Content{&mcp.TextContent{Text: "boom"}}, IsError: true}, nil, nil
	case "image":
		return &mcp.CallToolResult{Content: []mcp.Content{&mcp.ImageContent{Data: []byte("png-bytes"), MIMEType: "image/png"}}}, nil, nil
	case "resource":
		return &mcp.CallToolResult{Content: []mcp.Content{&mcp.ResourceLink{URI: "file:///tmp/example", Name: "example"}}}, nil, nil
	case "sleep":
		select {
		case <-ctx.Done():
			return nil, nil, ctx.Err()
		case <-time.After(2 * time.Second):
			return &mcp.CallToolResult{Content: []mcp.Content{&mcp.TextContent{Text: "late"}}}, nil, nil
		}
	default:
		return &mcp.CallToolResult{Content: []mcp.Content{&mcp.TextContent{Text: "unknown mode"}}}, nil, nil
	}
}

func TestYCServerHelper(t *testing.T) {
	if os.Getenv("GO_WANT_YC_HELPER") != "1" {
		return
	}
	server := mcp.NewServer(&mcp.Implementation{Name: "yc-test-server", Version: "v1"}, nil)
	mcp.AddTool(server, &mcp.Tool{Name: "probe", Description: "test probe"}, helperTool)
	if err := server.Run(context.Background(), &mcp.StdioTransport{}); err != nil {
		os.Exit(2)
	}
	os.Exit(0)
}

func helperConfig(t *testing.T) Config {
	t.Helper()
	exe, err := filepath.Abs(os.Args[0])
	if err != nil {
		t.Fatal(err)
	}
	return Config{
		Executable:   exe,
		Args:         []string{"-test.run=TestYCServerHelper"},
		Env:          []string{"GO_WANT_YC_HELPER=1", "YC_ALLOWED=yes"},
		Timeout:      time.Second,
		MaxTextBytes: 1024,
		MaxArtifacts: 4,
	}
}

func TestCallConnectsOverCommandTransportAndReturnsText(t *testing.T) {
	client := New(helperConfig(t))
	result, err := client.Call(context.Background(), "probe", map[string]any{"mode": "text", "text": "hello"})
	if err != nil {
		t.Fatalf("Call: %v", err)
	}
	if result.IsError || result.Text != "hello" {
		t.Fatalf("unexpected result: %#v", result)
	}
}

func TestCallDoesNotInheritParentSecrets(t *testing.T) {
	t.Setenv("SHOULD_NOT_LEAK", "parent-secret")
	client := New(helperConfig(t))
	result, err := client.Call(context.Background(), "probe", map[string]any{"mode": "env"})
	if err != nil {
		t.Fatalf("Call: %v", err)
	}
	if result.Text != "yes|" {
		t.Fatalf("child environment leaked or allowed env missing: %q", result.Text)
	}
}

func TestCallTimesOutAndClosesChild(t *testing.T) {
	cfg := helperConfig(t)
	cfg.Timeout = 50 * time.Millisecond
	client := New(cfg)

	start := time.Now()
	result, err := client.Call(context.Background(), "probe", map[string]any{"mode": "sleep"})
	if err == nil {
		t.Fatal("expected timeout error")
	}
	if !errors.Is(err, context.DeadlineExceeded) {
		t.Fatalf("error = %v, want deadline exceeded", err)
	}
	if result.Code != "TIMEOUT" {
		t.Fatalf("code = %q, want TIMEOUT", result.Code)
	}
	if time.Since(start) > time.Second {
		t.Fatalf("timeout did not stop promptly")
	}
}

func TestCallMapsToolErrorWithoutProtocolFailure(t *testing.T) {
	client := New(helperConfig(t))
	result, err := client.Call(context.Background(), "probe", map[string]any{"mode": "tool-error"})
	if err != nil {
		t.Fatalf("Call protocol error: %v", err)
	}
	if !result.IsError || result.Code != "MCP_TOOL_ERROR" || result.Text != "boom" {
		t.Fatalf("unexpected result: %#v", result)
	}
}

func TestCallCollectsImageArtifact(t *testing.T) {
	client := New(helperConfig(t))
	result, err := client.Call(context.Background(), "probe", map[string]any{"mode": "image"})
	if err != nil {
		t.Fatalf("Call: %v", err)
	}
	if len(result.Files) != 1 {
		t.Fatalf("artifact count = %d, want 1", len(result.Files))
	}
	if result.Files[0].MIMEType != "image/png" || string(result.Files[0].Data) != "png-bytes" {
		t.Fatalf("unexpected artifact: %#v", result.Files[0])
	}
}

func TestCallIgnoresUnsupportedContentWithoutPanic(t *testing.T) {
	client := New(helperConfig(t))
	result, err := client.Call(context.Background(), "probe", map[string]any{"mode": "resource"})
	if err != nil {
		t.Fatalf("Call: %v", err)
	}
	if result.IsError {
		t.Fatalf("unexpected tool error: %#v", result)
	}
}

func TestCallCapsTextOutput(t *testing.T) {
	cfg := helperConfig(t)
	cfg.MaxTextBytes = 5
	client := New(cfg)
	result, err := client.Call(context.Background(), "probe", map[string]any{"mode": "text", "text": "123456789"})
	if err != nil {
		t.Fatalf("Call: %v", err)
	}
	if result.Text != "12345" || !result.Truncated {
		t.Fatalf("unexpected capped result: %#v", result)
	}
}
