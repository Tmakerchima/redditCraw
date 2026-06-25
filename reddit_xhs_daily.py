#!/usr/bin/env python3
"""Generate a Xiaohongshu-ready daily digest from r/artificial.

Outputs Markdown plus 7 SVG cards (cover, 5 posts, trend) under
D:\\codex\\autogenFlow\\YYYY-MM-DD on Windows by default. On Linux/macOS,
that Windows path is mapped to /mnt/d/codex/autogenFlow when available,
otherwise to ./D_drive/codex/autogenFlow.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_UA = "redditCraw Daily News Generator/1.0 (by u/Tmakerchima)"


def resolve_output_root(value: str | None) -> Path:
    value = value or r"D:\codex\autogenFlow"
    match = re.match(r"^([A-Za-z]):[\\/](.*)$", value)
    if os.name != "nt" and match:
        drive, rest = match.group(1).lower(), match.group(2).replace("\\", "/")
        mnt = Path(f"/mnt/{drive}")
        if mnt.exists():
            return mnt / rest
        return Path.cwd() / f"{drive.upper()}_drive" / rest
    return Path(value)


def fetch_reddit(limit: int = 5) -> list[dict[str, Any]]:
    url = f"https://www.reddit.com/r/artificial/new.json?limit={limit}&raw_json=1"
    req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    posts: list[dict[str, Any]] = []
    for child in payload["data"]["children"][:limit]:
        data = child["data"]
        created = dt.datetime.fromtimestamp(data["created_utc"], dt.timezone.utc)
        permalink = "https://www.reddit.com" + data.get("permalink", "")
        external = data.get("url_overridden_by_dest") or ""
        if external.startswith("https://www.reddit.com") or external == permalink:
            external = ""
        posts.append(
            {
                "title": data.get("title", ""),
                "author": data.get("author", "unknown"),
                "created_utc": created.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "ups": data.get("ups", 0),
                "num_comments": data.get("num_comments", 0),
                "selftext": data.get("selftext", "").strip(),
                "permalink": permalink,
                "external_url": external,
            }
        )
    return posts


def one_line_summary(post: dict[str, Any]) -> str:
    text = post.get("selftext") or post["title"]
    text = re.sub(r"\s+", " ", text).strip()
    return (text[:115] + "...") if len(text) > 115 else text


def build_markdown(posts: list[dict[str, Any]], day: str) -> str:
    lines = [
        f"# AI Daily News {day}",
        "",
        "适合小红书发布的 r/artificial 最新 5 篇帖子日报。",
        "",
    ]
    for index, post in enumerate(posts, 1):
        lines += [
            f"## {index}. {post['title']}",
            "",
            f"作者：{post['author']}",
            "",
            f"发布时间：{post['created_utc']}",
            "",
            f"热度：⬆ {post['ups']}",
            "",
            f"评论：{post['num_comments']}",
            "",
            "标签：",
            "",
            "#AI #LLM #Agent",
            "",
            f"原帖链接：{post['permalink']}",
            "",
            f"外部新闻链接：{post['external_url'] or '无'}",
            "",
            "### 新闻摘要",
            "",
            (
                f"{one_line_summary(post)} "
                "本条内容来自 Reddit r/artificial 最新帖子；如果包含外部链接，"
                "发布前建议补充阅读原文并替换为新闻原文摘要。"
            ),
            "",
            "### 中文解读",
            "",
            (
                "从开发者视角看，这条内容可用于观察 AI 产品、LLM 能力、"
                "Agent 工作流和行业商业化趋势。建议重点评估技术意义、商业意义、"
                "对 Agent 的影响、对 AI 开发岗位的影响，以及可能带来的行业变化。"
            ),
            "",
        ]
    lines += [
        "## 今日趋势",
        "",
        (
            "今天的 r/artificial 最新内容可作为海外 AI 社区温度计：重点观察模型能力、"
            "Agent 落地、商业化、监管与开发者岗位变化。"
        ),
        "",
    ]
    return "\n".join(lines)


def wrap_text(text: str, width: int) -> list[str]:
    """Wrap mixed Chinese/English text for SVG cards without external deps."""
    chunks: list[str] = []
    line = ""
    count = 0
    for char in text:
        char_width = 1 if ord(char) < 128 else 2
        if count + char_width > width and line:
            chunks.append(line)
            line = char
            count = char_width
        else:
            line += char
            count += char_width
    if line:
        chunks.append(line)
    return chunks or [""]


def svg_card(title: str, body: list[str], footer: str) -> str:
    def esc(value: str) -> str:
        return html.escape(value, quote=True)

    y = 170
    body_svg = []
    for line in body:
        for wrapped in wrap_text(line, 44):
            body_svg.append(
                f'<text x="80" y="{y}" fill="#dbeafe" font-size="34" '
                f'font-family="Arial, sans-serif">{esc(wrapped)}</text>'
            )
            y += 48
        y += 10

    title_lines = wrap_text(title, 34)[:3]
    title_svg = "".join(
        f'<text x="80" y="{78 + i * 54}" fill="#ffffff" font-size="44" '
        f'font-weight="700" font-family="Arial, sans-serif">{esc(line)}</text>'
        for i, line in enumerate(title_lines)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1242" height="1656" viewBox="0 0 1242 1656">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#111827"/><stop offset="0.55" stop-color="#172554"/><stop offset="1" stop-color="#581c87"/></linearGradient></defs>
<rect width="1242" height="1656" fill="url(#g)"/><circle cx="1040" cy="210" r="220" fill="#38bdf8" opacity="0.12"/><circle cx="160" cy="1410" r="260" fill="#a78bfa" opacity="0.14"/>
<path d="M80 1320 C360 1180 610 1450 1160 1260" stroke="#60a5fa" stroke-width="3" opacity="0.28" fill="none"/>
{title_svg}<rect x="70" y="136" width="1100" height="2" fill="#93c5fd" opacity="0.45"/>{''.join(body_svg)}
<text x="80" y="1580" fill="#bfdbfe" font-size="30" font-family="Arial, sans-serif">{esc(footer)}</text></svg>"""


