import re

def parse_progress_original(line: str):
    """Extract percent from yt-dlp lines."""
    if "[download]" not in line or "%" not in line:
        return None
    parts = line.split()
    for p in parts:
        if p.endswith("%"):
            try:
                pct = float(p.strip("%"))
                return int(max(0, min(100, pct)))
            except:
                return None
    return None

def parse_progress_regex(line: str):
    """Extract percent using regex."""
    # Look for patterns like 45.0% or 45%
    match = re.search(r'(\d+(?:\.\d+)?)%', line)
    if match:
        try:
            pct = float(match.group(1))
            return int(max(0, min(100, pct)))
        except:
            return None
    return None

test_lines = [
    "[download]   0.0% of 10.00MiB at 100.00KiB/s ETA 01:42",
    "[download]  23.5% of 10.00MiB at 2.00MiB/s ETA 00:03",
    "[download] 100% of 10.00MiB in 00:05",
    "some other line",
    "[download] Destination: video.mp4"
]

print("Testing Original:")
for line in test_lines:
    print(f"'{line}' -> {parse_progress_original(line)}")

print("\nTesting Regex:")
for line in test_lines:
    print(f"'{line}' -> {parse_progress_regex(line)}")
