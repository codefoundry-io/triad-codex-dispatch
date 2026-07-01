import json, sys
sys.path.insert(0, "bin")
from _common import extract_claude_answer

def test_plain_result():
    env = {"type":"result","subtype":"success","is_error":False,"result":"hello"}
    ans, err = extract_claude_answer(json.dumps(env), "")
    assert (ans, err) == ("hello", None)

def test_structured_output_returned_as_json():
    env = {"type":"result","subtype":"success","is_error":False,"result":"",
           "structured_output":{"todos":["a","b"]}}
    ans, err = extract_claude_answer(json.dumps(env), "")
    assert err is None
    assert json.loads(ans) == {"todos":["a","b"]}

def test_schema_retries_exhausted_is_extraction_error():
    env = {"type":"result","subtype":"error_max_structured_output_retries",
           "is_error":False,"result":""}
    ans, err = extract_claude_answer(json.dumps(env), "")
    assert ans == ""
    assert "schema-retries-exhausted" in err

def test_is_error_still_surfaces():
    env = {"type":"result","is_error":True,"api_error_status":401,"result":"Not logged in"}
    ans, err = extract_claude_answer(json.dumps(env), "")
    assert ans == ""
    assert "is_error=true" in err and "401" in err
