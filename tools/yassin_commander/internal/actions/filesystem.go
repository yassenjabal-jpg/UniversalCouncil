package actions

import (
	"context"

	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/mcpclient"
)

func (r *Registry) filesystemList(ctx context.Context, args map[string]any) (mcpclient.Result, error) {
	return r.caller.Call(ctx, "FileSystem", map[string]any{"mode": "list", "path": args["path"]})
}

func (r *Registry) filesystemRead(ctx context.Context, args map[string]any) (mcpclient.Result, error) {
	return r.caller.Call(ctx, "FileSystem", map[string]any{"mode": "read", "path": args["path"]})
}

func (r *Registry) filesystemWrite(ctx context.Context, args map[string]any) (mcpclient.Result, error) {
	out := map[string]any{"mode": "write", "path": args["path"]}
	if value, ok := args["content"]; ok {
		out["content"] = value
	}
	if value, ok := args["append"]; ok {
		out["append"] = value
	}
	return r.caller.Call(ctx, "FileSystem", out)
}

func (r *Registry) filesystemCopy(ctx context.Context, args map[string]any) (mcpclient.Result, error) {
	return r.caller.Call(ctx, "FileSystem", map[string]any{
		"mode": "copy", "path": args["source"], "destination": args["destination"],
	})
}

func (r *Registry) filesystemMove(ctx context.Context, args map[string]any) (mcpclient.Result, error) {
	return r.caller.Call(ctx, "FileSystem", map[string]any{
		"mode": "move", "path": args["source"], "destination": args["destination"],
	})
}
