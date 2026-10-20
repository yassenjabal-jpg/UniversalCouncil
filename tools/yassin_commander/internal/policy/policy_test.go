package policy

import (
	"testing"

	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/job"
)

type fakeResolver struct {
	resolved map[string]string
	parents  map[string]string
}

func (f fakeResolver) ResolveExisting(path string) (string, error) {
	if v, ok := f.resolved[path]; ok {
		return v, nil
	}
	return path, nil
}

func (f fakeResolver) ResolveNearestExistingParent(path string) (string, error) {
	if v, ok := f.parents[path]; ok {
		return v, nil
	}
	return path, nil
}

func baseConfig() Config {
	return Config{
		EnabledActions: []string{
			"filesystem.list", "filesystem.read", "filesystem.write",
			"filesystem.copy", "filesystem.move", "system.status",
		},
		AllowedRoots: []RootRule{
			{Path: `C:\YC-Sandbox`, Read: true, Write: true},
			{Path: `C:\Reports`, Read: true, Write: false},
		},
	}
}

func request(action string, args map[string]any) job.Request {
	return job.Request{Version: 1, Target: "YASSIN", Action: action, Args: args, RequestID: "yc-test"}
}

func TestAuthorizeAllowsPathInsideWritableRoot(t *testing.T) {
	decision := Authorize(request("filesystem.write", map[string]any{
		"path": `c:/yc-sandbox/sub/report.txt`,
	}), baseConfig())
	if !decision.Allowed {
		t.Fatalf("expected allow, got deny: %s", decision.Reason)
	}
	if got := decision.NormalizedArgs["path"]; got != `C:\YC-Sandbox\sub\report.txt` {
		t.Fatalf("normalized path = %#v", got)
	}
}

func TestAuthorizeRejectsTraversalEvenWhenItWouldCleanInside(t *testing.T) {
	decision := Authorize(request("filesystem.read", map[string]any{
		"path": `C:\YC-Sandbox\sub\..\report.txt`,
	}), baseConfig())
	if decision.Allowed {
		t.Fatal("expected traversal to be denied")
	}
}

func TestAuthorizeRejectsUNCAndDevicePaths(t *testing.T) {
	for _, path := range []string{
		`\\server\share\a.txt`,
		`\\?\C:\YC-Sandbox\a.txt`,
		`\\.\C:\YC-Sandbox\a.txt`,
		`C:\YC-Sandbox\a.txt:secret`,
	} {
		t.Run(path, func(t *testing.T) {
			decision := Authorize(request("filesystem.read", map[string]any{"path": path}), baseConfig())
			if decision.Allowed {
				t.Fatalf("expected %q to be denied", path)
			}
		})
	}
}

func TestAuthorizeUsesCaseInsensitiveRootComparison(t *testing.T) {
	decision := Authorize(request("filesystem.read", map[string]any{
		"path": `c:\YC-SANDBOX\Data\a.txt`,
	}), baseConfig())
	if !decision.Allowed {
		t.Fatalf("expected case-insensitive allow: %s", decision.Reason)
	}
}

func TestAuthorizeDeniesWriteToReadOnlyRoot(t *testing.T) {
	decision := Authorize(request("filesystem.write", map[string]any{
		"path": `C:\Reports\today.txt`,
	}), baseConfig())
	if decision.Allowed {
		t.Fatal("expected write to read-only root to be denied")
	}
}

func TestAuthorizeAllowsReadFromReadOnlyRoot(t *testing.T) {
	decision := Authorize(request("filesystem.read", map[string]any{
		"path": `C:\Reports\today.txt`,
	}), baseConfig())
	if !decision.Allowed {
		t.Fatalf("expected read to be allowed: %s", decision.Reason)
	}
}

func TestAuthorizeDeniesSensitiveCredentialLocations(t *testing.T) {
	cfg := baseConfig()
	cfg.AllowedRoots = append(cfg.AllowedRoots, RootRule{Path: `C:\Users\Yassen`, Read: true, Write: true})
	paths := []string{
		`C:\Users\Yassen\.ssh\id_ed25519`,
		`C:\Users\Yassen\AppData\Local\Google\Chrome\User Data\Default\Login Data`,
		`C:\Users\Yassen\AppData\Local\Microsoft\Edge\User Data\Default\Cookies`,
		`C:\Users\Yassen\AppData\Roaming\Microsoft\Credentials\deadbeef`,
		`C:\Users\Yassen\AppData\Roaming\Microsoft\Protect\S-1-5-21\key`,
	}
	for _, path := range paths {
		t.Run(path, func(t *testing.T) {
			decision := Authorize(request("filesystem.read", map[string]any{"path": path}), cfg)
			if decision.Allowed {
				t.Fatalf("expected sensitive path %q to be denied", path)
			}
		})
	}
}

func TestAuthorizeDeniesReparseEscapeForExistingPath(t *testing.T) {
	cfg := baseConfig()
	cfg.Resolver = fakeResolver{resolved: map[string]string{
		`C:\YC-Sandbox\link\secret.txt`: `C:\Users\Yassen\.ssh\id_ed25519`,
	}}
	decision := Authorize(request("filesystem.read", map[string]any{
		"path": `C:\YC-Sandbox\link\secret.txt`,
	}), cfg)
	if decision.Allowed {
		t.Fatal("expected resolved path outside allowed roots to be denied")
	}
}

func TestAuthorizeChecksNearestExistingParentForNewFile(t *testing.T) {
	cfg := baseConfig()
	cfg.Resolver = fakeResolver{parents: map[string]string{
		`C:\YC-Sandbox\new\file.txt`: `C:\Outside`,
	}}
	decision := Authorize(request("filesystem.write", map[string]any{
		"path": `C:\YC-Sandbox\new\file.txt`,
	}), cfg)
	if decision.Allowed {
		t.Fatal("expected new file whose existing parent resolves outside root to be denied")
	}
}

func TestAuthorizeDeniesUnknownOrDisabledAction(t *testing.T) {
	cfg := baseConfig()
	for _, action := range []string{"shell.raw", "process.stop"} {
		decision := Authorize(request(action, map[string]any{}), cfg)
		if decision.Allowed {
			t.Fatalf("expected action %q to be denied", action)
		}
	}
}

func TestActionRiskComesFromCodeNotIssue(t *testing.T) {
	req := request("filesystem.read", map[string]any{"path": `C:\YC-Sandbox\a.txt`})
	req.Risk = "high"
	decision := Authorize(req, baseConfig())
	if !decision.Allowed {
		t.Fatalf("expected allow: %s", decision.Reason)
	}
	if decision.Risk != RiskLow {
		t.Fatalf("risk = %q, want %q", decision.Risk, RiskLow)
	}
}
