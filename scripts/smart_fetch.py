#!/usr/bin/env python3
"""
smart_fetch.py — 万能内容抓取脚本（deep-learn skill 核心组件）

自动识别平台 → 选择最优抓取策略 → 多级 fallback → 输出 Markdown

支持平台：微信公众号、B站、YouTube、arXiv、小红书、X/Twitter、通用网页
首次运行自动安装依赖（x-reader + playwright）

用法:
    python3 smart_fetch.py <url>                    # 输出到 stdout
    python3 smart_fetch.py <url> -o output.md       # 输出到文件
    python3 smart_fetch.py <url1> <url2> ...        # 批量抓取
    python3 smart_fetch.py --setup                  # 仅安装依赖
    python3 smart_fetch.py --check                  # 检查依赖状态
"""

import sys
import os
import re
import subprocess
import shutil
import json
from pathlib import Path
from urllib.parse import urlparse

# ─── 配置 ───────────────────────────────────────────────
SKILL_DIR = Path(__file__).resolve().parent.parent
VENV_DIR = Path.home() / ".openclaw" / "workspace" / "x-reader-env"
VENV_PYTHON = VENV_DIR / "bin" / "python3"
VENV_ACTIVATE = VENV_DIR / "bin" / "activate"
X_READER_BIN = VENV_DIR / "bin" / "x-reader"

# B站 BV 号 → YouTube 映射（常见的搬运/原版对应）
# 用户可以扩展这个映射
BILIBILI_YOUTUBE_MAP = {}


# ─── 平台识别 ────────────────────────────────────────────
def detect_platform(url: str) -> str:
    """识别 URL 属于哪个平台"""
    host = urlparse(url).hostname or ""
    host = host.lower().replace("www.", "")

    if "mp.weixin.qq.com" in host or "weixin.qq.com" in host:
        return "wechat"
    elif "bilibili.com" in host or "b23.tv" in host:
        return "bilibili"
    elif "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    elif "arxiv.org" in host:
        return "arxiv"
    elif "xiaohongshu.com" in host or "xhslink.com" in host:
        return "xiaohongshu"
    elif "twitter.com" in host or "x.com" in host:
        return "twitter"
    elif host.endswith(".pdf") or url.endswith(".pdf"):
        return "pdf"
    else:
        return "web"


# ─── 依赖管理 ────────────────────────────────────────────
def check_dependencies() -> dict:
    """检查所有依赖的安装状态"""
    status = {
        "x-reader": X_READER_BIN.exists(),
        "venv": VENV_DIR.exists(),
        "playwright": False,
        "summarize": shutil.which("summarize") is not None,
    }

    # 检查 playwright
    if status["venv"]:
        try:
            result = subprocess.run(
                [str(VENV_PYTHON), "-c", "import playwright; print('ok')"],
                capture_output=True, text=True, timeout=10
            )
            status["playwright"] = result.stdout.strip() == "ok"
        except Exception:
            pass

    return status


def setup_dependencies(force=False):
    """安装所有依赖"""
    print("🔧 检查依赖...")
    status = check_dependencies()

    if all(status.values()) and not force:
        print("✅ 所有依赖已就绪")
        return True

    # 1. 创建 venv
    if not status["venv"]:
        print("📦 创建 Python 虚拟环境...")
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            check=True
        )

    # 2. 安装 x-reader
    if not status["x-reader"]:
        print("📦 安装 x-reader（万能内容读取器）...")
        subprocess.run(
            [str(VENV_PYTHON), "-m", "pip", "install",
             "git+https://github.com/runesleo/x-reader.git@fdd582ccd39c70375d0dba176faeea2e59159ba9", "-q"],
            check=True
        )

    # 3. 安装 playwright
    if not status["playwright"]:
        print("📦 安装 Playwright（浏览器引擎，用于微信等需要渲染的页面）...")
        subprocess.run(
            [str(VENV_PYTHON), "-m", "pip", "install",
             "x-reader[browser]", "-q"],
            check=True
        )
        print("📦 安装 Chromium...")
        subprocess.run(
            [str(VENV_DIR / "bin" / "playwright"), "install", "chromium"],
            check=True
        )

    print("✅ 所有依赖安装完成")
    return True


