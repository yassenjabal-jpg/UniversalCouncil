package policy

import (
	"errors"
	"fmt"
	"strings"
	"unicode"
)

var sensitiveFragments = []string{
	`\.ssh\`,
	`\appdata\local\google\chrome\user data\`,
	`\appdata\local\microsoft\edge\user data\`,
	`\appdata\roaming\microsoft\credentials\`,
	`\appdata\local\microsoft\credentials\`,
	`\appdata\roaming\microsoft\protect\`,
	`\appdata\local\microsoft\vault\`,
	`\appdata\roaming\microsoft\vault\`,
	`\windows\system32\config\sam`,
	`\windows\system32\config\security`,
	`\windows\system32\config\system`,
}

var reservedDeviceNames = map[string]struct{}{
	"con": {}, "prn": {}, "aux": {}, "nul": {},
	"com1": {}, "com2": {}, "com3": {}, "com4": {}, "com5": {}, "com6": {}, "com7": {}, "com8": {}, "com9": {},
	"lpt1": {}, "lpt2": {}, "lpt3": {}, "lpt4": {}, "lpt5": {}, "lpt6": {}, "lpt7": {}, "lpt8": {}, "lpt9": {},
}

func normalizeWindowsPath(raw string) (string, error) {
	if strings.IndexByte(raw, 0) >= 0 {
		return "", errors.New("NUL byte is not allowed")
	}
	p := strings.ReplaceAll(strings.TrimSpace(raw), "/", `\`)
	if strings.HasPrefix(p, `\\`) {
		return "", errors.New("UNC and device paths are not allowed")
	}
	if len(p) < 3 || p[1] != ':' || p[2] != '\\' || !unicode.IsLetter(rune(p[0])) {
		return "", errors.New("absolute drive path is required")
	}

	drive := strings.ToUpper(p[:1]) + ":"
	parts := strings.Split(p[3:], `\`)
	clean := make([]string, 0, len(parts))
	for _, part := range parts {
		if part == "" || part == "." {
			continue
		}
		if part == ".." {
			return "", errors.New("path traversal is not allowed")
		}
		if strings.Contains(part, ":") {
			return "", errors.New("alternate data streams are not allowed")
		}
		if strings.HasSuffix(part, ".") || strings.HasSuffix(part, " ") {
			return "", errors.New("ambiguous trailing dot/space segment is not allowed")
		}
		base := strings.ToLower(part)
		if dot := strings.IndexByte(base, '.'); dot >= 0 {
			base = base[:dot]
		}
		if _, reserved := reservedDeviceNames[base]; reserved {
			return "", fmt.Errorf("reserved device segment %q is not allowed", part)
		}
		clean = append(clean, part)
	}
	if len(clean) == 0 {
		return drive + `\`, nil
	}
	return drive + `\` + strings.Join(clean, `\`), nil
}

func isSensitivePath(path string) bool {
	lower := strings.ToLower(path)
	for _, fragment := range sensitiveFragments {
		if strings.Contains(lower, fragment) {
			return true
		}
	}
	return false
}

func authorizedRoot(path string, write bool, roots []RootRule) (RootRule, bool) {
	for _, root := range roots {
		if !pathWithinRoot(path, root.Path) {
			continue
		}
		if write && !root.Write {
			continue
		}
		if !write && !root.Read {
			continue
		}
		return root, true
	}
	return RootRule{}, false
}

func pathWithinRoot(path, rawRoot string) bool {
	root, err := normalizeWindowsPath(rawRoot)
	if err != nil {
		return false
	}
	p := strings.ToLower(path)
	r := strings.TrimSuffix(strings.ToLower(root), `\`)
	return p == r || strings.HasPrefix(p, r+`\`)
}

func canonicalizeUnderRoot(path, rawRoot string) string {
	root, err := normalizeWindowsPath(rawRoot)
	if err != nil {
		return path
	}
	r := strings.TrimSuffix(root, `\`)
	if strings.EqualFold(path, r) {
		return r
	}
	if len(path) > len(r) && strings.EqualFold(path[:len(r)], r) {
		return r + path[len(r):]
	}
	return path
}
