//go:build !windows

package policy

type lexicalResolver struct{}

func defaultPathResolver() PathResolver { return lexicalResolver{} }

func (lexicalResolver) ResolveExisting(path string) (string, error) {
	return path, nil
}

func (lexicalResolver) ResolveNearestExistingParent(path string) (string, error) {
	return path, nil
}
