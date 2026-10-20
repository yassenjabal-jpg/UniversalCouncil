package audit

import (
	"bufio"
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
)

type Writer struct {
	path string
	mu   sync.Mutex
}

func NewWriter(path string) *Writer {
	return &Writer{path: path}
}

func (w *Writer) Append(record Record) error {
	w.mu.Lock()
	defer w.mu.Unlock()

	if err := os.MkdirAll(filepath.Dir(w.path), 0o700); err != nil {
		return fmt.Errorf("create audit directory: %w", err)
	}

	previous, err := currentHead(w.path)
	if err != nil {
		return err
	}
	record.PreviousHash = previous
	record.EntryHash, err = hashRecord(record)
	if err != nil {
		return fmt.Errorf("hash audit record: %w", err)
	}

	line, err := MarshalLine(record)
	if err != nil {
		return fmt.Errorf("marshal audit record: %w", err)
	}

	f, err := os.OpenFile(w.path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o600)
	if err != nil {
		return fmt.Errorf("open audit log: %w", err)
	}
	if _, err := f.Write(append(line, '\n')); err != nil {
		_ = f.Close()
		return fmt.Errorf("append audit log: %w", err)
	}
	if err := f.Sync(); err != nil {
		_ = f.Close()
		return fmt.Errorf("sync audit log: %w", err)
	}
	if err := f.Close(); err != nil {
		return fmt.Errorf("close audit log: %w", err)
	}

	if err := writeHead(w.path, record.EntryHash); err != nil {
		return err
	}
	return nil
}

func ReadAll(path string) ([]Record, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	var records []Record
	scanner := bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 64*1024), 1024*1024)
	for scanner.Scan() {
		line := bytes.TrimSpace(scanner.Bytes())
		if len(line) == 0 {
			continue
		}
		var record Record
		dec := json.NewDecoder(bytes.NewReader(line))
		dec.DisallowUnknownFields()
		if err := dec.Decode(&record); err != nil {
			return nil, fmt.Errorf("decode audit record %d: %w", len(records)+1, err)
		}
		records = append(records, record)
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return records, nil
}

func Verify(path string) error {
	records, err := ReadAll(path)
	if err != nil {
		return err
	}

	previous := ""
	for i, record := range records {
		if record.PreviousHash != previous {
			return fmt.Errorf("audit chain previous hash mismatch at record %d", i+1)
		}
		expected, err := hashRecord(record)
		if err != nil {
			return fmt.Errorf("hash audit record %d: %w", i+1, err)
		}
		if record.EntryHash == "" || record.EntryHash != expected {
			return fmt.Errorf("audit chain entry hash mismatch at record %d", i+1)
		}
		previous = record.EntryHash
	}

	headBytes, err := os.ReadFile(headPath(path))
	if err != nil {
		if errors.Is(err, os.ErrNotExist) && len(records) == 0 {
			return nil
		}
		return fmt.Errorf("read audit head: %w", err)
	}
	head := strings.TrimSpace(string(headBytes))
	if len(records) == 0 {
		if head != "" {
			return errors.New("audit head exists for empty log")
		}
		return nil
	}
	if head != previous {
		return errors.New("audit head does not match final record; log may be truncated or head may be stale")
	}
	return nil
}

func currentHead(path string) (string, error) {
	data, err := os.ReadFile(headPath(path))
	if err == nil {
		return strings.TrimSpace(string(data)), nil
	}
	if !errors.Is(err, os.ErrNotExist) {
		return "", fmt.Errorf("read audit head: %w", err)
	}

	info, statErr := os.Stat(path)
	if statErr == nil && info.Size() > 0 {
		return "", errors.New("audit log exists without head manifest")
	}
	if statErr != nil && !errors.Is(statErr, os.ErrNotExist) {
		return "", fmt.Errorf("stat audit log: %w", statErr)
	}
	return "", nil
}

func writeHead(path, hash string) error {
	head := headPath(path)
	tmp := head + ".tmp"
	if err := os.WriteFile(tmp, []byte(hash+"\n"), 0o600); err != nil {
		return fmt.Errorf("write audit head temp: %w", err)
	}
	if err := os.Rename(tmp, head); err != nil {
		_ = os.Remove(tmp)
		return fmt.Errorf("replace audit head: %w", err)
	}
	return nil
}

func headPath(path string) string {
	return path + ".head"
}
