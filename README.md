# 🔬 Papers MCP — 让 AI 帮你读论文

<div align="center">

**一键连接 2 亿+ 学术论文，让 Claude 成为你的科研助手**

[![MCP](https://img.shields.io/badge/MCP-Server-blue?logo=anthropic)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.10+-green?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## ✨ 这是什么？

一个 [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 服务器，让你的 AI 助手（Claude Code / Claude Desktop）直接**搜索论文、查引用、读 PDF**——不需要离开对话窗口。

## 🚀 能做什么？

| 工具 | 功能 | 示例 |
|------|------|------|
| 🔍 `search_papers` | Semantic Scholar 搜索 2 亿+ 论文 | "帮我搜 RAG 相关论文" |
| 📄 `get_paper_detail` | 获取论文详情 + 摘要 + 引用数 | "第三篇的详情" |
| 📚 `get_citations` | 查看谁引用了这篇论文 | "这篇文章被谁引用了？" |
| 🔎 `search_arxiv` | 搜索 arXiv 最新预印本 | "arXiv 上最新的多模态论文" |
| 📥 `download_arxiv_pdf` | 下载论文 PDF | "下载这篇论文" |
| 📖 `read_pdf_text` | 提取 PDF 文本内容 | "帮我读一下方法部分" |

### 💬 使用演示

```
你: 搜一下 2024 年关于 large language model reasoning 的论文，要5篇

Claude: [调用 search_papers] 找到 5 篇论文：
  1. "Chain-of-Thought Reasoning..." (2024) - 引用 342 次
  2. "Scaling LLM Reasoning..." (2024) - 引用 189 次
  ...

你: 第一篇下载下来，读一下 Abstract

Claude: [调用 download_arxiv_pdf → read_pdf_text]
  Abstract: 本文提出了一种新的思维链推理方法...

你: 这篇论文被谁引用了？

Claude: [调用 get_citations] 共 342 篇引用论文：
  1. "Improved CoT via..." (2025)
  ...
```

## 📦 安装

### 1. 安装依赖

```bash
pip install fastmcp arxiv httpx PyMuPDF
```

### 2. 配置 Claude Code

```bash
claude mcp add papers -- cmd /c python /path/to/server.py
```

### 3. 配置 Claude Desktop

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "papers": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

### 4. 验证

重启 Claude，输入 `/mcp`，确认 `papers` 显示 ✅ Connected。

## 🔑 API 说明

| API | 是否需要 Key | 说明 |
|-----|-------------|------|
| Semantic Scholar | ❌ 免费 | 2 亿+ 论文，无需注册 |
| arXiv | ❌ 免费 | 开放预印本平台 |
| PyMuPDF | ❌ 本地 | PDF 文本提取 |

**零配置，零成本，开箱即用。**

## 🏗️ 技术栈

- **[FastMCP](https://github.com/jlowin/fastmcp)** — MCP 服务器框架
- **[Semantic Scholar API](https://api.semanticscholar.org/)** — 学术论文图谱
- **[arXiv API](https://info.arxiv.org/help/api/)** — 预印本搜索 + PDF 下载
- **[PyMuPDF](https://pymupdf.readthedocs.io/)** — PDF 文本提取

## 📁 项目结构

```
papers-mcp/
├── server.py          # MCP 服务器主文件
├── pyproject.toml     # 项目配置
├── README.md          # 你正在看的这个
├── .gitignore
└── LICENSE
```

## 💬 社区

- [Linux.do 讨论帖](https://linux.do) — 欢迎交流反馈！

## 📝 License

MIT License — 随便用，开心就好。

---

<div align="center">

**⭐ 觉得有用？点个 Star 支持一下！**

Made with ❤️ by [@xwmxcz](https://github.com/xwmxcz)

</div>
