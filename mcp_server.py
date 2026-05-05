"""
loveletter-qx20 MCP Server
Exposes Canon SELPHY QX20 printer as MCP tools.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from qx20 import QX20Printer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

mcp = Server("loveletter-qx20")
printer = QX20Printer()


@mcp.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="qx20_discover",
            description="Discover the Canon SELPHY QX20 printer on WiFi Direct and return its device ID.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="qx20_status",
            description="Read the Canon SELPHY QX20 printer status: paper, ink, error code, and supported image size range.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="qx20_print_image",
            description="Print an image to the Canon SELPHY QX20. The image will be resized to 644x826 and converted to the required JPEG format automatically.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Absolute path to the image file to print.",
                    },
                },
                "required": ["image_path"],
            },
        ),
        Tool(
            name="qx20_cancel",
            description="Cancel the current print job on the Canon SELPHY QX20.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@mcp.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "qx20_discover":
            device_id = await asyncio.to_thread(printer.discover)
            return [TextContent(type="text", text=f"Printer found: {device_id}")]

        elif name == "qx20_status":
            status = await asyncio.to_thread(printer.status)
            result = {
                "paper": status.paper,
                "ink": status.ink,
                "error": status.error,
                "image_range": f"{status.min_w}x{status.min_h} ~ {status.max_w}x{status.max_h}",
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "qx20_print_image":
            image_path = arguments.get("image_path", "")
            if not image_path or not Path(image_path).exists():
                return [TextContent(type="text", text=f"Image not found: {image_path}")]

            messages = []
            def on_progress(stage, detail):
                messages.append(f"[{stage}] {detail}")

            success = await asyncio.to_thread(printer.print_image, image_path, on_progress)
            log = "\n".join(messages)
            if success:
                return [TextContent(type="text", text=f"Print successful!\n{log}")]
            else:
                return [TextContent(type="text", text=f"Print failed.\n{log}")]

        elif name == "qx20_cancel":
            await asyncio.to_thread(printer.cancel)
            return [TextContent(type="text", text="Print job cancelled.")]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.exception(f"Tool {name} failed")
        return [TextContent(type="text", text=f"Error: {e}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, mcp.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
