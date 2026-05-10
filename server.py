"""Academic Papers MCP Server - 搜论文/查引用/读摘要"""

from fastmcp import FastMCP
import arxiv
import httpx
import json
import time

mcp = FastMCP("PapersMCP")

# ── Semantic Scholar API (with retry for 429) ──
S2_BASE = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = "paperId,title,abstract,year,citationCount,authors,externalIds,url"
S2_RETRIES = 3
S2_WAIT = 2  # seconds


def _s2_get(url: str, params: dict) -> dict | None:
    """Semantic Scholar GET with 429 retry."""
    for attempt in range(S2_RETRIES):
        resp = httpx.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 429:
            wait = S2_WAIT * (attempt + 1)
            time.sleep(wait)
            continue
        return {"error": f"{resp.status_code}: {resp.text[:200]}"}
    return {"error": "429: Too Many Requests after retries"}


@mcp.tool()
def search_papers(query: str, limit: int = 10) -> str:
    """语义搜索学术论文（Semantic Scholar，5B+论文库）

    Args:
        query: 搜索关键词或句子（建议用英文）
        limit: 返回结果数量，默认10
    """
    data = _s2_get(f"{S2_BASE}/paper/search", {"query": query, "limit": min(limit, 20), "fields": S2_FIELDS})
    if "error" in data:
        return f"搜索失败: {data['error']}"
    papers = data.get("data", [])
    if not papers:
        return "未找到相关论文"
    results = []
    for i, p in enumerate(papers, 1):
        authors = ", ".join(a["name"] for a in (p.get("authors") or [])[:3])
        results.append(
            f"{i}. [{p.get('title','')}]({p.get('url','')})\n"
            f"   作者: {authors} | 年份: {p.get('year','')} | 引用: {p.get('citationCount',0)}\n"
            f"   摘要: {(p.get('abstract') or '无')[:200]}..."
        )
    return "\n\n".join(results)


@mcp.tool()
def get_paper_detail(paper_id: str) -> str:
    """获取论文详情（传入Semantic Scholar paperId或arXiv ID如2301.07041）

    Args:
        paper_id: Semantic Scholar paperId 或 arXiv ID
    """
    if paper_id.startswith("10.") or paper_id.startswith("ARXIV:"):
        pid = paper_id
    elif paper_id.replace(".", "").isdigit() and len(paper_id) >= 10:
        pid = f"ARXIV:{paper_id}"
    else:
        pid = paper_id
    data = _s2_get(
        f"{S2_BASE}/paper/{pid}",
        {"fields": S2_FIELDS + ",references.title,references.citationCount,tldr"},
    )
    if "error" in data:
        return f"查询失败: {data['error']}"
    p = data
    authors = ", ".join(a["name"] for a in (p.get("authors") or [])[:5])
    refs = (p.get("references") or [])[:10]
    ref_lines = [f"  - {r['title']} (引用:{r.get('citationCount',0)})" for r in refs]
    tldr = (p.get("tldr") or {}).get("text", "无")
    return (
        f"# {p.get('title','')}\n\n"
        f"**作者**: {authors}\n"
        f"**年份**: {p.get('year','')} | **引用**: {p.get('citationCount',0)}\n"
        f"**链接**: {p.get('url','')}\n\n"
        f"## 摘要\n{p.get('abstract','无')}\n\n"
        f"## TL;DR\n{tldr}\n\n"
        f"## 主要参考文献\n" + "\n".join(ref_lines)
    )


@mcp.tool()
def get_citations(paper_id: str, limit: int = 10) -> str:
    """查看谁引用了这篇论文

    Args:
        paper_id: 论文ID
        limit: 返回数量
    """
    data = _s2_get(
        f"{S2_BASE}/paper/{paper_id}/citations",
        {"fields": "title,year,citationCount,authors", "limit": min(limit, 20)},
    )
    if "error" in data:
        return f"查询失败: {data['error']}"
    data = data.get("data", [])
    lines = []
    for i, item in enumerate(data, 1):
        p = item.get("citingPaper", {})
        authors = ", ".join(a["name"] for a in (p.get("authors") or [])[:2])
        lines.append(f"{i}. {p.get('title','')} ({p.get('year','')}) - {authors}")
    return "\n".join(lines) if lines else "暂无引用"


@mcp.tool()
def search_arxiv(query: str, max_results: int = 5) -> str:
    """搜索 arXiv 预印本论文

    Args:
        query: 搜索关键词
        max_results: 返回数量
    """
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=min(max_results, 10), sort_by=arxiv.SortCriterion.Relevance)
    results = []
    for i, paper in enumerate(client.results(search), 1):
        authors = ", ".join(str(a) for a in paper.authors[:3])
        results.append(
            f"{i}. {paper.title}\n"
            f"   作者: {authors} | 发布: {paper.published.strftime('%Y-%m-%d')}\n"
            f"   arXiv: {paper.entry_id}\n"
            f"   摘要: {paper.summary[:200]}..."
        )
    return "\n\n".join(results) if results else "未找到论文"


@mcp.tool()
def download_arxiv_pdf(arxiv_id: str, save_dir: str = ".") -> str:
    """下载 arXiv 论文 PDF 到本地

    Args:
        arxiv_id: arXiv ID（如 2301.07041）
        save_dir: 保存目录，默认当前目录
    """
    import os
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    papers = list(client.results(search))
    if not papers:
        return f"未找到 arXiv:{arxiv_id}"
    paper = papers[0]
    path = paper.download_pdf(dirpath=save_dir)
    return f"已下载: {path}\n标题: {paper.title}"


@mcp.tool()
def read_pdf_text(pdf_path: str, max_pages: int = 10) -> str:
    """提取本地 PDF 文件的文本内容

    Args:
        pdf_path: PDF 文件路径
        max_pages: 最多读取页数
    """
    try:
        import fitz
    except ImportError:
        return "需要安装 PyMuPDF: pip install PyMuPDF"
    doc = fitz.open(pdf_path)
    texts = []
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        texts.append(f"--- 第{i+1}页 ---\n{page.get_text()}")
    doc.close()
    return "\n".join(texts) if texts else "PDF无法提取文本（可能是扫描件）"


if __name__ == "__main__":
    mcp.run(transport="stdio")
