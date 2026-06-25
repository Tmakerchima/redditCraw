# redditCraw

Generate Xiaohongshu-style AI news cards from the newest five Reddit `r/artificial` posts.

## Run

```bash
python3 reddit_xhs_daily.py --date 2026-06-25 --clean
```

By default, output is written to `D:\codex\autogenFlow\YYYY-MM-DD` on Windows. On Linux/macOS, the script maps that path to `/mnt/d/codex/autogenFlow` when available, otherwise to `./D_drive/codex/autogenFlow`.

## Output files

- `daily.md`: Markdown copywriting draft.
- `posts.json`: Raw normalized post metadata.
- `01_news.png` through `05_news.png`: Five vertical cards, one news item per image.

## Offline/retry mode

If Reddit is temporarily blocked, save a compatible post list and run:

```bash
python3 reddit_xhs_daily.py --date 2026-06-25 --input-json posts.json --clean
```
