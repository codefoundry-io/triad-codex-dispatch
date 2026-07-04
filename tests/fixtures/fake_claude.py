# tests/fixtures/fake_claude.py  — emulates `claude -p --output-format json`
# Mode is read from the FAKE_MODE env var so the wrapper (which owns the argv) needn't pass it.
import json, os, sys
def main():
    argv_file = os.environ.get("ARGV_FILE")
    if argv_file:
        open(argv_file, "w", encoding="utf-8").write("\n".join(sys.argv[1:]))
    mode = os.environ.get("FAKE_MODE", "success")   # success|is_error|is_error_success|permission_denied|structured|schema_retries|schema_retries_nonzero|schema_retries_server_stderr|empty
    if mode == "success":
        print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"FAKE-OK"}))
    elif mode == "structured":
        print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"",
                          "structured_output":{"todos":["x"]}}))
    elif mode == "schema_retries":
        print(json.dumps({"type":"result","subtype":"error_max_structured_output_retries",
                          "is_error":False,"result":""}))
    elif mode == "schema_retries_nonzero":
        print(json.dumps({"type":"result","subtype":"error_max_structured_output_retries",
                          "is_error":False,"result":""}))
        return 1
    elif mode == "schema_retries_server_stderr":
        print("model overloaded", file=sys.stderr)
        print(json.dumps({"type":"result","subtype":"error_max_structured_output_retries",
                          "is_error":False,"result":""}))
        return 1
    elif mode == "is_error":
        print(json.dumps({"type":"result","is_error":True,"api_error_status":401,
                          "result":"Failed to authenticate. API Error: 401 Invalid authentication credentials"}))
        return 1
    elif mode == "is_error_success":
        print(json.dumps({"type":"result","subtype":"success","is_error":True,"api_error_status":401,
                          "result":"Failed to authenticate. API Error: 401 Invalid authentication credentials"}))
    elif mode == "permission_denied":
        print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"",
                          "permission_denials":[{"tool_name":"Write","reason":"blocked by policy"}]}))
    elif mode == "empty":
        pass  # no stdout → extraction-error
    return 0
if __name__ == "__main__":
    sys.exit(main())