# ─── 抓取策略 ────────────────────────────────────────────
def fetch_with_x_reader(url: str) -> str | None:
    """用 x-reader 抓取"""
    if not X_READER_BIN.exists():
        return None
    try:
        result = subprocess.run(
            [str(X_READER_BIN), url],
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "PATH": f"{VENV_DIR / 'bin'}:{os.environ.get('PATH', '')}"}
        )
        if result.returncode == 0 and result.stdout.strip():
            # 过滤掉日志行（loguru 格式）
            lines = result.stdout.split("\n")
            content_lines = [l for l in lines if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}', l)]
            content = "\n".join(content_lines).strip()
            if len(content) > 100:
                return content
    except Exception as e:
        print(f"  ⚠️ x-reader 失败: {e}", file=sys.stderr)
    return None


def fetch_with_summarize(url: str) -> str | None:
    """用 summarize skill 抓取（适合 YouTube 长视频字幕）"""
    if not shutil.which("summarize"):
        return None
    try:
        result = subprocess.run(
            ["summarize", url, "--youtube", "auto", "--length", "xxl", "--extract-only"],
            capture_output=True, text=True, timeout=180
        )
        if result.returncode == 0 and result.stdout.strip():
            content = result.stdout.strip()
            if len(content) > 200:
                return content
    except Exception as e:
        print(f"  ⚠️ summarize 失败: {e}", file=sys.stderr)
    return None


def extract_bilibili_bvid(url: str) -> str | None:
    """从 B站 URL 提取 BV 号"""
    match = re.search(r'(BV[A-Za-z0-9]+)', url)
    return match.group(1) if match else None


def search_youtube_equivalent(bilibili_title: str) -> str | None:
    """尝试找到 B站视频对应的 YouTube 原版（通过标题搜索）"""
    # 这个功能需要 Agent 层面配合，脚本层面做不到完美搜索
    # 返回 None 表示需要 Agent 介入
    return None


def fetch_bilibili(url: str) -> tuple[str | None, list[str]]:
    """
    B站视频抓取策略：
    1. x-reader 拿简介和元数据
    2. 提示 Agent：B站无法直接拿字幕，需要找 YouTube 原版
    
    返回: (content, hints)
    """
    hints = []
    content = fetch_with_x_reader(url)

    if content:
        # 检查内容中是否有 YouTube 原始链接
        yt_match = re.search(r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]+)', content)
        if yt_match:
            yt_url = yt_match.group(0)
            hints.append(f"YOUTUBE_ORIGINAL:{yt_url}")
            # 尝试用 summarize 拿完整字幕
            transcript = fetch_with_summarize(yt_url)
            if transcript:
                content = content + "\n\n---\n## 完整字幕（来自 YouTube 原版）\n\n" + transcript
        else:
            hints.append(
                "BILIBILI_NO_SUBTITLE:B站视频无法直接提取字幕。"
                "如果这是搬运/翻译视频，请搜索 YouTube 原版链接，"
                "然后用 summarize 工具提取字幕：\n"
                "  summarize '<youtube_url>' --youtube auto --length xxl --extract-only"
            )

    return content, hints


