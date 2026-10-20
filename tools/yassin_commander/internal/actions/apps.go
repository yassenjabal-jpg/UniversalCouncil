package actions

import (
	"context"
	"fmt"
	"strings"

	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/mcpclient"
)

func (r *Registry) appLaunch(ctx context.Context, args map[string]any) (mcpclient.Result, error) {
	ok, err := r.probe.InteractiveAvailable(ctx)
	if err != nil {
		return mcpclient.Result{IsError: true, Code: "INTERACTIVE_SESSION_CHECK_FAILED"}, fmt.Errorf("interactive session probe: %w", err)
	}
	if !ok {
		return mcpclient.Result{IsError: true, Code: "INTERACTIVE_SESSION_UNAVAILABLE"}, nil
	}
	name, ok := args["name"].(string)
	if !ok || strings.TrimSpace(name) == "" {
		return mcpclient.Result{IsError: true, Code: "INVALID_ARGS"}, fmt.Errorf("app.launch requires name")
	}
	name = strings.TrimSpace(name)
	if !containsFold(r.cfg.AllowedApps, name) {
		return mcpclient.Result{IsError: true, Code: "APP_NOT_ALLOWED"}, fmt.Errorf("app is not allowlisted")
	}
	return r.caller.Call(ctx, "App", map[string]any{"mode": "launch", "name": name})
}

func (r *Registry) appSwitch(ctx context.Context, args map[string]any) (mcpclient.Result, error) {
	ok, err := r.probe.InteractiveAvailable(ctx)
	if err != nil {
		return mcpclient.Result{IsError: true, Code: "INTERACTIVE_SESSION_CHECK_FAILED"}, fmt.Errorf("interactive session probe: %w", err)
	}
	if !ok {
		return mcpclient.Result{IsError: true, Code: "INTERACTIVE_SESSION_UNAVAILABLE"}, nil
	}
	name, ok := args["name"].(string)
	if !ok || strings.TrimSpace(name) == "" {
		return mcpclient.Result{IsError: true, Code: "INVALID_ARGS"}, fmt.Errorf("app.switch requires name")
	}
	return r.caller.Call(ctx, "App", map[string]any{"mode": "switch", "name": name})
}
