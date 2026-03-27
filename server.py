import os
import re
from mcp.server.fastmcp import FastMCP
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

mcp = FastMCP("yt-transcript")
yta = YouTubeTranscriptApi()


def extract_video_id(url_or_id: str) -> str:
    patterns = [
        r'(?:v=|youtu\.be/|shorts/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def get_video_title(video_id: str) -> str:
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return info.get('title', 'Unknown Title')
    except Exception:
        return 'Unknown Title'


@mcp.tool()
def get_transcript(url: str, language: str = "en") -> str:
    """Get the transcript of a YouTube video. Accepts a URL or video ID."""
    try:
        video_id = extract_video_id(url)
        snippets = yta.fetch(video_id, languages=[language, "en"])
        text = " ".join(s.text for s in snippets)
        title = get_video_title(video_id)
        return f"**{title}**\nhttps://www.youtube.com/watch?v={video_id}\n\n{text}"
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(mcp.streamable_http_app(), host="0.0.0.0", port=port)
