package actions

import (
	"context"
	"errors"
	"reflect"
	"strings"
	"testing"

	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/job"
	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/mcpclient"
	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/policy"
)

type callRecord struct {
	tool string
	args map[string]any
}

type fakeCaller struct {
	tools []string
	calls []callRecord
	err   error
}

func (f *fakeCaller) ListTools(context.Context) ([]string, error) {
	return append([]string(nil), f.tools...), f.err
}

func (f *fakeCaller) Call(_ context.Context, tool string, args map[string]any) (mcpclient.Result, error) {
	copyArgs := make(map[string]any, len(args))
	for k, v := range args {
		copyArgs[k] = v
	}
	f.calls = append(f.calls, callRecord{tool: tool, args: copyArgs})
	return mcpclient.Result{Text: "ok"}, f.err
}

type fakeProbe struct {
	available bool
	err       error
}

func (p fakeProbe) InteractiveAvailable(context.Context) (bool, error) {
	return p.available, p.err
}

func allUpstreamTools() []string {
	return []string{
		"PowerShell", "FileSystem", "Process", "LaunchExecutable",
		"Screenshot", "Snapshot", "Invoke", "Click", "Type", "Shortcut", "App",
	}
}

func newTestRegistry(t *testing.T, probe fakeProbe) (*Registry, *fakeCaller) {
	t.Helper()
	caller := &fakeCaller{tools: allUpstreamTools()}
	reg, err := NewRegistry(context.Background(), caller, probe, Config{
		TrustedScriptRoots: []string{`C:\YASSINCommander\scripts`},
		AllowedExecutables: []string{`C:\Windows\System32\notepad.exe`},
		AllowedApps:        []string{"notepad", "msedge"},
	})
	if err != nil {
		t.Fatalf("NewRegistry: %v", err)
	}
	return reg, caller
}

func allow(args map[string]any) policy.Decision {
	return policy.Decision{Allowed: true, Reason: "allowed", NormalizedArgs: args}
}

func req(action string) job.Request {
	return job.Request{Version: 1, Target: "YASSIN", Action: action, RequestID: "yc-action-test"}
}

func lastCall(t *testing.T, caller *fakeCaller) callRecord {
	t.Helper()
	if len(caller.calls) == 0 {
		t.Fatal("expected MCP call")
	}
	return caller.calls[len(caller.calls)-1]
}

func TestNewRegistryFailsClosedWhenRequiredUpstreamToolMissing(t *testing.T) {
	caller := &fakeCaller{tools: []string{"FileSystem"}}
	_, err := NewRegistry(context.Background(), caller, fakeProbe{available: true}, Config{})
	if err == nil || !strings.Contains(err.Error(), "missing required MCP tool") {
		t.Fatalf("expected missing tool error, got %v", err)
	}
}

func TestRegistryRejectsDeniedDecisionAndUnknownAction(t *testing.T) {
	reg, caller := newTestRegistry(t, fakeProbe{available: true})

	if _, err := reg.Execute(context.Background(), req("filesystem.read"), policy.Decision{Allowed: false, Reason: "no"}); err == nil {
		t.Fatal("expected denied policy decision to fail")
	}
	if _, err := reg.Execute(context.Background(), req("mcp.raw"), allow(map[string]any{})); err == nil {
		t.Fatal("expected unknown public action to fail")
	}
	if len(caller.calls) != 0 {
		t.Fatalf("unexpected MCP calls: %#v", caller.calls)
	}
}

func TestFilesystemMappingsAreFixed(t *testing.T) {
	tests := []struct {
		action string
		args   map[string]any
		want   map[string]any
	}{
		{"filesystem.list", map[string]any{"path": `C:\YC-Sandbox`}, map[string]any{"mode": "list", "path": `C:\YC-Sandbox`}},
		{"filesystem.read", map[string]any{"path": `C:\YC-Sandbox\a.txt`}, map[string]any{"mode": "read", "path": `C:\YC-Sandbox\a.txt`}},
		{"filesystem.write", map[string]any{"path": `C:\YC-Sandbox\a.txt`, "content": "hello", "append": true}, map[string]any{"mode": "write", "path": `C:\YC-Sandbox\a.txt`, "content": "hello", "append": true}},
		{"filesystem.copy", map[string]any{"source": `C:\YC-Sandbox\a.txt`, "destination": `C:\YC-Sandbox\b.txt`}, map[string]any{"mode": "copy", "path": `C:\YC-Sandbox\a.txt`, "destination": `C:\YC-Sandbox\b.txt`}},
		{"filesystem.move", map[string]any{"source": `C:\YC-Sandbox\a.txt`, "destination": `C:\YC-Sandbox\b.txt`}, map[string]any{"mode": "move", "path": `C:\YC-Sandbox\a.txt`, "destination": `C:\YC-Sandbox\b.txt`}},
	}
	for _, tt := range tests {
		t.Run(tt.action, func(t *testing.T) {
			reg, caller := newTestRegistry(t, fakeProbe{available: true})
			if _, err := reg.Execute(context.Background(), req(tt.action), allow(tt.args)); err != nil {
				t.Fatalf("Execute: %v", err)
			}
			got := lastCall(t, caller)
			if got.tool != "FileSystem" || !reflect.DeepEqual(got.args, tt.want) {
				t.Fatalf("call = %#v, want FileSystem %#v", got, tt.want)
			}
		})
	}
}

