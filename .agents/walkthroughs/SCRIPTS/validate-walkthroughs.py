#!/usr/bin/env python3
"""Validate .agents/walkthroughs/ against the rules in
INSTRUCTIONS/00-conventions.org, 01-index-guide.org, and
02-expansion-guide.org. Exits non-zero if any check fails.

Usage: .agents/walkthroughs/SCRIPTS/validate-walkthroughs.py
"""

import re
import sys
from pathlib import Path

WT_DIR = Path(__file__).resolve().parent.parent
ROOT = WT_DIR.parent.parent
INDEX = WT_DIR / "index.org"
CONVENTIONS = WT_DIR / "INSTRUCTIONS" / "00-conventions.org"
SKIP_DIRS = {"INSTRUCTIONS", "SCRIPTS"}

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
UUID_ANY_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I
)

failures = []
warnings = []
seen_uuids = {}  # lowercased uuid -> first location string


def fail(msg):
    failures.append(msg)


def warn(msg):
    warnings.append(msg)


def register_uuid(uuid, location):
    if not UUID_RE.match(uuid):
        fail(f"{location}: '{uuid}' is not a valid UUID")
        return
    key = uuid.lower()
    if key in seen_uuids:
        fail(f"{location}: UUID {uuid} collides with {seen_uuids[key]}")
    else:
        seen_uuids[key] = location


def extract_drawer_id(lines, start, stop):
    """First :ID: value inside a :PROPERTIES:...:END: drawer in lines[start:stop]."""
    in_drawer = False
    id_val = None
    for line in lines[start:stop]:
        s = line.strip()
        if s == ":PROPERTIES:":
            in_drawer = True
            continue
        if s == ":END:":
            in_drawer = False
            continue
        if in_drawer and re.match(r"^:ID:\s*", s, re.I):
            id_val = re.sub(r"^:ID:\s*", "", s, flags=re.I).strip()
    return id_val


def current_guide_version():
    if not CONVENTIONS.exists():
        fail(f"{CONVENTIONS.relative_to(ROOT)}: file is missing")
        return None
    text = CONVENTIONS.read_text()
    m = re.search(r"^#\+WALKTHROUGH_GUIDE_VERSION:\s*(\S+)", text, re.M)
    if not m:
        fail(f"{CONVENTIONS.relative_to(ROOT)}: missing #+WALKTHROUGH_GUIDE_VERSION:")
        return None
    return m.group(1)


def validate_index():
    """Returns {uuid: {"state", "title", "has_link", "loc"}}."""
    node_ids = {}
    if not INDEX.exists():
        fail(f"{INDEX.relative_to(ROOT)}: file is missing")
        return node_ids

    lines = INDEX.read_text().splitlines()
    heading_idxs = [i for i, l in enumerate(lines) if re.match(r"^\*+\s", l)]

    for i, line in enumerate(lines):
        m = re.match(r"^\*\*\*\s+(TODO|DONE)\s+(.*)$", line)
        if not m:
            continue
        state, title = m.group(1), m.group(2).strip()
        loc = f"index.org:{i + 1}"

        if UUID_ANY_RE.search(title):
            fail(f"{loc}: heading text contains a raw UUID: '{title}'")

        next_idx = next((h for h in heading_idxs if h > i), len(lines))
        node_id = extract_drawer_id(lines, i + 1, next_idx)
        if not node_id:
            fail(f"{loc}: node '{title}' has no :ID: drawer")
            continue
        register_uuid(node_id, loc)

        has_link = any(
            f"file:{node_id}/walkthrough.org" in l for l in lines[i + 1 : next_idx]
        )
        node_ids[node_id] = {
            "state": state,
            "title": title,
            "has_link": has_link,
            "loc": loc,
        }
        if state == "DONE" and not has_link:
            fail(f"{loc}: DONE node '{title}' has no walkthrough link")
        if state == "TODO" and has_link:
            warn(f"{loc}: TODO node '{title}' has a walkthrough link — should this be DONE?")

    return node_ids


def find_package_dirs():
    dirs = {}
    if not WT_DIR.is_dir():
        return dirs
    for p in WT_DIR.iterdir():
        if not p.is_dir() or p.name in SKIP_DIRS:
            continue
        if not UUID_RE.match(p.name):
            warn(f"{p.relative_to(ROOT)}: directory name is not a UUID, skipping")
            continue
        dirs[p.name] = p
    return dirs


def cross_check(node_ids, package_dirs):
    for node_id, info in node_ids.items():
        if info["state"] == "DONE" and node_id not in package_dirs:
            fail(
                f"{info['loc']}: DONE node '{info['title']}' has no matching "
                f".agents/walkthroughs/{node_id}/ directory"
            )
    for dir_id, path in package_dirs.items():
        rel = path.relative_to(ROOT)
        if dir_id not in node_ids:
            fail(f"{rel}: no matching index.org node for this UUID")
        elif node_ids[dir_id]["state"] != "DONE":
            fail(f"{rel}: package exists but index.org node is not DONE")


