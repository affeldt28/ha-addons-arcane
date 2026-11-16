// Save the canonical UI fields through the add-on's own Supervisor endpoint.
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

func save(client *http.Client, endpoint, token string, options map[string]string) error {
	payload, err := json.Marshal(map[string]any{"options": options})
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPost, endpoint, bytes.NewReader(payload))
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")
	response, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("Supervisor request failed")
	}
	defer response.Body.Close()
	var result struct {
		Result string `json:"result"`
	}
	if response.StatusCode != http.StatusOK || json.NewDecoder(io.LimitReader(response.Body, 1<<20)).Decode(&result) != nil || result.Result != "ok" {
		return fmt.Errorf("Supervisor did not confirm saved options")
	}
	return nil
}

func main() {
	options := map[string]string{}
	for _, key := range []string{"ARCANE_MANAGER_API_URL", "ARCANE_AGENT_TOKEN", "ARCANE_AGENT_TRANSPORT"} {
		options[key] = os.Getenv(key)
	}
	client := &http.Client{Timeout: 10 * time.Second, CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }}
	if err := save(client, "http://supervisor/addons/self/options", os.Getenv("SUPERVISOR_TOKEN"), options); err != nil {
		fmt.Fprintln(os.Stderr, "WARNING: Could not save migrated Configuration fields; startup continues. Retry by restarting the add-on.")
		os.Exit(1)
	}
	fmt.Println("Saved migrated Arcane fields in Home Assistant Configuration.")
}
