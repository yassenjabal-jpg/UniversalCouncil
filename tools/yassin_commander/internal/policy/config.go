package policy

type RootRule struct {
	Path  string `json:"path"`
	Read  bool   `json:"read"`
	Write bool   `json:"write"`
}

type PathResolver interface {
	ResolveExisting(path string) (string, error)
	ResolveNearestExistingParent(path string) (string, error)
}

type Config struct {
	EnabledActions []string     `json:"enabled_actions"`
	AllowedRoots   []RootRule   `json:"allowed_roots"`
	Resolver       PathResolver `json:"-"`
}

type Decision struct {
	Allowed        bool
	Reason         string
	NormalizedArgs map[string]any
	Risk           Risk
}
