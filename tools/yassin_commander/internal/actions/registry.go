package actions

import (
	"context"
	"fmt"
	"strings"

	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/job"
	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/mcpclient"
	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/policy"
)

type Caller interface {
	ListTools(context.Context) ([]string, error)
	Call(context.Context, string, map[string]any) (mcpclient.Result, error)
}

type InteractiveProbe interface {
	InteractiveAvailable(context.Context) (bool, error)
}

type Config struct {
	TrustedScriptRoots []string
	AllowedExecutables []string
	AllowedApps        []string
}

type handler func(context.Context, map[string]any) (mcpclient.Result, error)

type Registry struct {
	caller Caller
	probe  InteractiveProbe
	cfg    Config
	table  map[string]handler
}

var requiredMCPTools = []string{
	"PowerShell",
	"FileSystem",
	"Process",
	"LaunchExecutable",
	"Screenshot",
	"Snapshot",
	"Invoke",
	"Click",
	"Type",
	"Shortcut",
	"App",
}

func NewRegistry(ctx context.Context, caller Caller, probe InteractiveProbe, cfg Config) (*Registry, error) {
	if caller == nil {
		return nil, fmt.Errorf("MCP caller is required")
	}
	if probe == nil {
		return nil, fmt.Errorf("interactive session probe is required")
	}

	tools, err := caller.ListTools(ctx)
	if err != nil {
		return nil, fmt.Errorf("discover MCP tools: %w", err)
	}
	available := make(map[string]struct{}, len(tools))
	for _, name := range tools {
		available[name] = struct{}{}
	}
	for _, required := range requiredMCPTools {
		if _, ok := available[required]; !ok {
			return nil, fmt.Errorf("missing required MCP tool %q", required)
		}
	}

	normalizedCfg, err := normalizeConfig(cfg)
	if err != nil {
		return nil, err
	}

	r := &Registry{caller: caller, probe: probe, cfg: normalizedCfg}
	r.table = map[string]handler{
		"system.status":      r.systemStatus,
		"filesystem.list":    r.filesystemList,
		"filesystem.read":    r.filesystemRead,
		"filesystem.write":   r.filesystemWrite,
		"filesystem.copy":    r.filesystemCopy,
		"filesystem.move":    r.filesystemMove,
		"process.list":       r.processList,
		"process.start":      r.processStart,
		"process.stop":       r.processStop,
		"shell.powershell":   r.powerShellScript,
		"screen.screenshot":  r.interactive("Screenshot", nil, nil),
		"ui.snapshot":        r.interactive("Snapshot", []string{"all_windows"}, nil),
		"ui.invoke":          r.interactive("Invoke", []string{"label", "automation_id", "name", "control_type", "name_match", "occurrence", "nth", "action", "value"}, nil),
		"ui.click":           r.interactive("Click", []string{"loc", "label", "automation_id", "name", "control_type", "name_match", "occurrence", "nth", "button", "clicks"}, nil),
		"ui.type":            r.interactive("Type", []string{"loc", "label", "automation_id", "name", "control_type", "name_match", "occurrence", "nth", "text", "clear", "press_enter"}, nil),
		"ui.shortcut":        r.interactive("Shortcut", []string{"shortcut"}, nil),
		"app.launch":         r.appLaunch,
		"app.switch":         r.appSwitch,
	}
	return r, nil
}

func (r *Registry) Execute(ctx context.Context, req job.Request, decision policy.Decision) (mcpclient.Result, error) {
	if !decision.Allowed {
		return mcpclient.Result{IsError: true, Code: "POLICY_DENIED"}, fmt.Errorf("policy denied %q: %s", req.Action, decision.Reason)
	}
	h, ok := r.table[req.Action]
	if !ok {
		return mcpclient.Result{IsError: true, Code: "UNKNOWN_ACTION"}, fmt.Errorf("unknown public action %q", req.Action)
	}
	if decision.NormalizedArgs == nil {
		return mcpclient.Result{IsError: true, Code: "INVALID_ARGS"}, fmt.Errorf("normalized arguments are required")
	}
	return h(ctx, decision.NormalizedArgs)
}

func normalizeConfig(cfg Config) (Config, error) {
	out := Config{
		TrustedScriptRoots: make([]string, 0, len(cfg.TrustedScriptRoots)),
		AllowedExecutables: make([]string, 0, len(cfg.AllowedExecutables)),
		AllowedApps:        make([]string, 0, len(cfg.AllowedApps)),
	}
	for _, root := range cfg.TrustedScriptRoots {
		normalized, err := policy.NormalizeWindowsPath(root)
		if err != nil {
			return Config{}, fmt.Errorf("invalid trusted script root %q: %w", root, err)
		}
		out.TrustedScriptRoots = append(out.TrustedScriptRoots, normalized)
	}
	for _, exe := range cfg.AllowedExecutables {
		normalized, err := policy.NormalizeWindowsPath(exe)
		if err != nil {
			return Config{}, fmt.Errorf("invalid allowed executable %q: %w", exe, err)
		}
		out.AllowedExecutables = append(out.AllowedExecutables, normalized)
	}
	for _, app := range cfg.AllowedApps {
		app = strings.TrimSpace(strings.ToLower(app))
		if app == "" || strings.ContainsAny(app, "\\/:
	") {
			return Config{}, fmt.Errorf("invalid allowed app %q", app)
		}
		out.AllowedApps = append(out.AllowedApps, app)
	}
	return out, nil
}

func (r *Registry) interactive(tool string, keys []string, fixed map[string]any) handler {
	return func(ctx context.Context, args map[string]any) (mcpclient.Result, error) {
		ok, err := r.probe.InteractiveAvailable(ctx)
		if err != nil {
			return mcpclient.Result{IsError: true, Code: "INTERACTIVE_SESSION_CHECK_FAILED"}, fmt.Errorf("interactive session probe: %w", err)
		}
		if !ok {
			return mcpclient.Result{IsError: true, Code: "INTERACTIVE_SESSION_UNAVAILABLE"}, nil
		}
		out := pick(args, keys...)
		for k, v := range fixed {
			out[k] = v
		}
		return r.caller.Call(ctx, tool, out)
	}
}

func pick(args map[string]any, keys ...string) map[string]any {
	out := make(map[string]any, len(keys))
	for _, key := range keys {
		if value, ok := args[key]; ok {
			out[key] = value
		}
	}
	return out
}

func containsFold(items []string, value string) bool {
	for _, item := range items {
		if strings.EqualFold(item, value) {
			return true
		}
	}
	return false
}
