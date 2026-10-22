import json
import os
import pathlib
import sys
import threading

ROOT = pathlib.Path(r"E:\GPT\Tools\DC-Replacement-20261022")
VERIFIED = ROOT / "verified-files-v2"
sys.path.insert(0, str(VERIFIED))

from protocol_client import Client

VERSION = "1.0.0"

for name in ("CONTROL_PLANE_API_KEY", "OPENAI_ADMIN_KEY", "OPENAI_API_KEY"):
    os.environ.pop(name, None)

VERIFIED_ARGV = [
    sys.executable,
    str(ROOT / "config" / "code-files-tunnel-bootstrap.py"),
]

WINDOWS_ARGV = [
    str(ROOT / "windows-mcp-server" / "windows-mcp-server.exe"),
    "stdio",
    "--toolsets",
    "screen,interaction,apps,testing",
    "--exclude-tools",
    "Type,Move,Shortcut,MultiSelect,MultiEdit,Clipboard,Process,Notification,Registry,ScheduledTask,PowerShell,LaunchExecutable,FileSystem,Scrape,Package,Credentials",
    "--policy-config",
    str(ROOT / "profiles" / "YASSIN-ENGINEERING" / "YASSIN_ENGINEERING_AUDIT_POLICY.json"),
    "--record-codec",
    "h264",
    "--record-fps",
    "4",
    "--log-file",
    str(ROOT / "logs" / "windows-engineering-gateway.log"),
]

children = {
    "verified": Client(VERIFIED_ARGV, "yassin-gateway-verified"),
    "windows": Client(WINDOWS_ARGV, "yassin-gateway-windows"),
}

owners = {}
tool_cache = []
lock = threading.Lock()


def init_children():
    manifests = {}
    for key, client in children.items():
        reply = client.init()
        if "error" in reply:
            raise RuntimeError(f"{key} initialize failed: {reply['error']}")
        listed = client.rpc("tools/list", {})
        if "error" in listed:
            raise RuntimeError(f"{key} tools/list failed: {listed['error']}")
        tools = listed.get("result", {}).get("tools", [])
        manifests[key] = tools

    seen = {}
    merged = []
    for key in ("verified", "windows"):
        for tool in manifests[key]:
            name = tool.get("name")
            if not name:
                raise RuntimeError(f"{key} served an unnamed tool")
            if name in seen:
                raise RuntimeError(f"tool collision: {name} from {seen[name]} and {key}")
            seen[name] = key
            merged.append(tool)

    owners.clear()
    owners.update(seen)
    tool_cache.clear()
    tool_cache.extend(merged)


def send(payload):
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def result(req_id, value):
    send({"jsonrpc": "2.0", "id": req_id, "result": value})


def error(req_id, code, message, data=None):
    body = {"code": code, "message": message}
    if data is not None:
        body["data"] = data
    send({"jsonrpc": "2.0", "id": req_id, "error": body})


def handle(request):
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params") or {}

    if method == "initialize":
        requested = params.get("protocolVersion") or "2025-11-25"
        result(
            req_id,
            {
                "protocolVersion": requested,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "YASSIN Gateway MCP", "version": VERSION},
                "instructions": (
                    "Use Verified Files for source/file edits and authorized command sessions. "
                    "Use Windows tools only for constrained GUI/QA work. "
                    "The gateway itself has no file, shell, or GUI authority."
                ),
            },
        )
        return

    if method == "notifications/initialized":
        return

    if method == "ping":
        result(req_id, {})
        return

    if method == "tools/list":
        result(req_id, {"tools": tool_cache})
        return

    if method == "tools/call":
        tool_name = params.get("name")
        owner = owners.get(tool_name)
        if owner is None:
            error(req_id, -32602, f"unknown tool: {tool_name}")
            return
        with lock:
            reply = children[owner].rpc("tools/call", params)
        if "error" in reply:
            send({"jsonrpc": "2.0", "id": req_id, "error": reply["error"]})
        else:
            result(req_id, reply.get("result", {}))
        return

    if method == "resources/list":
        result(req_id, {"resources": []})
        return

    if method == "prompts/list":
        result(req_id, {"prompts": []})
        return

    if req_id is not None:
        error(req_id, -32601, f"method not supported by gateway: {method}")


def main():
    init_children()
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                handle(request)
            except Exception as exc:
                req_id = request.get("id") if isinstance(request, dict) else None
                if req_id is not None:
                    error(req_id, -32603, "gateway internal error", {"type": type(exc).__name__, "message": str(exc)})
    finally:
        for client in children.values():
            try:
                client.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
