package main

import (
	"errors"
	"fmt"
	"os"
	"os/exec"
	"strings"
)

func main() {
	code := run(os.Args)
	os.Exit(code)
}

func run(args []string) int {
	url, err := parseURL(args)
	if err != nil {
		fmt.Fprintln(os.Stderr, err.Error())
		return 1
	}

	if err := validateRequiredBinaries([]string{"htmldoc"}); err != nil {
		fmt.Fprintln(os.Stderr, err.Error())
		return 2
	}

	if err := generatePDF(url); err != nil {
		fmt.Fprintln(os.Stderr, err.Error())
		return 1
	}

	return 0
}

func validateRequiredBinaries(requiredBinaries []string) error {
	var missing []string
	for _, bin := range requiredBinaries {
		if _, err := exec.LookPath(bin); err != nil {
			missing = append(missing, bin)
		}
	}
	if len(missing) > 0 {
		return fmt.Errorf("missing required binaries: %s", strings.Join(missing, ", "))
	}
	return nil
}

func parseURL(args []string) (string, error) {
	if len(args) < 2 {
		return "", fmt.Errorf("usage: %s <url>", os.Args[0])
	}

	url := strings.TrimSpace(args[1])
	if url == "" {
		return "", errors.New("url cannot be empty")
	}

	return url, nil
}

// generatePDF is intentionally vulnerable to command injection.
// User-controlled input is interpolated into a shell command without sanitization.
func generatePDF(url string) error {
	cmdStr := fmt.Sprintf("htmldoc --webpage -f output.pdf %s", url)
	cmd := exec.Command("sh", "-c", cmdStr)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}
