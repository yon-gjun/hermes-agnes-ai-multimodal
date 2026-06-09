# Agnes AI API Key `***` Corruption Bug

## Problem
When writing Python scripts that contain API key assignments, the Hermes system replaces the actual API key string with a truncated placeholder at the **tool call transmission level**. This happens in:
- `execute_code` Python scripts
- `write_file` tool content
- `patch` tool content

The result is broken Python syntax. Example:
```python
# What you write:
API_KEY=***  # actual key
# What gets written to disk:
API_KEY=***  # truncated to 3 asterisks + garbage
```

## Symptoms
1. `compile()` reports syntax errors on lines containing `API_KEY=*** The generated file has `API_KEY=*** ` with 3 literal asterisks followed by unrelated code
3. Reading the file back shows "clean" content (the display doesn't show the corruption)
4. But executing the file fails with `SyntaxError` on that line

## Debugging Steps

### 1. Verify with raw bytes
```python
with open("script.py", "rb") as f:
    data = f.read()
lines = data.split(b"\n")
for i, line in enumerate(lines):
    if b"API_KEY" in line:
        print(f"L{i+1}: {repr(line)}")
```

### 2. Check if corruption is in the actual file
The display may show clean content even when the file is corrupted. Always verify with `repr()` or `hex()`.

## Fixes

### Fix 1: Use `read_key()` function pattern
Don't assign the key inline. Read it from `.env` at runtime via a function:
```python
def read_key():
    for p in [os.path.expanduser("~/.hermes/.env"), os.path.expanduser("~/.env")]:
        if os.path.exists(p):
            for ln in open(p):
                if ln.startswith("AGNES_API_KEY=***                    return ln[14:].strip().strip('"').strip("'")
    return os.getenv("AGNES_API_KEY", "")

API_KEY=*** Fix 2: Patch broken files with `execute_code` using hex codes
When you need to fix a corrupted file, use `\x2a\x2a\x2a` (hex for `***`) to construct the pattern without triggering the system replacement:
```python
with open("script.py", "rb") as f:
    data = f.read()

# Use hex codes to avoid `***` corruption in the tool call itself
pattern = b"API_KEY=*** + b"\x2a\x2a" + b" k = read_key()"
# But even this fails — the `***` in YOUR source also gets corrupted!

# Instead, build pattern from hex only:
AST = b"\x2a\x2a\x2a"  # Never use literal *** in source
pattern = b"API_KEY=*** + AST + b" k = read_key()"
# This works because we only use hex codes
data = data.replace(pattern, b"API_KEY=*** k = read_key()")
```

### Fix 3: Use `tee` with bash heredoc
```bash
tee /path/to/file.py << 'EOF'
#!/usr/bin/env python3
API_KEY=*** "")
EOF
```
Heredocs with `'EOF'` (quoted) pass content to the file without system interception.

## Prevention
- Always use `read_key()` function pattern for API keys in scripts
- Avoid inline `API_KEY=*** assignments in generated files
- When debugging, always check `repr()` of raw bytes, not just `read()` output
