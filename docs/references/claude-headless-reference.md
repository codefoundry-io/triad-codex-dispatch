# Claude Code Headless/Print Mode Complete Reference
**For v2.1.196** | [Official docs: code.claude.com/docs/en/headless.md](https://code.claude.com/docs/en/headless.md)

---

## 1. Print/Headless Invocation

### Basic Syntax
```bash
claude -p "your prompt"          # Short form
claude --print "your prompt"      # Long form
```

### Prompt Input Methods
- **Argv**: `claude -p "prompt text"`
- **Stdin**: `cat file.txt | claude -p "analyze this"` (pipe data)
- **Stdin stdin limit**: **10 MB** (as of v2.1.128; errors with non-zero exit if exceeded)
- **Input format**: `--input-format {text|stream-json}`
  - `text` (default): plain stdin
  - `stream-json`: newline-delimited JSON streaming input (for real-time prompts)

### Input vs Context
- **Piped stdin**: sole instruction when used alone; combines with prompt arg if both provided
- **Prompt arg**: required; stdin is supplementary context
- **Example**: `echo "10 + 5" | claude -p "Calculate this"` → stdin becomes context

### Workspace Trust (Print Mode)
- **Interactive dialogs skipped** in `-p` mode and when stdout is not a TTY
- **Settings validation**: files that fail validation are silently ignored (no error dialog)
- ⚠️ **Use only in directories you trust**

---

## 2. Output Formats & JSON Envelope

### `--output-format {text|json|stream-json}`

#### **`text` (default)**
```bash
claude -p "summarize" --output-format text
```
- Plain text response
- For piping: `claude -p "query" --output-format text > output.txt`

#### **`json` (single result object)**
```bash
claude -p "list files" --output-format json
```

**JSON Envelope Fields** (top-level keys):
```json
{
  "type": "result",
  "subtype": "success|error_max_structured_output_retries",
  "is_error": false,
  "api_error_status": 401 | null,
  "result": "Text response here",
  "stop_reason": "stop_sequence|max_tokens|tool_use|end_turn",
  "session_id": "uuid",
  "total_cost_usd": 0.00123,
  "usage": {
    "input_tokens": 500,
    "output_tokens": 250,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0,
    "server_tool_use": {
      "web_search_requests": 0,
      "web_fetch_requests": 0
    },
    "service_tier": "standard|batch",
    "cache_creation": {
      "ephemeral_1h_input_tokens": 0,
      "ephemeral_5m_input_tokens": 0
    },
    "inference_geo": "us-west-2",
    "iterations": [],
    "speed": "standard|turbo"
  },
  "modelUsage": {
    "model": "claude-opus-4-8",
    "input_tokens": 500,
    "output_tokens": 250,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0
  },
  "structured_output": { /* only if --json-schema used */ },
  "permission_denials": [],
  "terminal_reason": "completed|max_turns_reached|budget_exceeded",
  "fast_mode_state": "on|off",
  "uuid": "request-uuid",
  "duration_ms": 1234,
  "duration_api_ms": 900
}
```

**Key fields**:
- `result`: the text response (always present, even on error)
- `structured_output`: populated only when `--json-schema` is used
- `subtype == "error_max_structured_output_retries"`: validation failure on `--json-schema`
- `is_error`: `true` if API error occurred (auth, rate limit, etc.)
- `api_error_status`: HTTP status code (401, 429, 500, etc.) or `null`
- `total_cost_usd`: includes usage credits for multi-turn, tool use, etc.
- `terminal_reason`: why the session ended

#### **`stream-json` (newline-delimited events)**
```bash
claude -p "explain recursion" --output-format stream-json --verbose --include-partial-messages
```

**Event Types** (each line is a JSON object):
```json
{"type":"system","subtype":"init","session_id":"..","data":{"model":"claude-opus-4-8","tools":[...],...}}

{"type":"stream_event","subtype":"message_start","session_id":"..","uuid":"..","event":{"type":"message_start","message":{"id":"msg_...","type":"message",...}}}

{"type":"stream_event","subtype":"text_delta","session_id":"..","event":{"delta":{"type":"text_delta","text":"Hello"}}}

{"type":"stream_event","subtype":"tool_use","session_id":"..","event":{"delta":{"type":"input_json_delta","partial_json":"{\"path\": \"/etc\"..."}}}

{"type":"stream_event","subtype":"message_stop","session_id":"..","event":{"delta":{"stop_reason":"stop_sequence"}}}

{"type":"system","subtype":"api_retry","session_id":"..","attempt":1,"max_retries":2,"retry_delay_ms":1000,"error_status":429,"error":"rate_limit","uuid":"..."}

{"type":"system","subtype":"plugin_install","session_id":"..","status":"started|installed|failed|completed","name":"plugin-name","error":"failure message","uuid":"...","session_id":"..."}
```

**Stream event schema**:
| Field | Type | Description |
|-------|------|-------------|
| `type` | string | `"stream_event"` or `"system"` |
| `subtype` | string | `message_start`, `text_delta`, `tool_use`, `message_stop`, `api_retry`, `plugin_install` |
| `uuid` | string | unique event ID |
| `session_id` | string | session the event belongs to |
| `event` | object | event payload (structure varies by type) |
| `event.delta.type` | string | `text_delta`, `input_json_delta`, etc. |
| `event.delta.text` | string | streamed text chunk (when `type == "text_delta"`) |
| `attempt` | number | retry attempt (on `api_retry` events) |
| `max_retries` | number | total retries allowed |
| `retry_delay_ms` | number | milliseconds until next attempt |
| `error_status` | number \| null | HTTP status code (429, 500, etc.) or null for connection errors |
| `error` | string | error category: `authentication_failed`, `oauth_org_not_allowed`, `billing_error`, `rate_limit`, `overloaded`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `unknown` |

**Filtering with jq**:
```bash
# Extract just the streamed text
claude -p "Write a poem" --output-format stream-json --verbose --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'

# Extract the result from stream-json
claude -p "summarize" --output-format stream-json | jq -r '.result'
```

### Additional Output Flags

#### `--include-partial-messages`
- Emits `text_delta` events as tokens stream in (requires `--print` + `--output-format stream-json`)
- Without it, only the final message is shown

#### `--include-hook-events`
- Include hook lifecycle events in stream-json output (requires `--output-format stream-json`)
- Useful for monitoring setup/teardown phases in CI

#### `--verbose`
- Enables verbose logging; shows full turn-by-turn output
- Adds hook events to stream-json
- Overrides `viewMode` setting for the session

#### `--prompt-suggestions`
- After each turn, emit a `prompt_suggestion` event with predicted next prompt
- Requires `--print`, `--output-format stream-json`, `--verbose`
- Accepts: `"true"`, `"false"`, `"1"`, `"0"`, `"yes"`, `"no"`, `"on"`, `"off"` (default: `"true"`)

---

## 3. Structured Output

### Syntax: `--json-schema <schema>`
```bash
claude -p "Extract function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'
```

### How It Works
1. Pass a **JSON Schema** (standard JSON Schema format)
2. Claude generates output matching the schema
3. Output is validated; on mismatch, retried (up to retry limit)
4. Result goes in `structured_output` field of JSON envelope
5. On validation failure, `subtype` becomes `"error_max_structured_output_retries"`

### Output Location
- **Field name**: `structured_output` (in the `json` envelope)
- **Validation**: automatic; re-prompts on mismatch
- **Error handling**: see § Error Handling below

### Supported Schema Features
- Basic types: `object`, `array`, `string`, `number`, `boolean`, `null`
- `enum` and `const`
- `required` fields
- Nested objects
- `$ref` definitions
- Array items with type constraints

### Error Handling
```json
{
  "type": "result",
  "subtype": "success|error_max_structured_output_retries",
  "structured_output": { /* validated object */ },
  "errors": [ /* validation details, if any */ ]
}
```

**Subtype values**:
- `success`: output validated; `structured_output` is present
- `error_max_structured_output_retries`: validation failed after retries

### Example with jq
```bash
# Extract structured output
claude -p "Extract contacts" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"contacts":{"type":"array","items":{"type":"object","properties":{"name":{"type":"string"},"email":{"type":"string"}}}}}}' \
  | jq '.structured_output'
```

---

## 4. Model/Tier Selection

### Model Aliases (latest versions per provider)
- **`default`**: clears override, reverts to account-type default
- **`best`**: Fable 5 (where available) or latest Opus
- **`fable`**: Claude Fable 5 (v2.1.170+)
- **`opus`**: latest Opus (Opus 4.8 on API, Opus 4.7 on AWS, etc.)
- **`sonnet`**: latest Sonnet (Sonnet 5 on API, Sonnet 4.6 on AWS, etc.)
- **`haiku`**: Haiku model (Haiku 4-5 on API)
- **`opusplan`**: Opus in plan mode, switches to Sonnet in execution
- **`sonnet[1m]`**, **`opus[1m]`**: with 1M token context window

### Full Model IDs (Anthropic API)
- `claude-fable-5` (requires v2.1.170+)
- `claude-opus-4-8`
- `claude-sonnet-5`
- `claude-haiku-4-5-20241001` (dated release)

### Flags
```bash
claude -p "query" --model opus              # Use Opus alias
claude -p "query" --model claude-sonnet-5   # Full model ID
claude -p "query" --fallback-model sonnet,haiku  # Fallback chain
```

### Environment Variables
```bash
export ANTHROPIC_MODEL="opus"
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-opus-4-8"
export ANTHROPIC_DEFAULT_SONNET_MODEL="claude-sonnet-5"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="claude-haiku-4-5-20241001"
```

### Fallback Model Chains
```bash
# CLI flag (comma-separated)
claude -p "query" --fallback-model sonnet,haiku

# Settings file (array)
{
  "fallbackModel": ["claude-sonnet-5", "claude-haiku-4-5"]
}
```
- Tries each model in order if primary is overloaded/unavailable
- Skips retired or disallowed models
- Limited to 3 models max
- Each turn retries primary first

---

## 5. Reasoning/Effort

### `--effort <level>`
**Allowed levels** (depend on model):

| Level | Models | Description |
|-------|--------|-------------|
| `low` | Fable, Sonnet 5, Opus 4.8, 4.7, 4.6, Sonnet 4.6 | Fast, low token spend |
| `medium` | Fable, Sonnet 5, Opus 4.8, 4.7, 4.6, Sonnet 4.6 | Reduced token usage |
| `high` | Fable, Sonnet 5, Opus 4.8, 4.7, 4.6, Sonnet 4.6 | **Default on most models** |
| `xhigh` | Fable, Sonnet 5, Opus 4.8, 4.7, 4.6, Sonnet 4.6 | Deeper reasoning, more tokens |
| `max` | Fable, Sonnet 5, Opus 4.8, 4.7, 4.6, Sonnet 4.6 | Deepest reasoning, no token cap (session-only) |

- **Default**: `high` (Fable, Sonnet 5, Opus 4.8, 4.6, Sonnet 4.6); `xhigh` on Opus 4.7
- **Unsupported levels**: fall back to highest supported level at or below requested
- **`max` persistence**: session-only (unless set via `CLAUDE_CODE_EFFORT_LEVEL` env var)

```bash
claude -p "complex task" --effort xhigh --model opus
```

### Environment Variable
```bash
export CLAUDE_CODE_EFFORT_LEVEL="xhigh"
```

---

## 6. Permissions/Sandbox (Read-Only vs Write)

### `--permission-mode <mode>`
Enum: `default|acceptEdits|plan|auto|dontAsk|bypassPermissions`

| Mode | Behavior |
|------|----------|
| `default` | Prompt on each tool use (interactive mode default) |
| `acceptEdits` | Auto-approve file reads/writes and common fs commands (`mkdir`, `touch`, `mv`, `cp`); other Bash/network still prompt |
| `plan` | Plan mode; executes in planning context first |
| `auto` | Auto-approve safe commands (read-only set); deny others |
| `dontAsk` | Deny anything not in `permissions.allow` or the read-only set |
| `bypassPermissions` | Skip all permission checks (⚠️ dangerous; only in trusted sandboxes) |

```bash
# Read-only strict mode (pre-approve only safe reads)
claude -p "analyze code" --permission-mode dontAsk --allowedTools "Read,Glob,Grep"

# Auto-approve writes (for CI/automation)
claude -p "apply fixes" --permission-mode acceptEdits

# Bypass all checks (sandbox only)
claude -p "query" --permission-mode bypassPermissions
```

### `--allowedTools <tools...>`
Comma or space-separated list of tool patterns. Supports wildcard matching:
```bash
claude -p "create commit" \
  --allowedTools "Bash(git diff *)" "Bash(git log *)" "Bash(git commit *)" "Read" "Edit"
```

**Syntax**:
- `Read` — allow all file reads
- `Bash(git *)` — allow bash commands starting with `git`
- `Edit` — allow file edits
- `Bash(rm *)` — allow rm commands (be careful!)
- Space before `*` is required for prefix matching

### `--disallowedTools <tools...>`
Deny rules. Two forms:
- **Bare**: `--disallowedTools "Edit"` removes the tool from context
- **Scoped**: `--disallowedTools "Bash(rm *)"` leaves the tool available, blocks matching calls

### Web Search & WebFetch
```bash
# Enable WebSearch tool (for current session)
claude -p "research topic" --allowedTools "WebSearch,Read"

# Default: off in print mode (not auto-enabled)
```

### `--add-dir <directories...>`
Grant file access to additional directories:
```bash
claude -p "analyze code" --add-dir ../apps ../lib
```
- Grants read/write in those dirs
- CLAUDE.md config is NOT discovered from these dirs
- To persist, set `permissions.additionalDirectories` in settings.json

### `--dangerously-skip-permissions`
Equivalent to `--permission-mode bypassPermissions`. **Use only in trusted sandboxes.**

### Strict Read-Only Run
```bash
# Pre-approve only safe read tools
claude -p "review code" \
  --permission-mode dontAsk \
  --allowedTools "Read,Glob,Grep,Bash(grep *)"
```

---

## 7. Web Search in Headless

### Enable WebSearch
```bash
claude -p "latest Claude models" --allowedTools "WebSearch"
```

### WebSearch + WebFetch
```bash
claude -p "research feature" \
  --allowedTools "WebSearch,WebFetch,Read" \
  --output-format json
```

### Default Behavior
- **Print mode default**: WebSearch is off (must explicitly enable with `--allowedTools`)
- Interactive mode default: WebSearch available (requires prompt approval each time)
- No environment variable to flip the default

---

## 8. Limits & Lifecycle

### `--max-turns <number>`
- Limit agentic iterations
- Exits with error when limit reached
- No limit by default

```bash
claude -p "refactor code" --max-turns 3
```

### `--max-budget-usd <amount>`
- Stop when API spend reaches limit
- Print mode only

```bash
claude -p "expensive task" --max-budget-usd 5.00
```

### Timeout Behavior
- **No built-in timeout** for `claude -p` itself
- **Caller must enforce** via shell timeout or other means:
  ```bash
  timeout 60s claude -p "query"
  ```
- **API timeout**: `API_TIMEOUT_MS` env var (default: 600000 / 10 min)
- **Bash timeout**: `BASH_DEFAULT_TIMEOUT_MS` (default: 120000 / 2 min)
- **Background task grace period**: 5 seconds after result returned before terminating

### `--no-session-persistence`
- Don't save session to disk
- Print mode only
- Session cannot be resumed

```bash
claude -p "one-off task" --no-session-persistence
```

### `--session-id <uuid>`
Use a specific session UUID:
```bash
claude -p "task" --session-id "550e8400-e29b-41d4-a716-446655440000"
```

### `--resume <session_id>` / `--continue`
Continue a prior conversation:
```bash
# Get session ID from first run
session_id=$(claude -p "analyze" --output-format json | jq -r '.session_id')

# Continue that session
claude -p "now focus on X" --resume "$session_id"

# Or continue most recent
claude -p "now focus on X" --continue
```

### `--fork-session`
Create a new session ID instead of reusing the original when resuming:
```bash
claude -p "new direction" --resume abc123 --fork-session
```

---

## 9. CI/Auth (Headless)

### `--bare` (Minimal Mode)
Skips auto-discovery:
- ❌ Hooks
- ❌ Skills
- ❌ Plugins
- ❌ MCP servers
- ❌ Auto-memory (CLAUDE.md)
- ✅ Bash, file read, file edit tools
- ✅ API access (must provide context explicitly)

**Recommended for CI/scripts** so they don't pick up local config:
```bash
claude --bare -p "check code" --allowedTools "Read,Glob,Bash"
```

**To provide context in bare mode**, use flags:
```bash
claude --bare \
  -p "query" \
  --system-prompt "You are a security auditor" \
  --add-dir /app /lib \
  --mcp-config ./mcp.json \
  --settings '{"model":"opus"}' \
  --allowedTools "Read,Bash"
```

### Authentication
**Method priority**:
1. `ANTHROPIC_API_KEY` (API key from env)
2. `apiKeyHelper` in `--settings` (script to obtain key)
3. OAuth / keychain (interactive only; skipped in `-p` mode)

```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
claude -p "task" --output-format json
```

### Bedrock / Vertex AI / Foundry / AWS Auth
```bash
# Bedrock
export CLAUDE_CODE_USE_BEDROCK=1
# Configure AWS credentials (IAM, credentials file, etc.)
claude -p "task" --model opus

# Vertex AI
export CLAUDE_CODE_USE_VERTEX=1
# Configure gcloud
claude -p "task" --model sonnet

# Foundry
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_API_KEY="..."
export ANTHROPIC_FOUNDRY_RESOURCE="my-resource"
claude -p "task"

# Claude Platform on AWS
export CLAUDE_CODE_USE_ANTHROPIC_AWS=1
export ANTHROPIC_AWS_WORKSPACE_ID="..."
# Configure AWS credentials
claude -p "task"
```

### Environment Variables (Headless)
```bash
ANTHROPIC_API_KEY              # API key for Anthropic API
ANTHROPIC_AUTH_TOKEN           # Custom Authorization header
ANTHROPIC_BASE_URL             # Gateway/proxy endpoint
ANTHROPIC_MODEL                # Model alias/name
API_TIMEOUT_MS                 # Timeout for API requests (default: 600000)
BASH_DEFAULT_TIMEOUT_MS        # Bash command timeout (default: 120000)
DISABLE_TELEMETRY              # Disable telemetry/surveys
CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS  # Max wait for background tasks (default: 600000)
CLAUDE_CODE_SKIP_PROMPT_HISTORY  # Skip saving prompt history
CLAUDE_CODE_SIMPLE             # Set by --bare (internal)
```

---

## 10. Exit Codes

### Exit Code Taxonomy
**No official, detailed exit code spec.** Observed behavior:

| Exit Code | Likely Meaning |
|-----------|---|
| `0` | Success |
| `1` | Generic error (auth, invalid args, tool deny, etc.) |
| `126` | Permission denied / tool not found |
| `127` | Command not found |

**Error detection**: Check `is_error` and `api_error_status` in JSON output instead of relying on exit codes alone.

### Example: Error Handling
```bash
output=$(claude -p "task" --output-format json)
exit_code=$?

if [ $exit_code -eq 0 ]; then
  is_error=$(echo "$output" | jq -r '.is_error')
  if [ "$is_error" = "true" ]; then
    echo "API error: $(echo "$output" | jq -r '.api_error_status')"
    exit 1
  fi
else
  echo "Command failed with exit code $exit_code"
  exit $exit_code
fi
```

---

## 11. Custom Agents / MCP in Headless

### Custom Agents (`--agents <json>`)
Define subagents on the fly:
```bash
claude -p "use code-reviewer" \
  --agents '{"code-reviewer":{"description":"Reviews code quality","prompt":"You are a code reviewer. Suggest improvements.","tools":["Read","Glob"]}}'
```

### MCP Servers (`--mcp-config <configs...>`)
Load MCP servers from JSON:
```bash
claude -p "query" \
  --mcp-config '{"postgres":{"command":"node","args":["db-mcp.js"]}}' \
  --allowedTools "mcp__postgres__*"
```

### Append System Prompt
```bash
claude -p "refactor" --append-system-prompt "Always use modern Python patterns"
```

### Replace System Prompt
```bash
claude -p "query" --system-prompt "You are a security auditor. Analyze code for vulnerabilities."
```

### System Prompt from File
```bash
claude -p "query" --system-prompt-file ./my-system-prompt.txt
```

---

## 12. Quick Examples

### JSON Cost Tracking (for scripts)
```bash
result=$(claude -p "summarize logs" --output-format json)
cost=$(echo "$result" | jq '.total_cost_usd')
echo "Cost for this run: \$$cost"
```

### Read-Only Code Review
```bash
git diff main | claude -p \
  --permission-mode dontAsk \
  --allowedTools "Read,Grep" \
  --append-system-prompt "Review for security issues, do not modify files" \
  --output-format json | jq '.result'
```

### Multi-Turn Conversation
```bash
# First query
session_id=$(claude -p "Analyze auth module" --output-format json | jq -r '.session_id')

# Second query in same session
claude -p "Find all callers of login()" --resume "$session_id" --output-format json | jq '.result'

# Third query
claude -p "Generate a refactoring plan" --resume "$session_id"
```

### Structured Output Extraction
```bash
claude -p "Extract all TODO comments" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"todos":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line":{"type":"number"},"text":{"type":"string"}}}}}}' \
  --allowedTools "Grep,Glob,Read" | jq '.structured_output'
```

### Stream Text in Real-Time
```bash
claude -p "Write deployment guide" \
  --output-format stream-json \
  --include-partial-messages \
  --verbose | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'
```

### CI with Timeout
```bash
timeout 30s claude -p "find bugs" \
  --bare \
  --permission-mode dontAsk \
  --allowedTools "Read,Bash(grep *)" \
  --output-format json | jq '.result'
```

---

## 13. Documentation & Links

**Official docs**:
- [Headless Mode](https://code.claude.com/docs/en/headless.md)
- [CLI Reference](https://code.claude.com/docs/en/cli-reference.md)
- [Model Configuration](https://code.claude.com/docs/en/model-config.md)
- [Agent SDK Overview](https://code.claude.com/docs/en/agent-sdk/overview.md)
- [Structured Outputs](https://code.claude.com/docs/en/agent-sdk/structured-outputs.md)
- [Environment Variables](https://code.claude.com/docs/en/env-vars.md)

**Installed version**: Claude Code v2.1.196
