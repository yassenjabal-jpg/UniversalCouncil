package job

import (
	"errors"
	"fmt"
	"strings"
)

type ValidationConfig struct {
	RegisteredActions map[string]struct{}
}

func Validate(req Request, cfg ValidationConfig) error {
	if req.Version != 1 {
		return fmt.Errorf("unsupported job version: %d", req.Version)
	}
	if req.Target != "YASSIN" {
		return fmt.Errorf("unexpected target: %q", req.Target)
	}
	if strings.TrimSpace(req.RequestID) == "" {
		return errors.New("request_id is required")
	}
	if strings.TrimSpace(req.Action) == "" {
		return errors.New("action is required")
	}
	if _, ok := cfg.RegisteredActions[req.Action]; !ok {
		return fmt.Errorf("unregistered action: %q", req.Action)
	}
	if req.Args == nil {
		return errors.New("args must be a JSON object")
	}
	return nil
}
