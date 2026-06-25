#!/usr/bin/env python3
"""Generate Xiaohongshu-style AI news cards from r/artificial.

Default output directory:
  D:\\codex\\autogenFlow\\YYYY-MM-DD

The flow writes five vertical PNG images, one Reddit item per page, plus
posts.json and daily.md for editing/copywriting.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import urllib.request
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

DEFAULT_UA = "redditCraw Daily News Generator/1.2 (by u/Tmakerchima)"
DEFAULT_TITLE = "AI\u4eca\u65e5\u8d44\u8baf"
SUBREDDIT = "artificial"

TEXT_SOURCE = "\u6765\u6e90\uff1aReddit r/artificial \u6700\u65b0\u5e16\u5b50"
TEXT_AUTHOR = "\u4f5c\u8005"
TEXT_TIME = "\u53d1\u5e03\u65f6\u95f4"
TEXT_HEAT = "\u70ed\u5ea6"
TEXT_POST = "\u539f\u5e16"
TEXT_LINK = "\u5916\u90e8\u94fe\u63a5"
TEXT_NONE = "\u65e0"
TEXT_SUMMARY = "\u6458\u8981"
TEXT_INSIGHT = "\u89e3\u8bfb"
TEXT_CARD_SUMMARY = "\u8d44\u8baf\u6458\u8981"
TEXT_CARD_INSIGHT = "AI\u89e3\u8bfb"
TEXT_TAGS = "#AI #\u4eba\u5de5\u667a\u80fd #\u4eca\u65e5\u8d44\u8baf #LLM"


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
    url = f"https://www.reddit.com/r/{SUBREDDIT}/new.json?limit={limit}&raw_json=1"
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
                "title": data.get("title", "").strip(),
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


def clean_text(value: str) -> str:
    value = re.sub(r"https?://\S+", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def truncate(value: str, limit: int) -> str:
    value = clean_text(value)
    return value[: limit - 3].rstrip() + "..." if len(value) > limit else value


def summary_for(post: dict[str, Any]) -> str:
    source = post.get("selftext") or post.get("title") or ""
    return truncate(source, 150)


def angle_for(post: dict[str, Any]) -> str:
    text = f"{post.get('title', '')} {post.get('selftext', '')}".lower()
    if any(term in text for term in ["agent", "workflow", "automation"]):
        return "\u5173\u6ce8 Agent \u5de5\u4f5c\u6d41\u662f\u5426\u80fd\u771f\u5b9e\u964d\u4f4e\u4eba\u529b\u6210\u672c\uff0c\u800c\u4e0d\u662f\u53ea\u505c\u7559\u5728\u6f14\u793a\u6548\u679c\u3002"
    if any(term in text for term in ["model", "llm", "gpt", "claude", "gemini"]):
        return "\u91cd\u70b9\u770b\u6a21\u578b\u80fd\u529b\u8fb9\u754c\u3001\u7a33\u5b9a\u6027\u548c\u53ef\u63a7\u6027\uff0c\u5bf9\u4ea7\u54c1\u843d\u5730\u5f71\u54cd\u66f4\u76f4\u63a5\u3002"
    if any(term in text for term in ["law", "regulation", "copyright", "policy"]):
        return "\u8fd9\u7c7b\u8bdd\u9898\u4f1a\u5f71\u54cd AI \u4ea7\u54c1\u7684\u5408\u89c4\u6210\u672c\uff0c\u4e5f\u4f1a\u6539\u53d8\u521b\u4e1a\u516c\u53f8\u7684\u8282\u594f\u3002"
    return "\u9002\u5408\u4ece\u4ea7\u54c1\u3001\u5f00\u53d1\u8005\u548c\u5546\u4e1a\u5316\u4e09\u4e2a\u89d2\u5ea6\u5224\u65ad\u8fd9\u6761\u8d44\u8baf\u7684\u5b9e\u9645\u4ef7\u503c\u3002"


def build_markdown(posts: list[dict[str, Any]], day: str) -> str:
    lines = [f"# {DEFAULT_TITLE} {day}", "", TEXT_SOURCE, ""]
    for index, post in enumerate(posts[:5], 1):
        lines += [
            f"## {index}. {post['title']}",
            "",
            f"{TEXT_AUTHOR}\uff1a{post['author']}",
            f"{TEXT_TIME}\uff1a{post['created_utc']}",
            f"{TEXT_HEAT}\uff1a{post['ups']} upvotes / {post['num_comments']} comments",
            f"{TEXT_POST}\uff1a{post['permalink']}",
            f"{TEXT_LINK}\uff1a{post['external_url'] or TEXT_NONE}",
            "",
            f"{TEXT_SUMMARY}\uff1a{summary_for(post)}",
            "",
            f"{TEXT_INSIGHT}\uff1a{angle_for(post)}",
            "",
        ]
    return "\n".join(lines)


def font_path(bold: bool = False) -> str | None:
    candidates = [
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\NotoSansSC-VF.ttf",
        r"C:\Windows\Fonts\simhei.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = font_path(bold)
    if path:
        return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> float:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap_by_pixels(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int
) -> list[str]:
    words = re.findall(r"[A-Za-z0-9_./:+#'-]+|\s+|.", text)
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = line + word
        if text_width(draw, candidate.strip(), font) <= max_width or not line:
            line = candidate
            continue
        lines.append(line.strip())
        line = word
    if line.strip():
        lines.append(line.strip())
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    max_width: int,
    line_height: int,
    max_lines: int | None = None,
) -> int:
    x, y = xy
    lines = wrap_by_pixels(draw, text, font, max_width)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines[-1] and text_width(draw, lines[-1] + "...", font) > max_width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "..."
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def news_card_png(post: dict[str, Any], out_path: Path, index: int, total: int, day: str) -> None:
    title = truncate(post["title"], 120)
    summary = summary_for(post)
    angle = angle_for(post)
    meta = f"r/artificial  |  {post['ups']} upvotes  |  {post['num_comments']} comments"
    source = f"by u/{post['author']}  \u00b7  {post['created_utc'].replace(' UTC', '')}"

    image = Image.new("RGB", (1242, 1656), "#f7f2ec")
    draw = ImageDraw.Draw(image)
    title_font = load_font(54, bold=True)
    header_font = load_font(48, bold=True)
    label_font = load_font(32, bold=True)
    body_font = load_font(34)
    small_font = load_font(26)
    tag_font = load_font(25, bold=True)

    draw.rectangle((0, 0, 1242, 218), fill="#ff2442")
    draw.text((78, 54), DEFAULT_TITLE, font=header_font, fill="#ffffff")
    draw.text((78, 132), f"Reddit r/artificial \u00b7 {day}", font=small_font, fill="#ffe2e7")
    draw.text((1064, 82), f"{index:02d}/{total:02d}", font=load_font(42, bold=True), fill="#ffffff")

    draw.rounded_rectangle((52, 238, 1190, 1566), radius=30, fill="#ffffff")
    draw.rounded_rectangle((78, 276, 90, 448), radius=6, fill="#ff2442")
    draw_wrapped(draw, (108, 268), title, title_font, "#111111", 1000, 68, max_lines=4)

    draw.line((92, 598, 1150, 598), fill="#f0e6de", width=2)
    draw.text((92, 634), TEXT_CARD_SUMMARY, font=label_font, fill="#ff2442")
    draw_wrapped(draw, (92, 706), summary, body_font, "#2f2f2f", 1058, 52, max_lines=5)

    draw.line((92, 967, 1150, 967), fill="#f0e6de", width=2)
    draw.text((92, 1005), TEXT_CARD_INSIGHT, font=label_font, fill="#ff2442")
    draw_wrapped(draw, (92, 1077), angle, body_font, "#4b5563", 1058, 52, max_lines=4)

    draw.line((92, 1352, 1150, 1352), fill="#f0e6de", width=2)
    draw_wrapped(draw, (92, 1406), meta, small_font, "#777777", 1058, 36, max_lines=2)
    draw_wrapped(draw, (92, 1460), source, small_font, "#999999", 1058, 36, max_lines=2)
    draw.text((92, 1522), TEXT_TAGS, font=tag_font, fill="#ff2442")
    image.save(out_path, "PNG", optimize=True)


def write_outputs(posts: list[dict[str, Any]], out_dir: Path, day: str, clean: bool = False) -> None:
    if clean and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    selected = posts[:5]
    (out_dir / "daily.md").write_text(build_markdown(selected, day), encoding="utf-8")
    (out_dir / "posts.json").write_text(
        json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for index, post in enumerate(selected, 1):
        news_card_png(post, out_dir / f"{index:02d}_news.png", index, len(selected), day)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--input-json", help="Use a local posts JSON file instead of fetching Reddit.")
    parser.add_argument("--clean", action="store_true", help="Delete the target date folder before writing.")
    args = parser.parse_args()

    posts = (
        json.loads(Path(args.input_json).read_text(encoding="utf-8"))
        if args.input_json
        else fetch_reddit(5)
    )
    out_dir = resolve_output_root(args.output_root) / args.date
    write_outputs(posts, out_dir, args.date, clean=args.clean)
    print(out_dir)


if __name__ == "__main__":
    main()
