#!/usr/bin/env python3
import os
import sys
import time
import requests
import xml.etree.ElementTree as ET
import tempfile
import hashlib
from pathlib import Path

# Hard-coded (replace these with your values)
PLEX_URL = 'url' #eg. http://localhost:32400
PLEX_TOKEN = 'token' #read README.md
LIBRARY = 'id' #eg 1

LOCK_DIR_NAME = '.poster-lockdir'
LOCK_ACQUIRE_TIMEOUT = 10  # seconds
LOCK_RETRY_DELAY = 0.1     # seconds

def get_all_media(section_id):
    url = f"{PLEX_URL}/library/sections/{section_id}/all?X-Plex-Token={PLEX_TOKEN}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return ET.fromstring(resp.content)

def get_media_path(video_tag):
    media_tag = video_tag.find('Media')
    if media_tag is None:
        return None
    part_tag = media_tag.find('Part')
    if part_tag is None:
        return None
    file_path = part_tag.get('file')
    if not file_path:
        return None
    return Path(os.path.dirname(file_path))

def get_poster_url(video_tag):
    poster = video_tag.get('thumb')
    if not poster:
        return None
    return f"{PLEX_URL}{poster}?X-Plex-Token={PLEX_TOKEN}"

def existing_poster_hashes(directory: Path):
    hashes = {}
    for p in directory.glob('poster*.jpg'):
        try:
            with p.open('rb') as f:
                hashes[p.name] = hashlib.sha256(f.read()).hexdigest()
        except Exception:
            continue
    return hashes

def next_filename(directory: Path):
    base = directory / 'poster.jpg'
    if not base.exists():
        return base
    i = 1
    while (directory / f'poster-{i}.jpg').exists():
        i += 1
    return directory / f'poster-{i}.jpg'

def acquire_lock(directory: Path, timeout=LOCK_ACQUIRE_TIMEOUT):
    lock_dir = directory / LOCK_DIR_NAME
    deadline = time.time() + timeout
    while True:
        try:
            os.mkdir(lock_dir)
            # optionally write PID/time info
            try:
                (lock_dir / 'owner').write_text(f"{os.getpid()}\n{time.time()}\n")
            except Exception:
                pass
            return lock_dir
        except FileExistsError:
            if time.time() > deadline:
                return None
            time.sleep(LOCK_RETRY_DELAY)
        except PermissionError:
            return None

def release_lock(lock_dir: Path):
    try:
        # remove owner file if present
        try:
            (lock_dir / 'owner').unlink(missing_ok=True)
        except Exception:
            pass
        os.rmdir(lock_dir)
    except Exception:
        pass

def download_poster_if_new(poster_url, directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    lock_dir = acquire_lock(directory)
    if lock_dir is None:
        return False  # couldn't get lock

    try:
        existing_hashes = existing_poster_hashes(directory)

        resp = requests.get(poster_url, stream=True, timeout=30)
        if resp.status_code != 200:
            return False

        hasher = hashlib.sha256()
        with tempfile.NamedTemporaryFile(dir=str(directory), delete=False) as tmp:
            tmp_name = Path(tmp.name)
            for chunk in resp.iter_content(8192):
                if chunk:
                    hasher.update(chunk)
                    tmp.write(chunk)
            tmp.flush()
            os.fsync(tmp.fileno())

        new_hash = hasher.hexdigest()
        if new_hash in existing_hashes.values():
            tmp_name.unlink(missing_ok=True)
            return False

        target = next_filename(directory)
        tmp_name.replace(target)
        try:
            target.chmod(0o644)
        except Exception:
            pass
        return True
    finally:
        release_lock(lock_dir)

def main():
    try:
        root = get_all_media(LIBRARY)
    except Exception as e:
        print(f"Failed to fetch library: {e}", file=sys.stderr)
        sys.exit(1)

    for video_tag in root.findall('.//Video'):
        try:
            media_dir = get_media_path(video_tag)
            if not media_dir:
                continue
            poster_url = get_poster_url(video_tag)
            if not poster_url:
                continue
            written = download_poster_if_new(poster_url, media_dir)
            if written:
                print(f"Saved new poster for {media_dir}")
            else:
                print(f"No new poster saved for {media_dir}")
        except Exception as e:
            print(f"Error handling video: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
