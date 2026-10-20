package redact

import (
	"strings"
	"testing"
)

func TestTextRedactsCredentialPatterns(t *testing.T) {
	input := strings.Join([]string{
		"Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.secret.signature",
		"token=ghp_1234567890abcdefghijklmnopqrstuvwxyz",
		"fine=github_pat_11AA22BB33CC44DD55EE66FF77GG88HH99II00JJ",
		"API_KEY=super-secret-value",
		"Cookie: sessionid=abc123; csrftoken=xyz789",
	}, "\n")
	got := Text(input)

	for _, secret := range []string{
		"eyJhbGciOiJIUzI1NiJ9.secret.signature",
		"ghp_1234567890abcdefghijklmnopqrstuvwxyz",
		"github_pat_11AA22BB33CC44DD55EE66FF77GG88HH99II00JJ",
		"super-secret-value",
		"sessionid=abc123",
		"csrftoken=xyz789",
	} {
		if strings.Contains(got, secret) {
			t.Fatalf("secret %q leaked in %q", secret, got)
		}
	}
	if !strings.Contains(got, "[REDACTED]") {
		t.Fatalf("expected redaction marker in %q", got)
	}
}

func TestTextWithLiteralsRedactsConfiguredSecrets(t *testing.T) {
	got := TextWithLiterals("prefix local-secret-42 suffix", []string{"local-secret-42"})
	if strings.Contains(got, "local-secret-42") {
		t.Fatalf("configured literal leaked: %q", got)
	}
}

func TestTextKeepsOrdinaryPathsAndRequestIDsReadable(t *testing.T) {
	input := `request yc-123 path C:\YC-Sandbox\reports\today.txt status ok`
	if got := Text(input); got != input {
		t.Fatalf("ordinary text changed: got %q want %q", got, input)
	}
}
