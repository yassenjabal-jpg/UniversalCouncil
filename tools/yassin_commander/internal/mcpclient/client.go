package mcpclient

import (
	"context"
	"errors"
	"fmt"
	"os/exec"
	"time"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

type Config struct {
	Executable   string
	Args         []string
	WorkDir      string
	Env          []string
	Timeout      time.Duration
	MaxTextBytes int
	MaxArtifacts int
}

type Artifact struct {
	Kind     string
	MIMEType string
	Data     []byte
}

type Result struct {
	Text      string
	Files     []Artifact
	IsError   bool
	Code      string
	Truncated bool
}

type Client struct {
	cfg Config
}

func New(cfg Config) *Client {
	if cfg.Timeout <= 0 {
		cfg.Timeout = 30 * time.Second
	}
	if cfg.MaxTextBytes <= 0 {
		cfg.MaxTextBytes = 64 * 1024
	}
	if cfg.MaxArtifacts <= 0 {
		cfg.MaxArtifacts = 8
	}
	return &Client{cfg: cfg}
}

func (c *Client) Call(ctx context.Context, tool string, args map[string]any) (Result, error) {
	if c.cfg.Executable == "" {
		return Result{Code: "CONFIG_ERROR", IsError: true}, errors.New("MCP executable is required")
	}
	if tool == "" {
		return Result{Code: "CONFIG_ERROR", IsError: true}, errors.New("MCP tool name is required")
	}

	callCtx, cancel := context.WithTimeout(ctx, c.cfg.Timeout)
	defer cancel()

	cmd := exec.CommandContext(callCtx, c.cfg.Executable, c.cfg.Args...)
	cmd.Dir = c.cfg.WorkDir
	// A non-nil Env prevents exec.Cmd from inheriting the parent environment.
	cmd.Env = append([]string{}, c.cfg.Env...)

	transport := &mcp.CommandTransport{Command: cmd}
	client := mcp.NewClient(&mcp.Implementation{Name: "yassin-commander-bridge", Version: "v1"}, nil)
	session, err := client.Connect(callCtx, transport, nil)
	if err != nil {
		return classifyCallError(callCtx, err)
	}
	defer session.Close()

	res, err := session.CallTool(callCtx, &mcp.CallToolParams{
		Name:      tool,
		Arguments: args,
	})
	if err != nil {
		return classifyCallError(callCtx, err)
	}

	out := translateResult(res, c.cfg.MaxTextBytes, c.cfg.MaxArtifacts)
	if res.IsError {
		out.IsError = true
		out.Code = "MCP_TOOL_ERROR"
	}
	return out, nil
}

func classifyCallError(ctx context.Context, err error) (Result, error) {
	if errors.Is(ctx.Err(), context.DeadlineExceeded) || errors.Is(err, context.DeadlineExceeded) {
		return Result{IsError: true, Code: "TIMEOUT"}, context.DeadlineExceeded
	}
	return Result{IsError: true, Code: "MCP_PROTOCOL_ERROR"}, fmt.Errorf("MCP call failed: %w", err)
}
