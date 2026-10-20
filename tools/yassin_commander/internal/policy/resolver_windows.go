//go:build windows

package policy

import (
	"errors"
	"os"
	"path/filepath"
)

type windowsResolver struct{}

func defaultPathResolver() PathResolver { return windowsResolver{} }

func (windowsResolver) ResolveExisting(path string) (string, error) {
	if _, err := os.Lstat(path); err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return path, nil
		}
		return "", err
	}
	return filepath.EvalSymlinks(path)
}

func (windowsResolver) ResolveNearestExistingParent(path string) (string, error) {
	current := path
	for {
		if _, err := os.Lstat(current); err == nil {
			return filepath.EvalSymlinks(current)
		} else if !errors.Is(err, os.ErrNotExist) {
			return "", err
		}

		parent := filepath.Dir(current)
		if parent == current {
			return "", os.ErrNotExist
		}
		current = parent
	}
}
