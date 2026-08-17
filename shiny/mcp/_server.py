from __future__ import annotations

import asyncio
import json
import sys
from typing import Any, Dict, Optional, TextIO

from .. import __version__
from ._prompts import get_mcp_prompt, list_mcp_prompts
from ._resources import list_mcp_resources, read_mcp_resource
from ._tools import dispatch_mcp_tool, get_mcp_tools_definitions

SERVER_NAME = "shiny-mcp-server"
SERVER_VERSION = __version__


class ShinyMCPServer:
    def __init__(self) -> None:
        self.running = False

    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if not method:
            return None

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION,
                    },
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False},
                        "prompts": {"listChanged": False},
                    },
                },
            }

        elif method == "notifications/initialized":
            return None

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": get_mcp_tools_definitions(),
                },
            }

        elif method == "tools/call":
            name = params.get("name", "")
            args = params.get("arguments", {})
            try:
                result = await dispatch_mcp_tool(name, args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2),
                            }
                        ],
                        "isError": "error" in result
                        and result.get("error") is not None,
                    },
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Error: {e}"}],
                        "isError": True,
                    },
                }

        elif method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "resources": list_mcp_resources(),
                },
            }

        elif method == "resources/read":
            uri = params.get("uri", "")
            resource = read_mcp_resource(uri)
            if resource is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "contents": [resource],
                    },
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32602,
                        "message": f"Resource not found: {uri}",
                    },
                }

        elif method == "prompts/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "prompts": list_mcp_prompts(),
                },
            }

        elif method == "prompts/get":
            name = params.get("name", "")
            args = params.get("arguments", {})
            prompt = get_mcp_prompt(name, args)
            if prompt is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": prompt,
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32602,
                        "message": f"Prompt not found: {name}",
                    },
                }

        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found",
                },
            }
        return None

    async def run_stdio(
        self,
        stdin_stream: Optional[TextIO] = None,
        stdout_stream: Optional[TextIO] = None,
    ) -> None:
        reader_stream = stdin_stream or sys.stdin
        writer_stream = stdout_stream or sys.stdout

        self.running = True
        loop = asyncio.get_running_loop()

        while self.running:
            line = await loop.run_in_executor(None, reader_stream.readline)
            if not line:
                break
            line_str = line.strip()
            if not line_str:
                continue

            try:
                request = json.loads(line_str)
            except json.JSONDecodeError:
                continue

            response = await self.handle_request(request)
            if response is not None:
                writer_stream.write(json.dumps(response) + "\n")
                writer_stream.flush()


def run_server() -> None:
    server = ShinyMCPServer()
    try:
        asyncio.run(server.run_stdio())
    except (KeyboardInterrupt, SystemExit):
        pass
