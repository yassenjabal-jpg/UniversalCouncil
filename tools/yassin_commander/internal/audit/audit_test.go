package audit

import (
	"os"
	"path/filepath"
	"sync"
	"testing"
	"time"
)

func sampleRecord(id string) Record {
	start := time.Date(2026, 10, 20, 5, 0, 0, 0, time.UTC)
	return Record{
		RequestID:     id,
		IssueNumber:   42,
		Actor:         "yassenjabal-jpg",
		Action:        "filesystem.read",
		ArgsDigest:    "args-digest",
		PolicyVerdict: "allowed",
		StartedAt:     start,
		EndedAt:       start.Add(time.Second),
		Status:        "success",
		ResultDigest:  "result-digest",
	}
}

func TestWriterAppendAndVerifyChain(t *testing.T) {
	path := filepath.Join(t.TempDir(), "audit.jsonl")
	w := NewWriter(path)

	if err := w.Append(sampleRecord("yc-1")); err != nil {
		t.Fatalf("Append first: %v", err)
	}
	if err := w.Append(sampleRecord("yc-2")); err != nil {
		t.Fatalf("Append second: %v", err)
	}
	if err := Verify(path); err != nil {
		t.Fatalf("Verify: %v", err)
	}

	records, err := ReadAll(path)
	if err != nil {
		t.Fatalf("ReadAll: %v", err)
	}
	if len(records) != 2 {
		t.Fatalf("record count = %d, want 2", len(records))
	}
	if records[0].PreviousHash != "" {
		t.Fatalf("first previous hash = %q", records[0].PreviousHash)
	}
	if records[0].EntryHash == "" || records[1].PreviousHash != records[0].EntryHash {
		t.Fatalf("chain not linked: %#v", records)
	}
}

func TestVerifyDetectsTampering(t *testing.T) {
	path := filepath.Join(t.TempDir(), "audit.jsonl")
	w := NewWriter(path)
	if err := w.Append(sampleRecord("yc-1")); err != nil {
		t.Fatal(err)
	}
	if err := w.Append(sampleRecord("yc-2")); err != nil {
		t.Fatal(err)
	}

	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	for i := range data {
		if data[i] == '2' {
			data[i] = '9'
			break
		}
	}
	if err := os.WriteFile(path, data, 0o600); err != nil {
		t.Fatal(err)
	}
	if err := Verify(path); err == nil {
		t.Fatal("expected tampering to be detected")
	}
}

func TestVerifyDetectsTruncationAgainstHead(t *testing.T) {
	path := filepath.Join(t.TempDir(), "audit.jsonl")
	w := NewWriter(path)
	if err := w.Append(sampleRecord("yc-1")); err != nil {
		t.Fatal(err)
	}
	if err := w.Append(sampleRecord("yc-2")); err != nil {
		t.Fatal(err)
	}

	records, err := ReadAll(path)
	if err != nil {
		t.Fatal(err)
	}
	line, err := MarshalLine(records[0])
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, append(line, '\n'), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := Verify(path); err == nil {
		t.Fatal("expected truncation to be detected by head manifest")
	}
}

func TestWriterSerializesConcurrentAppends(t *testing.T) {
	path := filepath.Join(t.TempDir(), "audit.jsonl")
	w := NewWriter(path)
	const count = 20

	var wg sync.WaitGroup
	errs := make(chan error, count)
	for i := 0; i < count; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			errs <- w.Append(sampleRecord("yc-concurrent"))
		}(i)
	}
	wg.Wait()
	close(errs)
	for err := range errs {
		if err != nil {
			t.Fatalf("concurrent append: %v", err)
		}
	}
	if err := Verify(path); err != nil {
		t.Fatalf("Verify after concurrent appends: %v", err)
	}
	records, err := ReadAll(path)
	if err != nil {
		t.Fatal(err)
	}
	if len(records) != count {
		t.Fatalf("record count = %d, want %d", len(records), count)
	}
}
