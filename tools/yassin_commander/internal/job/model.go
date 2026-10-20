package job

const MaxIssueBodyBytes = 64 * 1024

type Request struct {
	Version     int            `json:"version"`
	Target      string         `json:"target"`
	Action      string         `json:"action"`
	Args        map[string]any `json:"args"`
	Risk        string         `json:"risk"`
	RequestID   string         `json:"request_id"`
	Actor       string         `json:"-"`
	Repository  string         `json:"-"`
	IssueNumber int            `json:"-"`
	Labels      []string       `json:"-"`
}
