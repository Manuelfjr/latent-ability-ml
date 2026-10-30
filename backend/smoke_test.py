"""End-to-end checks against a running backend.

Usage:
    poetry run python -m backend.smoke_test                       # http://127.0.0.1:8765
    poetry run python -m backend.smoke_test https://...hf.space   # any deployment
    poetry run python -m backend.smoke_test --quick               # skip the slow birt/timeout checks
"""

from __future__ import annotations

import json
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid

BASE_URL = "http://127.0.0.1:8765"


def request(path: str, method: str = "GET", payload: object | None = None, timeout: float = 300) -> tuple[int, dict]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8") or "{}")


def execute(session_id: str, code: str) -> dict:
    return request("/execute", "POST", {"session_id": session_id, "code": code})[1]


def new_session(initial_code: str = "") -> str:
    session_id = f"smoke-{uuid.uuid4().hex[:8]}"
    status, body = request("/session/init", "POST", {"session_id": session_id, "initial_code": initial_code})
    assert status == 200 and body["ok"], body
    return session_id


def check_health() -> None:
    status, body = request("/health")
    assert status == 200 and body["ok"], body


def check_state_and_outputs() -> None:
    sid = new_session("import numpy as np\nseed = 7")
    assert execute(sid, "x = seed * 6")["success"]
    result = execute(sid, "print(x)\nx + 0.5")
    assert result["stdout"] == "42\n42.5\n", result
    result = execute(sid, "import pandas as pd\npd.DataFrame({'a': [1, 2]})")
    assert result["html"] and "<table" in result["html"][0], result
    result = execute(sid, "import matplotlib.pyplot as plt\nplt.plot([1, 2])\nplt.show()")
    assert len(result["figures"]) == 1 and not result["stderr"], result
    result = execute(sid, "display('hi')")
    assert result["stdout"] == "'hi'\n", result


def check_errors_are_reported() -> None:
    sid = new_session()
    result = execute(sid, "def f():\n    return 1 / 0\nf()")
    assert not result["success"] and "ZeroDivisionError" in result["stderr"], result
    assert "executor.py" not in result["stderr"], result["stderr"]
    assert "return 1 / 0" in result["stderr"], result["stderr"]
    result = execute(sid, "raise SystemExit")
    assert not result["success"], result
    assert execute(sid, "print('still alive')")["stdout"] == "still alive\n"
    status, body = request("/session/init", "POST", {"session_id": sid, "initial_code": "1/0"})
    assert status == 200 and body["init"]["success"] is False, body
    status, body = request("/execute", "POST", [1, 2])
    assert status == 400 and not body["ok"], body


def check_isolation() -> None:
    a, b = new_session(), new_session()
    results: dict[str, dict] = {}
    code_a = "import time, matplotlib.pyplot as plt\nplt.plot([1, 2])\nfor i in range(5):\n    print('A', i); time.sleep(0.2)"
    code_b = "import time\ntime.sleep(0.3)\nfor i in range(3):\n    print('B', i); time.sleep(0.2)"
    threads = [
        threading.Thread(target=lambda: results.__setitem__("a", execute(a, code_a))),
        threading.Thread(target=lambda: results.__setitem__("b", execute(b, code_b))),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert results["a"]["stdout"] == "".join(f"A {i}\n" for i in range(5)), results["a"]
    assert results["b"]["stdout"] == "".join(f"B {i}\n" for i in range(3)), results["b"]
    assert len(results["a"]["figures"]) == 1 and not results["b"]["figures"]
    assert "NameError" in execute(b, "code_a_variable_from_a")["stderr"]


def check_no_secrets() -> None:
    sid = new_session()
    result = execute(sid, "import os\nsorted(k for k in os.environ if 'PASSWORD' in k or k.startswith('WORKSHOP_ADMIN'))")
    assert result["stdout"] == "[]\n", result


def check_birt() -> None:
    sid = new_session()
    result = execute(sid, "from birt import Beta4\nprint('birt ok')")
    assert result["stdout"].strip().endswith("birt ok"), result


def check_timeout_keeps_state(expected_timeout: float) -> None:
    sid = new_session()
    execute(sid, "kept = 123")
    started = time.time()
    result = execute(sid, "while True:\n    pass")
    elapsed = time.time() - started
    assert not result["success"] and "KeyboardInterrupt" in result["stderr"], result
    assert elapsed < expected_timeout + 15, elapsed
    assert execute(sid, "print(kept)")["stdout"] == "123\n"


def main() -> None:
    global BASE_URL
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    quick = "--quick" in sys.argv
    if args:
        BASE_URL = args[0].rstrip("/")

    checks = [check_health, check_state_and_outputs, check_errors_are_reported, check_isolation, check_no_secrets]
    if not quick:
        timeout = float(request("/health")[1].get("execution_timeout_seconds", 0) or 0)
        checks.append(check_birt)
        if timeout and timeout <= 30:
            checks.append(lambda: check_timeout_keeps_state(timeout))

    failures = 0
    for check in checks:
        name = getattr(check, "__name__", "check_timeout_keeps_state").replace("<lambda>", "check_timeout_keeps_state")
        started = time.time()
        try:
            check()
            print(f"PASS  {name}  ({time.time() - started:.1f}s)")
        except Exception as error:
            failures += 1
            print(f"FAIL  {name}: {error!r}")
    print(f"\n{len(checks) - failures}/{len(checks)} checks passed against {BASE_URL}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
