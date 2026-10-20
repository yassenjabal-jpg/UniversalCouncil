package policy

import (
	"fmt"

	"github.com/yassenjabal-jpg/universal-council/tools/yassin_commander/internal/job"
)

type pathUse struct {
	key   string
	write bool
}

var actionPathUses = map[string][]pathUse{
	"filesystem.list":  {{key: "path"}},
	"filesystem.read":  {{key: "path"}},
	"filesystem.write": {{key: "path", write: true}},
	"filesystem.copy":  {{key: "source"}, {key: "destination", write: true}},
	"filesystem.move":  {{key: "source"}, {key: "destination", write: true}},
}

func Authorize(req job.Request, cfg Config) Decision {
	decision := Decision{
		Allowed:        false,
		NormalizedArgs: cloneArgs(req.Args),
		Risk:           riskForAction(req.Action),
	}

	if !contains(cfg.EnabledActions, req.Action) {
		decision.Reason = fmt.Sprintf("action %q is not enabled", req.Action)
		return decision
	}

	uses := actionPathUses[req.Action]
	if len(uses) == 0 {
		decision.Allowed = true
		decision.Reason = "allowed"
		return decision
	}

	resolver := cfg.Resolver
	if resolver == nil {
		resolver = defaultPathResolver()
	}

	for _, use := range uses {
		raw, ok := req.Args[use.key].(string)
		if !ok || raw == "" {
			decision.Reason = fmt.Sprintf("argument %q must be a non-empty path string", use.key)
			return decision
		}

		normalized, err := normalizeWindowsPath(raw)
		if err != nil {
			decision.Reason = fmt.Sprintf("invalid path in %q: %v", use.key, err)
			return decision
		}
		if isSensitivePath(normalized) {
			decision.Reason = fmt.Sprintf("path in %q is sensitive", use.key)
			return decision
		}

		root, ok := authorizedRoot(normalized, use.write, cfg.AllowedRoots)
		if !ok {
			decision.Reason = fmt.Sprintf("path in %q is outside allowed roots", use.key)
			return decision
		}

		resolved, err := resolver.ResolveExisting(normalized)
		if err != nil {
			decision.Reason = fmt.Sprintf("cannot resolve %q: %v", use.key, err)
			return decision
		}
		if resolved != "" {
			resolvedNormalized, err := normalizeWindowsPath(resolved)
			if err != nil || isSensitivePath(resolvedNormalized) || !pathWithinRoot(resolvedNormalized, root.Path) {
				decision.Reason = fmt.Sprintf("resolved path in %q escapes allowed root", use.key)
				return decision
			}
		}

		if use.write {
			parent, err := resolver.ResolveNearestExistingParent(normalized)
			if err != nil {
				decision.Reason = fmt.Sprintf("cannot resolve parent for %q: %v", use.key, err)
				return decision
			}
			if parent != "" {
				parentNormalized, err := normalizeWindowsPath(parent)
				if err != nil || isSensitivePath(parentNormalized) || !pathWithinRoot(parentNormalized, root.Path) {
					decision.Reason = fmt.Sprintf("existing parent in %q escapes allowed root", use.key)
					return decision
				}
			}
		}

		decision.NormalizedArgs[use.key] = canonicalizeUnderRoot(normalized, root.Path)
	}

	decision.Allowed = true
	decision.Reason = "allowed"
	return decision
}

func cloneArgs(args map[string]any) map[string]any {
	out := make(map[string]any, len(args))
	for k, v := range args {
		out[k] = v
	}
	return out
}

func contains(items []string, value string) bool {
	for _, item := range items {
		if item == value {
			return true
		}
	}
	return false
}
