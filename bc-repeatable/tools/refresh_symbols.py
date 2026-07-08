#!/usr/bin/env python3
import argparse
import json
import os
import pathlib
import subprocess
import threading
import time


PROJECT_PATH = pathlib.Path(__file__).resolve().parents[1]


def find_altool():
    configured = os.environ.get("ALTOOL_PATH")
    if configured:
        path = pathlib.Path(configured)
        if path.exists():
            return path
        raise SystemExit(f"ALTOOL_PATH does not exist: {path}")

    home = pathlib.Path.home()
    candidates = sorted(
        home.glob(".vscode/extensions/ms-dynamics-smb.al-*/bin/win32/altool.exe"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    raise SystemExit("Could not find AL altool.exe. Install or update the Microsoft AL Language extension in VS Code.")


class McpClient:
    def __init__(self, altool_path, project_path):
        self.next_id = 1
        self.stderr_lines = []
        self.process = subprocess.Popen(
            [
                str(altool_path),
                "launchmcpserver",
                str(project_path),
                "--transport",
                "stdio",
                "--disableTelemetry",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        threading.Thread(target=self._read_stderr, daemon=True).start()

    def _read_stderr(self):
        for line in self.process.stderr:
            self.stderr_lines.append(line.rstrip())

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def notify(self, method, params=None):
        self._send({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def call(self, method, params=None, timeout=300):
        request_id = self.next_id
        self.next_id += 1
        self._send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}})
        return self._read_response(request_id, timeout)

    def _send(self, payload):
        if self.process.poll() is not None:
            raise SystemExit("AL MCP server exited early:\n" + "\n".join(self.stderr_lines))
        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()

    def _read_response(self, request_id, timeout):
        deadline = time.time() + timeout
        while time.time() < deadline:
            line = self.process.stdout.readline()
            if not line:
                if self.process.poll() is not None:
                    raise SystemExit("AL MCP server exited before responding:\n" + "\n".join(self.stderr_lines))
                continue
            message = json.loads(line)
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise SystemExit(json.dumps(message["error"], indent=2))
            return message.get("result", {})
        raise SystemExit(f"Timed out waiting for AL MCP response to request {request_id}.")


def refresh_symbols(project_path, force):
    altool_path = find_altool()
    client = McpClient(altool_path, project_path)
    try:
        client.call(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "bc-repeatable-symbol-refresh", "version": "1.0.0"},
            },
        )
        client.notify("notifications/initialized")
        return client.call(
            "tools/call",
            {
                "name": "al_downloadsymbols",
                "arguments": {
                    "projectPath": str(project_path),
                    "globalSourcesOnly": True,
                    "force": force,
                    "useInteractiveLogin": False,
                },
            },
            timeout=600,
        )
    finally:
        client.close()


def unwrap_tool_result(result):
    content = result.get("content", [])
    if not content:
        return result
    first = content[0]
    if first.get("type") != "text":
        return result
    text = first.get("text", "")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return result


def main():
    parser = argparse.ArgumentParser(description="Refresh Business Central AL symbols unattended.")
    parser.add_argument("--project-path", default=str(PROJECT_PATH), help="AL project folder that contains app.json.")
    parser.add_argument("--no-force", action="store_true", help="Do not force re-download of cached symbols.")
    args = parser.parse_args()

    project_path = pathlib.Path(args.project_path).resolve()
    if not (project_path / "app.json").exists():
        raise SystemExit(f"app.json not found in project path: {project_path}")

    result = unwrap_tool_result(refresh_symbols(project_path, force=not args.no_force))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