def fetch_wechat(url: str) -> tuple[str | None, list[str]]:
    """
    微信公众号抓取策略：
    1. x-reader（Jina → Playwright fallback）
    2. wechat-article skill
    3. read-wechat-article skill
    """
    hints = []

    # 策略 1: x-reader
    print("  📡 尝试 x-reader...", file=sys.stderr)
    content = fetch_with_x_reader(url)
    if content and len(content) > 200:
        return content, hints

    # 策略 2: wechat-article skill
    print("  📡 尝试 wechat-article skill...", file=sys.stderr)
    wechat_script = Path.home() / ".openclaw" / "workspace" / "skills" / "wechat-article" / "scripts" / "wechat_article.py"
    if wechat_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(wechat_script), url],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0 and len(result.stdout.strip()) > 200:
                return result.stdout.strip(), hints
        except Exception:
            pass

    # 策略 3: read-wechat-article skill
    print("  📡 尝试 read-wechat-article skill...", file=sys.stderr)
    read_script = Path.home() / ".openclaw" / "workspace" / "skills" / "read-wechat-article"
    if read_script.exists():
        for py_file in read_script.glob("*.py"):
            try:
                result = subprocess.run(
                    [sys.executable, str(py_file), url],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode == 0 and len(result.stdout.strip()) > 200:
                    return result.stdout.strip(), hints
            except Exception:
                continue

    hints.append(
        "WECHAT_FETCH_FAILED:所有微信抓取方式均失败。"
        "可能原因：文章需要登录/已被删除/反爬限制。"
        "请让用户手动复制文章内容发送。"
    )
    return None, hints


def fetch_youtube(url: str) -> tuple[str | None, list[str]]:
    """
    YouTube 视频抓取策略：
    1. summarize（拿完整字幕，首选）
    2. x-reader（拿简介 + 元数据）
    """
    hints = []

    # 策略 1: summarize（完整字幕）
    print("  📡 尝试 summarize 提取字幕...", file=sys.stderr)
    content = fetch_with_summarize(url)
    if content:
        return content, hints

    # 策略 2: x-reader
    print("  📡 尝试 x-reader...", file=sys.stderr)
    content = fetch_with_x_reader(url)
    if content:
        hints.append("YOUTUBE_PARTIAL:仅获取到视频简介，未能提取完整字幕。内容可能不完整。")
        return content, hints

    return None, hints


def fetch_arxiv(url: str) -> tuple[str | None, list[str]]:
    """arXiv 论文：提示 Agent 使用 pdf 工具"""
    hints = [
        f"ARXIV_USE_PDF:arXiv 论文建议使用 Agent 的 pdf 工具直接分析：\n"
        f"  pdf(url='{url.replace('/abs/', '/pdf/') + '.pdf' if '/abs/' in url else url}')"
    ]
    # 也尝试 x-reader 拿摘要
    content = fetch_with_x_reader(url)
    return content, hints


def fetch_generic(url: str) -> tuple[str | None, list[str]]:
    """通用网页抓取"""
    content = fetch_with_x_reader(url)
    return content, []


# ─── 统一入口 ────────────────────────────────────────────
def smart_fetch(url: str) -> dict:
    """
    智能抓取入口。返回：
    {
        "url": "...",
        "platform": "bilibili|wechat|youtube|...",
        "content": "Markdown 内容" | None,
        "hints": ["提示信息"],
        "success": True/False
    }
    """
    platform = detect_platform(url)
    print(f"🔍 [{platform}] {url}", file=sys.stderr)

    if platform == "bilibili":
        content, hints = fetch_bilibili(url)
    elif platform == "wechat":
        content, hints = fetch_wechat(url)
    elif platform == "youtube":
        content, hints = fetch_youtube(url)
    elif platform == "arxiv":
        content, hints = fetch_arxiv(url)
    else:
        content, hints = fetch_generic(url)

    success = content is not None and len(content) > 100
    return {
        "url": url,
        "platform": platform,
        "content": content,
        "hints": hints,
        "success": success
    }


# ─── CLI ─────────────────────────────────────────────────
def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    if "--setup" in args:
        setup_dependencies(force=True)
        sys.exit(0)

    if "--check" in args:
        status = check_dependencies()
        for tool, ok in status.items():
            emoji = "✅" if ok else "❌"
            print(f"  {emoji} {tool}")
        if not all(status.values()):
            print("\n运行 --setup 安装缺失的依赖")
        sys.exit(0 if all(status.values()) else 1)

    # 确保依赖已安装
    status = check_dependencies()
    if not status["x-reader"]:
        print("⚠️ 依赖未安装，正在自动安装...", file=sys.stderr)
        setup_dependencies()

    # 解析参数
    output_file = None
    urls = []
    i = 0
    while i < len(args):
        if args[i] == "-o" and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i].startswith("http://") or args[i].startswith("https://"):
            urls.append(args[i])
            i += 1
        else:
            print(f"⚠️ 跳过非 HTTP(S) 输入: {args[i]}", file=sys.stderr)
            i += 1

    results = []
    for url in urls:
        result = smart_fetch(url)
        results.append(result)

        if result["success"]:
            print(f"✅ [{result['platform']}] 成功", file=sys.stderr)
        else:
            print(f"❌ [{result['platform']}] 失败", file=sys.stderr)

        for hint in result["hints"]:
            print(f"  💡 {hint}", file=sys.stderr)

    # 输出
    output_parts = []
    for r in results:
        if r["content"]:
            output_parts.append(f"<!-- source: {r['url']} | platform: {r['platform']} -->\n")
            output_parts.append(r["content"])
            output_parts.append("\n\n---\n\n")

    output = "\n".join(output_parts)

    if output_file:
        # 安全检查：禁止绝对路径和路径遍历
        out_path = Path(output_file)
        if out_path.is_absolute() or ".." in out_path.parts:
            print("❌ 安全限制：输出路径不能是绝对路径或包含 '..'", file=sys.stderr)
            sys.exit(1)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"📁 已保存到 {output_file}", file=sys.stderr)
    else:
        print(output)

    # 输出 JSON 摘要到 stderr
    summary = {
        "total": len(results),
        "success": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "hints": [h for r in results for h in r["hints"]]
    }
    print(f"\n📊 抓取结果: {summary['success']}/{summary['total']} 成功", file=sys.stderr)


if __name__ == "__main__":
    main()
