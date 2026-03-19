"""검색 결과 → Markdown 보고서 생성."""

from datetime import datetime
from ..utils import fmt_number


def build_markdown(query, reddit_result, tiktok_result, ig_result, depth, elapsed):
    """3개 소스 검색 결과를 MD 문자열로 변환."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# ScrapeCreators 검색 결과",
        f"",
        f"- **검색어**: {query}",
        f"- **실행 시간**: {now}",
        f"- **Depth**: {depth}",
        f"- **소요 시간**: {elapsed:.1f}초",
        f"",
    ]

    # Reddit
    r_items = reddit_result.get("items", [])
    r_error = reddit_result.get("error")
    lines.append(f"---")
    lines.append(f"## Reddit ({len(r_items)}건)")
    if r_error:
        lines.append(f"> Error: {r_error}")
    lines.append("")

    for item in r_items:
        eng = item.get("engagement", {})
        lines.append(f"### [{item.get('title', 'No Title')}]({item.get('url', '')})")
        lines.append(f"")
        lines.append(f"| 항목 | 값 |")
        lines.append(f"|------|-----|")
        lines.append(f"| Subreddit | r/{item.get('subreddit', '?')} |")
        lines.append(f"| 날짜 | {item.get('date', '?')} |")
        lines.append(f"| Relevance | **{item.get('relevance', 0):.2f}** |")
        lines.append(f"| Upvotes | {fmt_number(eng.get('score', 0))} |")
        lines.append(f"| 댓글 수 | {fmt_number(eng.get('num_comments', 0))} |")
        lines.append(f"| Upvote Ratio | {eng.get('upvote_ratio', '?')} |")
        lines.append(f"")

        selftext = item.get("selftext", "")
        if selftext:
            lines.append(f"**본문 (발췌)**:")
            lines.append(f"> {selftext[:300]}{'...' if len(selftext) > 300 else ''}")
            lines.append(f"")

        top_comments = item.get("top_comments", [])
        if top_comments:
            lines.append(f"**Top Comments ({len(top_comments)})**:")
            lines.append(f"")
            for ci, c in enumerate(top_comments[:5], 1):
                lines.append(f"{ci}. **u/{c.get('author', '?')}** (score: {c.get('score', 0)})")
                if c.get("url"):
                    lines.append(f"   [link]({c['url']})")
                excerpt = c.get("excerpt", "")
                lines.append(f"   > {excerpt[:200]}{'...' if len(excerpt) > 200 else ''}")
                lines.append(f"")

        insights = item.get("comment_insights", [])
        if insights:
            lines.append(f"**Comment Insights**:")
            for ins in insights[:3]:
                lines.append(f"- {ins}")
            lines.append(f"")

    # TikTok
    t_items = tiktok_result.get("items", [])
    t_error = tiktok_result.get("error")
    lines.append(f"---")
    lines.append(f"## TikTok ({len(t_items)}건)")
    if t_error:
        lines.append(f"> Error: {t_error}")
    lines.append("")

    for item in t_items:
        eng = item.get("engagement", {})
        title = item.get("text", "")[:80] or "No Caption"
        lines.append(f"### [{title}]({item.get('url', '')})")
        lines.append(f"")
        lines.append(f"| 항목 | 값 |")
        lines.append(f"|------|-----|")
        lines.append(f"| 작성자 | @{item.get('author_name', '?')} |")
        lines.append(f"| 날짜 | {item.get('date', '?')} |")
        lines.append(f"| Relevance | **{item.get('relevance', 0):.2f}** |")
        lines.append(f"| 조회수 | {fmt_number(eng.get('views', 0))} |")
        lines.append(f"| 좋아요 | {fmt_number(eng.get('likes', 0))} |")
        lines.append(f"| 댓글 수 | {fmt_number(eng.get('comments', 0))} |")
        lines.append(f"| 공유 | {fmt_number(eng.get('shares', 0))} |")
        lines.append(f"| 해시태그 | {', '.join('#'+h for h in item.get('hashtags', [])[:10])} |")
        lines.append(f"")

        caption = item.get("caption_snippet", "")
        if caption:
            lines.append(f"**캡션/트랜스크립트**:")
            lines.append(f"> {caption[:400]}{'...' if len(caption) > 400 else ''}")
            lines.append(f"")

    # Instagram
    i_items = ig_result.get("items", [])
    i_error = ig_result.get("error")
    lines.append(f"---")
    lines.append(f"## Instagram ({len(i_items)}건)")
    if i_error:
        lines.append(f"> Error: {i_error}")
    lines.append("")

    for item in i_items:
        eng = item.get("engagement", {})
        title = item.get("text", "")[:80] or "No Caption"
        lines.append(f"### [{title}]({item.get('url', '')})")
        lines.append(f"")
        lines.append(f"| 항목 | 값 |")
        lines.append(f"|------|-----|")
        lines.append(f"| 작성자 | @{item.get('author_name', '?')} |")
        lines.append(f"| 날짜 | {item.get('date', '?')} |")
        lines.append(f"| Relevance | **{item.get('relevance', 0):.2f}** |")
        lines.append(f"| 조회수 | {fmt_number(eng.get('views', 0))} |")
        lines.append(f"| 좋아요 | {fmt_number(eng.get('likes', 0))} |")
        lines.append(f"| 댓글 수 | {fmt_number(eng.get('comments', 0))} |")
        lines.append(f"| 해시태그 | {', '.join('#'+h for h in item.get('hashtags', [])[:10])} |")
        lines.append(f"")

        caption = item.get("caption_snippet", "")
        if caption:
            lines.append(f"**캡션/트랜스크립트**:")
            lines.append(f"> {caption[:400]}{'...' if len(caption) > 400 else ''}")
            lines.append(f"")

    # Summary
    lines.append(f"---")
    lines.append(f"## Summary")
    lines.append(f"")
    lines.append(f"| 소스 | 결과 수 | 상태 |")
    lines.append(f"|------|---------|------|")
    lines.append(f"| Reddit | {len(r_items)} | {'OK' if not r_error else r_error} |")
    lines.append(f"| TikTok | {len(t_items)} | {'OK' if not t_error else t_error} |")
    lines.append(f"| Instagram | {len(i_items)} | {'OK' if not i_error else i_error} |")

    return "\n".join(lines)
