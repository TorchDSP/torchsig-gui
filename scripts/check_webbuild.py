"""Checks that the rebuilt interface in torchsiggui/webbuild matches the committed build.

Next.js does not produce byte-identical output on every platform and Node.js version:
- Chunk file names are content hashes that change between macOS and Linux, even from the same source
- The HTML page data can be split into scripts differently, and the HTML tags can be emitted in a different order

So the rebuilt and committed builds are compared after normalizing those differences:
- Chunk file names are replaced with a placeholder, in file lists and in file contents
- Chunk contents are not compared, since they are what differs between platforms
- The HTML page data is joined back together, and its rows and the other HTML tags are compared in sorted order
- The lines of the text payloads are compared in sorted order
- Every other file must match exactly
"""

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

BUILD_DIR = 'torchsiggui/webbuild'
CHUNK_NAME = re.compile(r'(static/chunks/)(turbopack-)?[A-Za-z0-9_-]+\.(js|css)')
TAG_START = re.compile(r'(?=<)')
PAGE_DATA = re.compile(r'<script>self\.__next_f\.push\((\[.*?\])\)</script>', re.DOTALL)


# Replaces the hashed part of every chunk file name with a placeholder
def normalize_names(text: str) -> str:
  return CHUNK_NAME.sub(r'\1\2#.\3', text)


# Splits the HTML into the sorted tags outside the page data scripts and the sorted rows of the page data
def normalize_html(text: str) -> tuple[list[str], list[str]]:
  data = ''.join(item[1] for item in map(json.loads, PAGE_DATA.findall(text)) if len(item) > 1)
  return sorted(TAG_START.split(PAGE_DATA.sub('', text))), sorted(data.splitlines())


# Returns the parts of a file that are compared, independent of chunk hashes and ordering
def normalize_file(path: str, data: bytes) -> object:
  if CHUNK_NAME.search(path): return None
  if path.endswith('.html'): return normalize_html(normalize_names(data.decode()))
  if path.endswith(('.txt', '.js')): return sorted(normalize_names(data.decode()).splitlines())
  return data


# Reads the committed build from the git index, keyed by path
def read_committed() -> dict[str, bytes]:
  paths = subprocess.run(['git', 'ls-files', '-z', BUILD_DIR], capture_output=True, check=True).stdout
  files = {}
  for path in filter(None, paths.decode().split('\0')):
    files[path] = subprocess.run(['git', 'show', f':{path}'], capture_output=True, check=True).stdout
  return files


# Reads the rebuilt files from disk, keyed by path
def read_rebuilt() -> dict[str, bytes]:
  return {path.as_posix(): path.read_bytes() for path in sorted(Path(BUILD_DIR).rglob('*')) if path.is_file()}


# Compares the file lists and the normalized contents, and returns the differences
def compare(committed: dict[str, bytes], rebuilt: dict[str, bytes]) -> list[str]:
  problems = []

  # Compares the file lists, counting each chunk name placeholder as many times as it occurs
  committed_names = Counter(normalize_names(path) for path in committed)
  rebuilt_names = Counter(normalize_names(path) for path in rebuilt)
  for name in sorted((committed_names - rebuilt_names).keys()): problems.append(f'missing from rebuild: {name}')
  for name in sorted((rebuilt_names - committed_names).keys()): problems.append(f'not committed: {name}')

  # Compares the contents of the files present in both builds
  for path in sorted(committed.keys() & rebuilt.keys()):
    if normalize_file(path, committed[path]) != normalize_file(path, rebuilt[path]):
      problems.append(f'contents differ: {path}')
  return problems


def main() -> int:
  problems = compare(read_committed(), read_rebuilt())
  if not problems: return 0
  print('\n'.join(problems))
  print(f"{BUILD_DIR} is out of date. Run 'make build-web' and commit the result.")
  return 1


if __name__ == '__main__':
  sys.exit(main())
