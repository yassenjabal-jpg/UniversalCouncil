package redact

import (
	"regexp"
	"strings"
)

const marker = "[REDACTED]"

var (
	bearerHeader = regexp.MustCompile(`(?i)(authorization\s*:\s*bearer\s+)[^\s]+`)
	cookieHeader = regexp.MustCompile(`(?im)^(\s*(?:cookie|set-cookie)\s*:\s*).+$`)
	githubToken  = regexp.MustCompile(`\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b`)
	keyValue     = regexp.MustCompile(`(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|token|secret|password|passwd)\s*[:=]\s*([^\s;,\r\n]+)`)
)

func Text(input string) string {
	out := bearerHeader.ReplaceAllString(input, "${1}"+marker)
	out = cookieHeader.ReplaceAllString(out, "${1}"+marker)
	out = githubToken.ReplaceAllString(out, marker)
	out = keyValue.ReplaceAllString(out, "${1}="+marker)
	return out
}

func TextWithLiterals(input string, literals []string) string {
	out := Text(input)
	for _, secret := range literals {
		if secret == "" {
			continue
		}
		out = strings.ReplaceAll(out, secret, marker)
	}
	return out
}
