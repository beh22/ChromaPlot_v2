from __future__ import annotations

import re
import ssl
import certifi
import urllib.request
from dataclasses import dataclass

from packaging.version import Version, InvalidVersion

from chromaplot import __version__


VERSION_URL = (
    "https://raw.githubusercontent.com/beh22/ChromaPlot_v2/main/"
    "chromaplot/__init__.py"
)

CHANGELOG_URL = (
    "https://raw.githubusercontent.com/beh22/ChromaPlot_v2/main/"
    "CHANGELOG.md"
)

RELEASES_URL = "https://github.com/beh22/ChromaPlot_v2/releases"

@dataclass
class UpdateInfo:
    current_version: str
    latest_version: str
    release_url: str
    changelog_text: str | None = None

def fetch_text(url: str, timeout: int = 5) -> str:
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(url, timeout=timeout, context=context) as response:
        return response.read().decode("utf-8")
    
def extract_version(init_text: str) -> str:
    match = re.search(
        r"__version__\s*=\s*['\"]([^'\"]+)['\"]",
        init_text,
    )
    if not match:
        raise ValueError("Could not find __version__ in remote __init__.py")
    return match.group(1)

def extract_changelog_for_version(changelog_text: str, version: str) -> str | None:
    """
    Extract the section for a version from CHANGELOG.md. Should match lines like:
    ## [1.2.3] - 2024-06-01
    ## 1.2.3
    """
    pattern = (
        rf"^##\s+"
        rf"(?:Version\s+)?"
        rf"\[?{re.escape(version)}\]?"
        rf".*$"
    )
    match = re.search(pattern, changelog_text, flags=re.MULTILINE)
    
    if not match:
        return None
    
    start = match.end()
    next_heading = re.search(r"^##\s+", changelog_text[start:], flags=re.MULTILINE)

    if next_heading:
        end = start + next_heading.start()
        section = changelog_text[start:end]
    else:
        section = changelog_text[start:]


    return section.strip() or None

def check_for_update() -> UpdateInfo | None:
    """
    Check GitHub for a newer ChromaPlot version

    Returns UpdateInfo if an update is available, otherwise None
    Fails silently by returning None if the check cannot be completed
    """
    try:
        remote_init = fetch_text(VERSION_URL)
        latest_version = extract_version(remote_init)

        current = Version(__version__)
        latest = Version(latest_version)

        if latest <= current:
            return None
        
        changelog_text = None
        try:
            full_changelog = fetch_text(CHANGELOG_URL)
            changelog_text = extract_changelog_for_version(full_changelog, latest_version)
        except Exception:
            changelog_text = None

        return UpdateInfo(
            current_version=__version__,
            latest_version=latest_version,
            release_url=RELEASES_URL,
            changelog_text=changelog_text,
        )
    
    except (Exception, InvalidVersion):
        return None