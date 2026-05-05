# loveletter-qx20

[中文版](README.zh-CN.md)

**First ever open-source Canon SELPHY QX20 printer driver.**

Print photos directly from your computer to a Canon SELPHY QX20 via WiFi Direct — no official Canon app needed.



## How it works

The Canon SELPHY QX20 uses a proprietary protocol called **CPNP** (Canon Proprietary Network Protocol) over WiFi Direct. This library implements the full CPNP stack:

1. **WiFi Direct** — Connect to the printer's `QX20-xxx` hotspot
2. **UDP 8609** — Device discovery, session management, status polling
3. **Dynamic TCP port** — Negotiated during session start for data transfer
4. **CPNP Write** — Chunked data transfer with acknowledgment
5. **State machine** — Wait for printer readiness at each step

## Features

- 🖨️ Print any image (auto-resized to 644×826, converted to 4:4:4 JPEG)
- 📊 Read printer status (paper, ink, error codes)
- 🔍 Discover printer on WiFi Direct
- ❌ Cancel print jobs
- 🔌 MCP server for AI integration

## Requirements

```
pip install Pillow mcp
```

## Quick Start

### CLI
```bash
# Connect to QX20 WiFi first, then:

# Check printer status
python qx20.py

# Print an image
python qx20.py photo.jpg
```

### Python API
```python
from qx20 import QX20Printer

printer = QX20Printer()
print(printer.discover())      # "MFG:Canon;MDL:SELPHY QX20;..."
print(printer.status())        # PrinterStatus(paper=1, ink=18, error=0, ...)
printer.print_image("photo.jpg")
```

### MCP Server
```json
{
  "mcpServers": {
    "qx20": {
      "command": "python3",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/loveletter-qx20"
    }
  }
}
```

Tools:
- `qx20_discover` — Find the printer
- `qx20_status` — Read paper/ink/error status
- `qx20_print_image` — Print an image (accepts `image_path`)
- `qx20_cancel` — Cancel current job

## Protocol Notes

The core print sequence is:

1. Start a CPNP UDP session and connect to the negotiated TCP port
2. Negotiate `MaxWriteSize = 33792`
3. Send `StartPrint`
4. Wait until the printer requests the 1-byte probe (`offset=16`, `size=1`)
5. Send the PrintDataTransfer probe
6. Wait until the printer requests the full JPEG (`offset=0`, `size=jpeg_size`)
7. Send PrintDataTransfer as one logical command, chunked through CPNP Write
8. Poll status until finalization, then send `EndPrint`

## How We Did It

Three days, two AIs (Claude Opus4.6 + Codex GPT5.5), one human, and countless QX20 power button presses:

1. **Day 1** — Fixed iOS app MCP/TTS bugs, started QX20 reverse engineering
2. **Day 2** — Decompiled Canon's Android app (APK), found CPNP protocol, established full UDP+TCP communication
3. **Day 3** — iPhone pcap capture, state machine alignment, JPEG format tuning, **first successful print** 🎉

## Credits

Built with 🌀 Claude Code

Built with 🌊 Codex

## License

MIT

---

*Every sticker printed by QX20 is a love letter.* 💌