func TestSystemStatusUsesFixedCommandNotIssueCommand(t *testing.T) {
	reg, caller := newTestRegistry(t, fakeProbe{available: true})
	args := map[string]any{"command": "Remove-Item C:\\* -Recurse -Force"}
	if _, err := reg.Execute(context.Background(), req("system.status"), allow(args)); err != nil {
		t.Fatalf("Execute: %v", err)
	}
	got := lastCall(t, caller)
	if got.tool != "PowerShell" {
		t.Fatalf("tool = %q", got.tool)
	}
	command, _ := got.args["command"].(string)
	if strings.Contains(command, "Remove-Item") || !strings.Contains(command, "[Environment]::MachineName") {
		t.Fatalf("unsafe/non-fixed status command: %q", command)
	}
}

func TestProcessMappingsUseProcessAndLaunchExecutable(t *testing.T) {
	reg, caller := newTestRegistry(t, fakeProbe{available: true})

	if _, err := reg.Execute(context.Background(), req("process.list"), allow(map[string]any{"name": "notepad", "limit": 5})); err != nil {
		t.Fatal(err)
	}
	if got := lastCall(t, caller); got.tool != "Process" || got.args["mode"] != "list" {
		t.Fatalf("process.list call = %#v", got)
	}

	if _, err := reg.Execute(context.Background(), req("process.stop"), allow(map[string]any{"pid": 123})); err != nil {
		t.Fatal(err)
	}
	if got := lastCall(t, caller); got.tool != "Process" || got.args["mode"] != "kill" || got.args["pid"] != 123 {
		t.Fatalf("process.stop call = %#v", got)
	}

	if _, err := reg.Execute(context.Background(), req("process.start"), allow(map[string]any{
		"executable": `C:\Windows\System32\notepad.exe`,
		"args":       []any{"C:\\YC-Sandbox\\a.txt"},
	})); err != nil {
		t.Fatal(err)
	}
	if got := lastCall(t, caller); got.tool != "LaunchExecutable" || got.args["executable"] != `C:\Windows\System32\notepad.exe` {
		t.Fatalf("process.start call = %#v", got)
	}
}

func TestProcessStartRejectsExecutableOutsideAllowlist(t *testing.T) {
	reg, caller := newTestRegistry(t, fakeProbe{available: true})
	_, err := reg.Execute(context.Background(), req("process.start"), allow(map[string]any{
		"executable": `C:\Windows\System32\cmd.exe`,
		"args":       []any{"/c", "whoami"},
	}))
	if err == nil {
		t.Fatal("expected executable outside allowlist to be rejected")
	}
	if len(caller.calls) != 0 {
		t.Fatalf("unexpected call: %#v", caller.calls)
	}
}

func TestPowerShellRejectsRawCommandAndBuildsQuotedTrustedScriptInvocation(t *testing.T) {
	reg, caller := newTestRegistry(t, fakeProbe{available: true})

	if _, err := reg.Execute(context.Background(), req("shell.powershell"), allow(map[string]any{
		"command": "Get-ChildItem Env:",
	})); err == nil {
		t.Fatal("expected raw command to be rejected")
	}

	if _, err := reg.Execute(context.Background(), req("shell.powershell"), allow(map[string]any{
		"script_path": `C:\YASSINCommander\scripts\health.ps1`,
		"arguments":   []any{"alpha", "O'Brien"},
		"timeout":     20,
	})); err != nil {
		t.Fatalf("trusted script: %v", err)
	}
	got := lastCall(t, caller)
	if got.tool != "PowerShell" {
		t.Fatalf("tool = %q", got.tool)
	}
	command, _ := got.args["command"].(string)
	if command != `& 'C:\YASSINCommander\scripts\health.ps1' 'alpha' 'O''Brien'` {
		t.Fatalf("command = %q", command)
	}
	if got.args["timeout"] != 20 {
		t.Fatalf("timeout = %#v", got.args["timeout"])
	}
}

