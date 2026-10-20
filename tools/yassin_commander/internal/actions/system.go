package actions

import (
	"context"

	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/mcpclient"
)

const systemStatusCommand = "[Environment]::MachineName"

func (r *Registry) systemStatus(ctx context.Context, _ map[string]any) (mcpclient.Result, error) {
	return r.caller.Call(ctx, "PowerShell", map[string]any{
		"command": systemStatusCommand,
		"timeout": 5,
	})
}
