"""검색 결과 MD 파일 파싱 — 구조화된 게시물 리스트로 변환."""

import re
from pathlib import Path
from typing import List, Dict

PLATFORM_PREFIX = {
    "reddit": "R",
    "tiktok": "TK",
    "instagram": "IG",
}


def parse_search_results(md_path: str) -> List[Dict]:
    """MD 파일을 파싱하여 모든 게시물을 구조화된 리스트로 반환."""
    text = Path(md_path).read_text(encoding="utf-8")
    items = []

    current_platform = None
    platform_counters = {"reddit": 0, "tiktok": 0, "instagram": 0}

    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("## Reddit"):
            current_platform = "reddit"
        elif line.startswith("## TikTok"):
            current_platform = "tiktok"
        elif line.startswith("## Instagram"):
            current_platform = "instagram"
        elif line.startswith("## Summary"):
            break

        # Detect item: ### [title](url)
        title_match = re.match(r"^### \[(.+?)\]\((.+?)\)\s*$", line)
        if not title_match and line.startswith("### [") and current_platform:
            accumulated = line
            peek = i + 1
            while peek < len(lines) and "](http" not in accumulated:
                accumulated += "\n" + lines[peek]
                peek += 1
                if peek - i > 10:
                    break
            title_match = re.match(r"^### \[(.+?)\]\((.+?)\)\s*$", accumulated, re.DOTALL)
            if title_match:
                i = peek

        if title_match and current_platform:
            platform_counters[current_platform] += 1
            count = platform_counters[current_platform]
            prefix = PLATFORM_PREFIX[current_platform]
            item_id = f"{prefix}{count}"

            title = title_match.group(1)
            url = title_match.group(2)

            engagement = {}
            caption = ""
            hashtags = ""
            j = i + 1
            while j < len(lines) and not lines[j].startswith("### ") and not lines[j].startswith("## "):
                tline = lines[j]

                table_match = re.match(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|$", tline)
                if table_match:
                    key = table_match.group(1).strip()
                    val = table_match.group(2).strip()
                    key_map = {
                        "Upvotes": "upvotes", "score": "upvotes",
                        "댓글 수": "comments", "조회수": "views",
                        "좋아요": "likes", "공유": "shares",
                        "Relevance": "relevance", "작성자": "author",
                        "날짜": "date", "Subreddit": "subreddit",
                        "Upvote Ratio": "upvote_ratio", "해시태그": None,
                    }
                    if key == "해시태그":
                        hashtags = val
                    elif key in key_map and key_map[key]:
                        engagement[key_map[key]] = val

                if tline.startswith("> "):
                    caption_lines = [tline[2:]]
                    k = j + 1
                    while k < len(lines) and (
                        lines[k].startswith("> ") or (
                            lines[k].strip() and
                            not lines[k].startswith("|") and
                            not lines[k].startswith("###") and
                            not lines[k].startswith("##") and
                            not lines[k].startswith("**")
                        )
                    ):
                        if lines[k].startswith("> "):
                            caption_lines.append(lines[k][2:])
                        elif lines[k].strip():
                            caption_lines.append(lines[k])
                        else:
                            break
                        k += 1
                    caption = "\n".join(caption_lines)
                    j = k
                    continue

                j += 1

            items.append({
                "id": item_id,
                "platform": current_platform,
                "title": title,
                "url": url,
                "engagement": engagement,
                "caption": caption,
                "hashtags": hashtags,
            })
            i = j
            continue

        i += 1

    return items
