package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestSave(t *testing.T) {
	calls := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls++
		if r.Method != "POST" || r.URL.Path != "/addons/self/options" || r.Header.Get("Authorization") != "Bearer fixture" {
			t.Error("incorrect authenticated self request")
		}
		var payload struct {
			Options map[string]string `json:"options"`
		}
		if err := json.NewDecoder(r.Body).Decode(&payload); err != nil {
			t.Fatal(err)
		}
		if payload.Options["ARCANE_AGENT_TOKEN"] != "quote\"slash\\newline\n" || len(payload.Options) != 3 {
			t.Error("incorrect canonical options")
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"result":"ok"}`))
	}))
	defer server.Close()
	err := save(server.Client(), server.URL+"/addons/self/options", "fixture", map[string]string{
		"ARCANE_MANAGER_API_URL": "https://manager.test", "ARCANE_AGENT_TOKEN": "quote\"slash\\newline\n", "ARCANE_AGENT_TRANSPORT": "auto",
	})
	if err != nil || calls != 1 {
		t.Fatalf("save failed: %v", err)
	}
}

func TestSaveFailure(t *testing.T) {
	for _, body := range []string{`{"result":"error","message":"secret"}`, `not json`} {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { _, _ = w.Write([]byte(body)) }))
		if err := save(server.Client(), server.URL, "fixture", nil); err == nil {
			t.Error("failure reported as success")
		}
		server.Close()
	}
}