REQUIRED_SECTIONS = ["Notes", "Search Prompts", "Quiz"]


def count_numbered(lines, start, stop):
    return sum(1 for i in range(start, stop) if re.match(r"^\d+\.\s+\S", lines[i]))


def validate_walkthrough(wt_id, path, current_version):
    rel = path.relative_to(ROOT)
    text = path.read_text()
    lines = text.splitlines()

    top_headings = [(i, l) for i, l in enumerate(lines) if re.match(r"^\*\s+\S", l)]
    titles = [re.sub(r"^\*\s+", "", l).strip() for _, l in top_headings]

    if "Problem" not in titles:
        fail(f"{rel}: missing '* Problem' section")

    guide_idx = None
    for idx, (_, l) in enumerate(top_headings):
        if re.match(r"^\*\s+(TODO|DONE)\s+.*\[\d+/\d+\]", l):
            guide_idx = idx
            break
    if guide_idx is None:
        fail(f"{rel}: missing Guide checklist heading ('* TODO <title> [x/n]')")

    for name in REQUIRED_SECTIONS:
        if name not in titles:
            fail(f"{rel}: missing '* {name}' section")

    m = re.search(r"^#\+WALKTHROUGH_GUIDE_VERSION:\s*(\S+)", text, re.M)
    if not m:
        warn(f"{rel}: no #+WALKTHROUGH_GUIDE_VERSION: line")
    elif current_version and m.group(1) != current_version:
        warn(
            f"{rel}: guide version {m.group(1)} is behind current "
            f"({current_version}) — may be missing newer required sections"
        )

    for i, l in top_headings:
        if UUID_ANY_RE.search(l):
            fail(f"{rel}:{i + 1}: heading text contains a raw UUID")

    if guide_idx is not None:
        start = top_headings[guide_idx][0] + 1
        end = (
            top_headings[guide_idx + 1][0]
            if guide_idx + 1 < len(top_headings)
            else len(lines)
        )
        step_idxs = [
            i for i in range(start, end) if re.match(r"^-\s+\[[ Xx]\]\s+\S", lines[i])
        ]
        for si, step_i in enumerate(step_idxs):
            step_end = step_idxs[si + 1] if si + 1 < len(step_idxs) else end
            step_loc = f"{rel}:{step_i + 1}"
            if UUID_ANY_RE.search(lines[step_i]):
                fail(f"{step_loc}: step text contains a raw UUID")
            step_id = extract_drawer_id(lines, step_i + 1, step_end)
            if not step_id:
                fail(f"{step_loc}: checklist step has no :ID: drawer")
                continue
            register_uuid(step_id, step_loc)

    quiz_start = next(
        (i for i, l in enumerate(lines) if re.match(r"^\*\s+Quiz\s*$", l)), None
    )
    if quiz_start is not None:
        quiz_end = next(
            (
                i
                for i in range(quiz_start + 1, len(lines))
                if re.match(r"^\*\s+\S", lines[i])
            ),
            len(lines),
        )
        ak_start = next(
            (
                i
                for i in range(quiz_start + 1, quiz_end)
                if re.match(r"^\*\*\s+Answer Key\s*$", lines[i])
            ),
            None,
        )
        if ak_start is None:
            fail(f"{rel}: Quiz section has no '** Answer Key' subsection")
            qcount = count_numbered(lines, quiz_start + 1, quiz_end)
            acount = None
        else:
            qcount = count_numbered(lines, quiz_start + 1, ak_start)
            acount = count_numbered(lines, ak_start + 1, quiz_end)

        if qcount != 5:
            fail(f"{rel}: Quiz has {qcount} question(s), must be exactly 5")
        if acount is not None and acount != 5:
            fail(f"{rel}: Answer Key has {acount} entr(y/ies), must be exactly 5")


def main():
    current_version = current_guide_version()
    node_ids = validate_index()
    package_dirs = find_package_dirs()
    cross_check(node_ids, package_dirs)

    for wt_id, dir_path in sorted(package_dirs.items()):
        wt_file = dir_path / "walkthrough.org"
        if not wt_file.exists():
            fail(f"{dir_path.relative_to(ROOT)}: missing walkthrough.org")
            continue
        validate_walkthrough(wt_id, wt_file, current_version)

    for w in warnings:
        print(f"WARN: {w}")
    for f in failures:
        print(f"FAIL: {f}")

    print()
    print(f"{len(failures)} failure(s), {len(warnings)} warning(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