def write_outputs(posts: list[dict[str, Any]], out_dir: Path, day: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "daily.md").write_text(build_markdown(posts, day), encoding="utf-8")
    (out_dir / "posts.json").write_text(
        json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "00_cover.svg").write_text(
        svg_card(
            f"AI Daily News {day}",
            ["Reddit r/artificial", "今日 5 条精选", "AI · LLM · Agent · 商业化"],
            f"AI Daily News · {day}",
        ),
        encoding="utf-8",
    )
    for index, post in enumerate(posts, 1):
        body = [
            f"作者：{post['author']}  时间：{post['created_utc']}",
            f"热度：⬆ {post['ups']}  评论：{post['num_comments']}",
            "核心看点：" + one_line_summary(post),
            "开发者视角：关注技术意义、商业意义、Agent 影响与岗位变化。",
        ]
        (out_dir / f"{index:02d}_post.svg").write_text(
            svg_card(f"{index:02d} {post['title']}", body, "Reddit r/artificial"),
            encoding="utf-8",
        )
    (out_dir / "06_trend.svg").write_text(
        svg_card(
            "今日趋势",
            [
                "1. 模型能力与可控性仍是核心",
                "2. Agent 落地更关注成本和可靠性",
                "3. 商业化、监管和岗位变化同步加速",
                "一句话总结：AI 正从能力竞赛进入落地约束阶段。",
            ],
            f"AI Daily News · {day}",
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--input-json", help="Use a local posts JSON file instead of fetching Reddit.")
    args = parser.parse_args()

    posts = (
        json.loads(Path(args.input_json).read_text(encoding="utf-8"))
        if args.input_json
        else fetch_reddit(5)
    )
    out_dir = resolve_output_root(args.output_root) / args.date
    write_outputs(posts, out_dir, args.date)
    print(out_dir)


if __name__ == "__main__":
    main()
