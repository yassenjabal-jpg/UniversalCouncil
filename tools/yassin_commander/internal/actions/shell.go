package actions

import (
	"context"
	"fmt"
	"strings"

	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/mcpclient"
	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/policy"
)

func (r *Registry) powerShellScript(ctx context.Context, args map[string]any) (mcpclient.Result, error) {
	raw, ok := args["script_path"].(string)
	if !ok || raw == "" {
		return mcpclient.Result{IsError: true, Code: "RAW_POWERSHELL_DISABLED"}, fmt.Errorf("shell.powershell requires script_path; raw command execution is disabled")
	}
	script, err := policy.NormalizeWindowsPath(raw)
	if err != nil {
		return mcpclient.Result{IsError: true, Code: "INVALID_SCRIPT_PATH"}, fmt.Errorf("invalid script path: %w", err)
	}
	if !strings.EqualFold(pathExtension(script), ".ps1") {
		return mcpclient.Result{IsError: true, Code: "INVALID_SCRIPT_PATH"}, fmt.Errorf("only .ps1 scripts are allowed")
	}
	trusted := false
	for _, root := range r.cfg.TrustedScriptRoots {
		if policy.WindowsPathWithinRoot(script, root) {
			trusted = true
			break
		}
	}
	if !trusted {
		return mcpclient.Result{IsError: true, Code: "SCRIPT_NOT_TRUSTED"}, fmt.Errorf("script is outside trusted roots")
	}

	arguments, ok := stringSlice(args["arguments"])
	if !ok {
		return mcpclient.Result{IsError: true, Code: "INVALID_ARGS"}, fmt.Errorf("arguments must contain only strings")
	}
	command := "& " + quotePowerShell(script)
	for _, argument := range arguments {
		command += " " + quotePowerShell(argument)
	}
	out := map[string]any{"command": command}
	if timeout, ok := args["timeout"]; ok {
		out["timeout"] = timeout
	}
	return r.caller.Call(ctx, "PowerShell", out)
}

func quotePowerShell(value string) string {
	return "'" + strings.ReplaceAll(value, "'", "''") + "'"
}

func pathExtension(path string) string {
	index := strings.LastIndex(path, ".")
	slash := strings.LastIndex(path, "\\")
	if index < 0 || index < slash {
		return ""
	}
	return path[index:]
}
