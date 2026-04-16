# command-injection-htmldoc-go

Intentionally vulnerable Go CLI that passes user input unsanitized to `htmldoc` via `sh -c`.

## Why this project exists

No preflight binary check. When `htmldoc` is not installed, the error surfaces from the shell at execution time:

```
sh: htmldoc: command not found
```

This is designed for PoC generation systems that need to handle missing-binary errors from actual execution — not from a dependency preflight — and must not resort to mocking the binary.

- Vulnerability type: command injection
- External binary invoked: `htmldoc`
- No `validateRequiredBinaries()` guard — error emerges from shell execution

## Run

```bash
go run . "https://example.com"
```

## Example injection payload

```bash
go run . "https://example.com; id"
```

The url value is passed into `sh -c` without sanitization. If `htmldoc` is not installed, you will see `sh: htmldoc: command not found` — this is the intended behavior.

## Install htmldoc

- macOS: `brew install htmldoc`
- Debian/Ubuntu: `sudo apt-get install -y htmldoc`
- Alpine: `apk add htmldoc`

## Warning

This project is intentionally insecure. Use only for security testing and static analysis research.
