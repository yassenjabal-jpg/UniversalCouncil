package actions

import (
	"context"
	"fmt"

	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/mcpclient"
	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/policy"
)

func (r *Registry) processList(ctx context.Context, args map[string]any) (mcpclient.Result, error) {
	out := map[string]any{"mode": "list"}
	for _, key := range []string{"name", "sort_by", "limit"} {
		if value, ok := args[key]; ok {
			out[key] = value
		}
	}
	return r.caller.Call(ctx, "Process", out)
}

func (r *Registry) processStop(ctx context.Context, args map[string]any) (mcpclient.Result, error) {
	out := map[string]any{"mode": "kill"}
	if value, ok := args["pid"]; ok {
		out["pid"] = value
	}
	if value, ok := args["name"]; ok {
		out["name"] = value
	}
	if _, pid := out["pid"]; !pid {
		if name, ok := out["name"].(string); !ok || name == "" {
			return mcpclient.Result{IsError: true, Code: "INVALID_ARGS"}, fmt.Errorf("process.stop requires pid or name")
		}
	}
	return r.caller.Call(ctx, "Process", out)
}

func (r *Registry) processStart(ctx context.Context, args map[string]any) (mcpclient.Result, error) {
	raw, ok := args["executable"].(string)
	if !ok || raw == "" {
		return mcpclient.Result{IsError: true, Code: "INVALID_ARGS"}, fmt.Errorf("process.start requires executable")
	}
	exe, err := policy.NormalizeWindowsPath(raw)
	if err != nil {
		return mcpclient.Result{IsError: true, Code: "INVALID_ARGS"}, fmt.Errorf("invalid executable: %w", err)
	}
	if !containsFold(r.cfg.AllowedExecutables, exe) {
		return mcpclient.Result{IsError: true, Code: "EXECUTABLE_NOT_ALLOWED"}, fmt.Errorf("executable is not allowlisted")
	}
	if cwd, ok := args["cwd"].(string); ok && cwd != "" {
		return mcpclient.Result{IsError: true, Code: "CWD_NOT_ALLOWED"}, fmt.Errorf("custom cwd is disabled in v1")
	}

	out := map[string]any{"executable": exe}
	if value, ok := stringSlice(args["args"]); ok && len(value) > 0 {
		out["args"] = value
	}
	return r.caller.Call(ctx, "LaunchExecutable", out)
}

func stringSlice(value any) ([]string, bool) {
	switch values := value.(type) {
	case []string:
		return append([]string(nil), values...), true
	case []any:
		out := make([]string, 0, len(values))
		for _, value := range values {
			text, ok := value.(string)
			if !ok {
				return nil, false
			}
			out = append(out, text)
		}
		return out, true
	case nil:
		return nil, true
	default:
		return nil, false
	}
}