func TestPowerShellRejectsTraversalWrongExtensionAndOutsideRoot(t *testing.T) {
	reg, caller := newTestRegistry(t, fakeProbe{available: true})
	for _, path := range []string{
		`C:\YASSINCommander\scripts\..\evil.ps1`,
		`C:\YASSINCommander\scripts\evil.cmd`,
		`C:\Outside\evil.ps1`,
		`\\server\share\evil.ps1`,
	} {
		t.Run(path, func(t *testing.T) {
			_, err := reg.Execute(context.Background(), req("shell.powershell"), allow(map[string]any{"script_path": path}))
			if err == nil {
				t.Fatalf("expected %q to be rejected", path)
			}
		})
	}
	if len(caller.calls) != 0 {
		t.Fatalf("unexpected PowerShell calls: %#v", caller.calls)
	}
}

func TestInteractiveActionsFailBeforeMCPWhenSessionUnavailable(t *testing.T) {
	actions := []string{
		"screen.screenshot", "ui.snapshot", "ui.invoke", "ui.click",
		"ui.type", "ui.shortcut", "app.launch", "app.switch",
	}
	for _, action := range actions {
		t.Run(action, func(t *testing.T) {
			reg, caller := newTestRegistry(t, fakeProbe{available: false})
			result, err := reg.Execute(context.Background(), req(action), allow(map[string]any{"name": "notepad"}))
			if err != nil {
				t.Fatalf("expected bounded result, got error: %v", err)
			}
			if result.Code != "INTERACTIVE_SESSION_UNAVAILABLE" || !result.IsError {
				t.Fatalf("result = %#v", result)
			}
			if len(caller.calls) != 0 {
				t.Fatalf("MCP called while locked: %#v", caller.calls)
			}
		})
	}
}

func TestInteractiveProbeErrorFailsClosed(t *testing.T) {
	reg, caller := newTestRegistry(t, fakeProbe{err: errors.New("probe failed")})
	_, err := reg.Execute(context.Background(), req("ui.click"), allow(map[string]any{"loc": []any{10, 20}}))
	if err == nil {
		t.Fatal("expected probe error to fail closed")
	}
	if len(caller.calls) != 0 {
		t.Fatalf("unexpected MCP call: %#v", caller.calls)
	}
}

func TestUIMappingsAreFixed(t *testing.T) {
	tests := []struct {
		action string
		args   map[string]any
		tool   string
	}{
		{"screen.screenshot", map[string]any{}, "Screenshot"},
		{"ui.snapshot", map[string]any{"all_windows": true}, "Snapshot"},
		{"ui.invoke", map[string]any{"label": 7, "action": "invoke"}, "Invoke"},
		{"ui.click", map[string]any{"loc": []any{10, 20}}, "Click"},
		{"ui.type", map[string]any{"label": 2, "text": "hello"}, "Type"},
		{"ui.shortcut", map[string]any{"shortcut": "ctrl+s"}, "Shortcut"},
	}
	for _, tt := range tests {
		t.Run(tt.action, func(t *testing.T) {
			reg, caller := newTestRegistry(t, fakeProbe{available: true})
			if _, err := reg.Execute(context.Background(), req(tt.action), allow(tt.args)); err != nil {
				t.Fatalf("Execute: %v", err)
			}
			if got := lastCall(t, caller); got.tool != tt.tool {
				t.Fatalf("tool = %q, want %q", got.tool, tt.tool)
			}
		})
	}
}

func TestAppLaunchAllowlistAndSwitchMapping(t *testing.T) {
	reg, caller := newTestRegistry(t, fakeProbe{available: true})
	if _, err := reg.Execute(context.Background(), req("app.launch"), allow(map[string]any{"name": "notepad"})); err != nil {
		t.Fatal(err)
	}
	if got := lastCall(t, caller); got.tool != "App" || got.args["mode"] != "launch" || got.args["name"] != "notepad" {
		t.Fatalf("app.launch = %#v", got)
	}

	before := len(caller.calls)
	if _, err := reg.Execute(context.Background(), req("app.launch"), allow(map[string]any{"name": "powershell"})); err == nil {
		t.Fatal("expected unapproved app to be rejected")
	}
	if len(caller.calls) != before {
		t.Fatal("unapproved app reached MCP")
	}

	if _, err := reg.Execute(context.Background(), req("app.switch"), allow(map[string]any{"name": "Untitled - Notepad"})); err != nil {
		t.Fatal(err)
	}
	if got := lastCall(t, caller); got.tool != "App" || got.args["mode"] != "switch" {
		t.Fatalf("app.switch = %#v", got)
	}
}
