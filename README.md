# redditCraw

Generate a Xiaohongshu-ready daily digest from the newest five Reddit `r/artificial` posts.

## Run

```bash
python3 reddit_xhs_daily.py --date 2026-06-25
```

By default, output is written to `D:\codex\autogenFlow\YYYY-MM-DD` on Windows. On Linux/macOS, the script maps that path to `/mnt/d/codex/autogenFlow` when available, otherwise to `./D_drive/codex/autogenFlow`.

## Output files

- `daily.md`: Markdown article using the Xiaohongshu template.
- `posts.json`: Raw normalized post metadata.
- `00_cover.svg`: Cover card.
- `01_post.svg` through `05_post.svg`: One card per post.
- `06_trend.svg`: Trend summary card.

## Offline/retry mode

If Reddit is temporarily blocked, save a compatible post list and run:

```bash
python3 reddit_xhs_daily.py --date 2026-06-25 --input-json posts.json
```
