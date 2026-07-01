# tests/fixtures/fake_claude.py  — emulates `claude -p --output-format json`
# Mode is read from the FAKE_MODE env var so the wrapper (which owns the argv) needn't pass it.
import json, os, sys
def main():
    mode = os.environ.get("FAKE_MODE", "success")   # success|is_error|structured|empty
    if mode == "success":
        print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"FAKE-OK"}))
    elif mode == "structured":
        print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"",
                          "structured_output":{"todos":["x"]}}))
    elif mode == "is_error":
        print(json.dumps({"type":"result","is_error":True,"api_error_status":401,
                          "result":"Not logged in"}))
    elif mode == "empty":
        pass  # no stdout → extraction-error
    return 0
if __name__ == "__main__":
    sys.exit(main())
