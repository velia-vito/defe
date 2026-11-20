"""Release title & URL parser for languages, audio formats, video formats, and size."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import unquote, urlparse

from scrapers._tags import name_from_url

# (pattern, canonical_label)
LANGUAGE_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(english|eng)\b", re.I), "English"),
    (re.compile(r"\b(hindi|hin)\b", re.I), "Hindi"),
    (re.compile(r"\b(japanese|jpn|jap)\b", re.I), "Japanese"),
    (re.compile(r"\b(korean|kor)\b", re.I), "Korean"),
    (re.compile(r"\b(chinese|chi|mandarin|cantonese)\b", re.I), "Chinese"),
    (re.compile(r"\b(spanish|spa|esp|latino|castellano)\b", re.I), "Spanish"),
    (re.compile(r"\b(french|fre|fra)\b", re.I), "French"),
    (re.compile(r"\b(german|ger|deu)\b", re.I), "German"),
    (re.compile(r"\b(italian|ita)\b", re.I), "Italian"),
    (re.compile(r"\b(portuguese|por|pt-br)\b", re.I), "Portuguese"),
    (re.compile(r"\b(russian|rus)\b", re.I), "Russian"),
    (re.compile(r"\b(arabic|ara)\b", re.I), "Arabic"),
    (re.compile(r"\b(tamil|tam)\b", re.I), "Tamil"),
    (re.compile(r"\b(telugu|tel)\b", re.I), "Telugu"),
    (re.compile(r"\b(malayalam|mal)\b", re.I), "Malayalam"),
    (re.compile(r"\b(kannada|kan)\b", re.I), "Kannada"),
    (re.compile(r"\b(bengali|ben)\b", re.I), "Bengali"),
    (re.compile(r"\b(punjabi|pan)\b", re.I), "Punjabi"),
    (re.compile(r"\b(indonesian|indo)\b", re.I), "Indonesian"),
    (re.compile(r"\b(turkish|tur)\b", re.I), "Turkish"),
    (re.compile(r"\b(thai|tha)\b", re.I), "Thai"),
    (re.compile(r"\b(vietnamese|vie)\b", re.I), "Vietnamese"),

]

AUDIO_OPTION_RULES: list[tuple[re.Pattern[str], str, int]] = [
    (re.compile(r"\b(ddp|dd\+|e-?ac-?3|eac3|dolby[\s.-]*digital[\s.-]*plus)(?:[ ._-]?\d\.\d)?\b", re.I), "Dolby Digital+", 700),
    (re.compile(r"\b(dd5\.?1|dd2\.?0|ac-?3|dolby[\s.-]*digital)\b", re.I), "Dolby Digital", 650),
    (re.compile(r"\b7\.1\b|\b(?:ddp|dd\+|dd|ac-?3|eac3|e-?ac-?3|dts|truehd)\s*7\.1\b", re.I), "7.1", 550),
    (re.compile(r"\b5\.1\b|\bdd5\.?1\b|\b(?:ddp|dd\+|dd|ac-?3|eac3|e-?ac-?3|dts|truehd)\s*5\.1\b", re.I), "5.1", 500),
    (re.compile(r"\b(stereo|2[\s.-]?ch|2\.0)\b", re.I), "Stereo", 100),
]

AUDIO_RULES: list[tuple[re.Pattern[str], str, int]] = [
    (re.compile(r"\b(truehd|dolby[\s.-]*truehd)\b", re.I), "TrueHD", 100),
    (re.compile(r"\batmos\b", re.I), "Atmos", 95),
    (re.compile(r"\bdts[\s.-]*hd[\s.-]*ma\b", re.I), "DTS-HD MA", 92),
    (re.compile(r"\bdts[\s.-]*hd\b", re.I), "DTS-HD", 88),
    (re.compile(r"\bdts[\s.-]*x\b", re.I), "DTS:X", 94),
    (re.compile(r"\bdts\b", re.I), "DTS", 75),
    (re.compile(r"\b(ddp|dd\+|e-?ac-?3|eac3|dolby[\s.-]*digital[\s.-]*plus)(?:[ ._-]?\d\.\d)?\b", re.I), "Dolby Digital+", 70),
    (re.compile(r"\b(dd5\.?1|dd2\.?0|ac-?3|dolby[\s.-]*digital)\b", re.I), "Dolby Digital", 60),
    (re.compile(r"\bflac\b", re.I), "FLAC", 85),
    (re.compile(r"\bopus\b", re.I), "Opus", 55),
    (re.compile(r"\baac\b", re.I), "AAC", 50),
    (re.compile(r"\bmp3\b", re.I), "MP3", 30),
    (re.compile(r"\b7\.1\b", re.I), "7.1", 15),
    (re.compile(r"\b5\.1\b", re.I), "5.1", 10),
    (re.compile(r"\b2\.0\b", re.I), "Stereo", 5),
]

RESOLUTION_RULES: list[tuple[re.Pattern[str], str, int]] = [
    (re.compile(r"\b(2160p+|4k|uhd)\b|\b\d{3,4}\s*[x×]\s*2160\b", re.I), "2160p", 2160),
    (re.compile(r"\b1080p+\b|\b\d{3,4}\s*[x×]\s*1080\b", re.I), "1080p", 1080),
    (re.compile(r"\b720p+\b|\b720\s*hc\b|\b720hc\b|\b\d{3,4}\s*[x×]\s*720\b", re.I), "720p", 720),
    (re.compile(r"\b540p+\b|\b\d{3,4}\s*[x×]\s*540\b", re.I), "540p", 540),
    (re.compile(r"\b480p+\b|\b480\s*hc\b|\b480hc\b|\b\d{3,4}\s*[x×]\s*480\b", re.I), "480p", 480),
    (re.compile(r"\b400p+\b|\b\d{3,4}\s*[x×]\s*400\b", re.I), "400p", 400),
    (re.compile(r"\b360p+\b|\b\d{3,4}\s*[x×]\s*360\b", re.I), "360p", 360),
]

VIDEO_CODEC_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bav1\b", re.I), "AV1"),
    (re.compile(r"\b(x265|h\.?265|hevc)\b", re.I), "HEVC"),
    (re.compile(r"\b(x264|x254|h\.?264|avc)\b", re.I), "AVC"),
    (re.compile(r"\bvp9\b", re.I), "VP9"),
    (re.compile(r"\bxvid\b", re.I), "XviD"),
]

VIDEO_HDR_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(dolby[\s.-]*vision|dovi|dv)\b", re.I), "Dolby Vision"),
    (re.compile(r"\bhdr10\+(?!\w)", re.I), "HDR10+"),
    (re.compile(r"\bhdr12\b", re.I), "HDR12"),
    (re.compile(r"\bhdr10\b", re.I), "HDR10"),
    (re.compile(r"\bhdr\b", re.I), "HDR"),
    (re.compile(r"\b10[\s.-]*bit\b", re.I), "10-bit"),
]

VIDEO_OPTION_RULES: list[tuple[re.Pattern[str], str, int]] = [
    (re.compile(r"\b(dolby[\s.-]*vision|dovi|dv)\b", re.I), "Dolby Vision", 700),
    (re.compile(r"\bhdr[\s._-]*12\b", re.I), "HDR12", 600),
    (re.compile(r"\bhdr[\s._-]*10\s*\+", re.I), "HDR10+", 580),
    (re.compile(r"\bhdr[\s._-]*10\b|\bhdr\b", re.I), "HDR10", 550),
    (re.compile(r"\bsdr[\s._-]*10\b|(?=.*\bsdr\b)(?=.*\b10[\s.-]*bit\b)", re.I), "SDR10", 250),
    (re.compile(r"\bsdr\b", re.I), "SDR", 100),
]

VIDEO_SOURCE_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bremux\b", re.I), "REMUX"),
    (re.compile(r"\b(bluray|blu[\s.-]?ray|bdrip|brrip)\b", re.I), "BluRay"),
    (re.compile(r"\bweb[\s.-]?dl\b", re.I), "Web-DL"),
    (re.compile(r"\bweb[\s.-]?rip\b", re.I), "Web-Rip"),
    (re.compile(r"\bhdtv\b", re.I), "HDTV"),
    (re.compile(r"\bhdrip\b", re.I), "HDRip"),
    (re.compile(r"\bdvdrip\b", re.I), "DVDRip"),
    (re.compile(r"\b(hdcam|camrip|hdts|telesync)\b", re.I), "CAM / TS"),
]

SIZE_RE = re.compile(r"\b(\d+(?:[.,]\d+)?)\s*(KB|MB|GB|TB|KiB|MiB|GiB|TiB)\b", re.I)
SIZE_MULTIPLIERS = {
    "KB": 1024,
    "KIB": 1024,
    "MB": 1024**2,
    "MIB": 1024**2,
    "GB": 1024**3,
    "GIB": 1024**3,
    "TB": 1024**4,
    "TIB": 1024**4,
}


def _display_name(name: str, url: str) -> str:
    if name and name.strip():
        return name.strip()
    guessed = name_from_url(url)
    if guessed:
        return guessed
    try:
        path = unquote(urlparse(url).path).rstrip("/")
        last = path.split("/")[-1]
        if last:
            return last
    except Exception:
        pass
    return url


def _parse_size(blob: str) -> tuple[int, str]:
    best_bytes = 0
    best_label = ""
    for m in SIZE_RE.finditer(blob):
        num_str = m.group(1).replace(",", ".")
        unit = m.group(2).upper()
        prefix = blob[:m.start(1)]
        previous_token = re.search(r"(\d+)\.$", prefix)
        whole, dot, fraction = num_str.partition(".")
        if dot and previous_token and previous_token.group(1).isdigit():
            num_str = fraction
        elif dot and len(whole) == 4 and whole.startswith(("19", "20")) and 1900 <= int(whole) <= 2099:
            num_str = fraction
        try:
            val = float(num_str)
        except ValueError:
            continue
        b = int(val * SIZE_MULTIPLIERS.get(unit, 1))
        if b > best_bytes:
            best_bytes = b
            clean_num = num_str.rstrip("0").rstrip(".") if "." in num_str else num_str
            clean_unit = unit.replace("IB", "B")
            best_label = f"{clean_num} {clean_unit}"
    return best_bytes, best_label


def parse_release(name: str = "", url: str = "", tags: list[str] | None = None) -> dict[str, Any]:
    tags = tags or []
    disp = _display_name(name, url)
    # Normalize underscores to spaces so \b word boundaries work reliably on Snake_Case filenames
    raw_blob = " ".join([disp, url, " ".join(str(t) for t in tags)])
    blob = raw_blob.replace("_", " ")

    languages: list[str] = []
    for pat, label in LANGUAGE_RULES:
        if pat.search(blob) and label not in languages:
            languages.append(label)

    audio_formats: list[str] = []
    for pat, label, _rank in AUDIO_RULES:
        if pat.search(blob) and label not in audio_formats:
            audio_formats.append(label)

    audio_options: list[str] = []
    audio_rank = 0
    for pat, label, rank in AUDIO_OPTION_RULES:
        if pat.search(blob) and label not in audio_options:
            audio_options.append(label)
            audio_rank = max(audio_rank, rank)

    resolution = ""
    resolution_rank = 0
    for pat, label, rank in RESOLUTION_RULES:
        if pat.search(blob):
            resolution = label
            resolution_rank = rank
            break

    video_codecs: list[str] = []
    for pat, label in VIDEO_CODEC_RULES:
        if pat.search(blob) and label not in video_codecs:
            video_codecs.append(label)

    video_hdr: list[str] = []
    for pat, label in VIDEO_HDR_RULES:
        if pat.search(blob) and label not in video_hdr:
            video_hdr.append(label)

    video_source = ""
    for pat, label in VIDEO_SOURCE_RULES:
        if pat.search(blob):
            video_source = label
            break
    source_category = (
        "BluRay" if video_source in {"BluRay", "REMUX"}
        else video_source if video_source in {"Web-Rip", "Web-DL"}
        else "Other"
    )

    video_option = ""
    video_rank = 0
    for pat, label, rank in VIDEO_OPTION_RULES:
        if pat.search(blob):
            video_option = label
            video_rank = rank
            break
    if not video_option and resolution:
        video_option = "SDR"
        video_rank = 100

    video_formats: list[str] = []
    if resolution:
        video_formats.append(resolution)
    if video_source:
        video_formats.append(video_source)
    video_formats.extend(video_codecs)
    video_formats.extend(video_hdr)
    if video_option:
        video_formats.append(video_option)

    size_bytes, size_label = _parse_size(blob)

    return {
        "display_name": disp,
        "languages": languages,
        "audio_formats": audio_formats,
        "audio_options": audio_options,
        "audio_rank": audio_rank,
        "resolution": resolution,
        "resolution_rank": resolution_rank,
        "video_source": video_source,
        "source_category": source_category,
        "video_option": video_option,
        "video_rank": video_rank,
        "video_codecs": video_codecs,
        "video_hdr": video_hdr,
        "video_formats": video_formats,
        "size_bytes": size_bytes,
        "size_label": size_label,
    }


def enrich_link(item: dict[str, Any]) -> dict[str, Any]:
    url = str(item.get("url") or "")
    name = str(item.get("name") or "")
    tags = [str(t) for t in (item.get("tags") or []) if t]
    parsed = parse_release(name=name, url=url, tags=tags)
    return {
        **item,
        "parsed": parsed,
    }
