---
name: youtube-transcript
description: Fetch and process YouTube video transcripts for research, documentation, and summary ingestion. Trigger when given a YouTube URL or video ID and asked to extract or ingest transcript notes.
disable-model-invocation: false
---

# YouTube Transcript Ingestion Skill

## Goal
To extract YouTube video transcripts and convert them into structured Markdown research notes or ground input for the Master Vision Plan.

## Workflow

1. **Extract Transcript**:
   - Use Python helper (`youtube_transcript_api` or `yt-dlp`) or curl/web tools to retrieve video caption track.
   - Example python execution:
     ```python
     from youtube_transcript_api import YouTubeTranscriptApi
     transcript = YouTubeTranscriptApi.get_transcript(video_id)
     ```
2. **Clean & Format**:
   - Strip timing artifacts and duplicate lines.
   - Group text into coherent thematic paragraphs.
3. **Ingest & Summarize**:
   - Extract key insights, claims, and code/architecture references.
   - Save processed output to `docs/research/yt_<video_id>.md` or pass to `seikoclaw-ingestor`.
