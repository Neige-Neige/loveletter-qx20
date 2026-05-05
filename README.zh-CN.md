# loveletter-qx20

[English](README.md)

**Canon SELPHY QX20 的开源打印客户端。**

通过 WiFi Direct 从电脑直接向 Canon SELPHY QX20 打印照片，不需要 Canon 官方 App。


## 工作原理

Canon SELPHY QX20 使用 Canon 私有的 **CPNP** 协议，通过 WiFi Direct 与打印机通信。本项目实现了 QX20 打印所需的核心流程：

1. **WiFi Direct**：先连接到打印机的 `QX20-xxx` 热点
2. **UDP 8609**：设备发现、会话管理、状态读取
3. **动态 TCP 端口**：会话开始后由打印机返回，用于传输打印数据
4. **CPNP Write**：按块发送打印命令和 JPEG 数据，并检查 accepted bytes
5. **状态机等待**：严格等待打印机请求 probe 和 JPEG 后再发送对应数据

## 功能

- 打印任意图片，自动缩放为 `644x826`
- 自动转换为 QX20 可处理的 JPEG 格式
- 读取打印机状态，包括纸张、墨盒、错误码和支持尺寸范围
- 发现 WiFi Direct 下的 QX20
- 取消当前打印任务
- 提供 MCP Server，方便接入支持 MCP 的 AI 工具

## 安装依赖

```bash
pip install Pillow mcp
```

## 快速开始

先连接到 QX20 的 WiFi Direct 热点，然后运行：

```bash
# 查看设备和状态
python qx20.py

# 打印图片
python qx20.py photo.jpg
```

## Python API

```python
from qx20 import QX20Printer

printer = QX20Printer()

print(printer.discover())
print(printer.status())

printer.print_image("photo.jpg")
```

## MCP Server

在 MCP 客户端配置中加入：

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

可用工具：

- `qx20_discover`：发现打印机并返回设备信息
- `qx20_status`：读取纸张、墨盒、错误码和支持尺寸
- `qx20_print_image`：打印图片，参数为 `image_path`
- `qx20_cancel`：取消当前打印任务

## 协议流程

核心打印流程如下：

1. 通过 UDP 启动 CPNP 会话
2. 连接打印机返回的动态 TCP 端口
3. 协商 `MaxWriteSize = 33792`
4. 发送 `StartPrint`
5. 等待打印机请求 1 字节 probe：`offset=16`, `size=1`
6. 发送 PrintDataTransfer probe
7. 等待打印机请求完整 JPEG：`offset=0`, `size=jpeg_size`
8. 以一个逻辑 PrintDataTransfer 命令发送 JPEG，底层按 CPNP Write 分块
9. 轮询状态，进入收尾状态后发送 `EndPrint`

QX20 对状态机时机很敏感。即使 TCP 层 accepted bytes 全部正确，如果过早发送 probe 或 JPEG，打印机也可能只进入处理状态或直接报错。

## 注意事项

- 需要先手动连接到打印机的 WiFi Direct 热点
- 默认打印机 IP 为 `192.168.0.1`
- UDP 本地端口需要绑定 `8609`
- 当前实现面向 Canon SELPHY QX20，其他 SELPHY 型号未测试
- 这是逆向实现，与 Canon 官方无关

## 致谢

这个项目来自一次围绕 QX20 的逆向工程：抓包、反编译、状态机对齐、JPEG 格式调试，最后终于让纸吐出来。

Built with 🌀 Claude Code

Built with 🌊 Codex
## License

MIT

---

*Every sticker printed by QX20 is a love letter.*
