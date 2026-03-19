"""yt-dlp 기반 콘텐츠 다운로드."""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional

from ..config import DOWNLOAD_TIMEOUT, VIDEO_FORMAT, MAX_VIDEO_SIZE


def _run_ytdlp(args: list, timeout: int = DOWNLOAD_TIMEOUT) -> subprocess.CompletedProcess:
    """yt-dlp를 subprocess로 실행."""
    cmd = [sys.executable, "-m", "yt_dlp", "--ignore-config"] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def download_video(url: str, output_dir: str, filename: str = "source") -> Optional[str]:
    """영상을 mp4로 다운로드."""
    output_path = os.path.join(output_dir, f"{filename}.mp4")
    output_template = os.path.join(output_dir, f"{filename}.%(ext)s")

    try:
        result = _run_ytdlp([
            "--no-playlist",
            "--format", VIDEO_FORMAT,
            "--max-filesize", MAX_VIDEO_SIZE,
            "--merge-output-format", "mp4",
            "-o", output_template,
            url,
        ])

        if result.returncode != 0:
            print(f"  [WARN] yt-dlp error: {result.stderr[:200]}")
            return None

        if os.path.exists(output_path):
            return output_path

        for f in Path(output_dir).glob(f"{filename}.*"):
            if f.suffix in (".mp4", ".mkv", ".webm"):
                return str(f)
        return None

    except subprocess.TimeoutExpired:
        print(f"  [WARN] Download timed out ({DOWNLOAD_TIMEOUT}s)")
        return None
    except Exception as e:
        print(f"  [WARN] Download failed: {e}")
        return None


def download_thumbnail(url: str, output_dir: str, filename: str = "thumb") -> Optional[str]:
    """영상 썸네일을 다운로드."""
    try:
        result = _run_ytdlp([
            "--skip-download",
            "--write-thumbnail",
            "--convert-thumbnails", "png",
            "-o", os.path.join(output_dir, filename),
            url,
        ], timeout=30)

        for f in Path(output_dir).glob(f"{filename}.*"):
            if f.suffix in (".png", ".jpg", ".jpeg", ".webp"):
                return str(f)
        return None

    except Exception as e:
        print(f"  [WARN] Thumbnail download failed: {e}")
        return None


def download_content(post: Dict, output_dir: str) -> Dict:
    """게시물 콘텐츠를 다운로드."""
    os.makedirs(output_dir, exist_ok=True)

    platform = post["platform"]
    url = post["url"]
    caption = post.get("caption", "")
    result = {
        "media_path": None,
        "media_type": "text",
        "thumb_path": None,
        "caption": caption,
        "platform": platform,
        "url": url,
        "title": post.get("title", ""),
        "engagement": post.get("engagement", {}),
        "hashtags": post.get("hashtags", ""),
    }

    if platform in ("tiktok", "instagram"):
        print(f"  Downloading video from {platform}...")
        video_path = download_video(url, output_dir)
        if video_path:
            result["media_path"] = video_path
            result["media_type"] = "video"
            print(f"  -> {video_path}")

            file_size = os.path.getsize(video_path)
            print(f"  File size: {file_size / 1024 / 1024:.1f}MB")

        print(f"  Downloading thumbnail...")
        thumb_path = download_thumbnail(url, output_dir)
        if thumb_path:
            result["thumb_path"] = thumb_path
            print(f"  -> {thumb_path}")
        print(f"  Media type: {result['media_type']}")

    elif platform == "reddit":
        if any(x in url for x in ["v.redd.it", "i.redd.it", "imgur.com"]):
            print(f"  Downloading Reddit media...")
            video_path = download_video(url, output_dir)
            if video_path:
                result["media_path"] = video_path
                result["media_type"] = "video"
        else:
            print(f"  Reddit text post - using caption/selftext only")
            result["media_type"] = "text"

    return result
