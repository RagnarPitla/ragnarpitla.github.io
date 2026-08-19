#!/usr/bin/env python3
"""Verify Everett source and built GitHub Pages output using only the stdlib."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import struct
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
import xml.etree.ElementTree as ET


THEME_BOOT = """<script>
  (() => {
    const param = new URLSearchParams(window.location.search).get("clawpilotTheme");
    const theme =
      param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  })();
</script>"""

CP_TOKENS = """/* cp-tokens:start */
:root {
  color-scheme: light;
  --cp-bg: #f7f4ef;
  --cp-bg-elevated: #fcfbf8;
  --cp-surface: #ffffff;
  --cp-surface-soft: #f5f5f5;
  --cp-border: #dedede;
  --cp-border-strong: #919191;
  --cp-text: #242424;
  --cp-text-muted: #5c5c5c;
  --cp-text-soft: #6f6f6f;
  --cp-accent: #b11f4b;
  --cp-accent-hover: #9a1a41;
  --cp-accent-soft: rgba(177, 31, 75, 0.08);
  --cp-accent-fg: #ffffff;
  --cp-success: #16a34a;
  --cp-danger: #dc2626;
  --cp-warning: #f59e0b;
  --cp-link: #0078d4;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
  --cp-overlay: rgba(255, 255, 255, 0.8);
  --cp-panel: rgba(255, 255, 255, 0.86);
  --cp-panel-strong: rgba(255, 255, 255, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.55);
  --cp-highlight: rgba(177, 31, 75, 0.12);
}

html[data-theme="dark"] {
  color-scheme: dark;
  --cp-bg: #3d3b3a;
  --cp-bg-elevated: #343231;
  --cp-surface: #292929;
  --cp-surface-soft: #2e2e2e;
  --cp-border: #474747;
  --cp-border-strong: #5f5f5f;
  --cp-text: #dedede;
  --cp-text-muted: #919191;
  --cp-text-soft: #b0b0b0;
  --cp-accent: #fd8ea1;
  --cp-accent-hover: #fb7b91;
  --cp-accent-soft: rgba(253, 142, 161, 0.14);
  --cp-accent-fg: #1a1a1a;
  --cp-success: #4ade80;
  --cp-danger: #f87171;
  --cp-warning: #fbbf24;
  --cp-link: #4da6ff;
  --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
  --cp-overlay: rgba(41, 41, 41, 0.88);
  --cp-panel: rgba(41, 41, 41, 0.72);
  --cp-panel-strong: rgba(41, 41, 41, 0.96);
  --cp-sheen: rgba(255, 255, 255, 0.04);
  --cp-highlight: rgba(253, 142, 161, 0.12);
}

@media (prefers-color-scheme: dark) {
  html:not([data-theme]) {
    color-scheme: dark;
    --cp-bg: #3d3b3a;
    --cp-bg-elevated: #343231;
    --cp-surface: #292929;
    --cp-surface-soft: #2e2e2e;
    --cp-border: #474747;
    --cp-border-strong: #5f5f5f;
    --cp-text: #dedede;
    --cp-text-muted: #919191;
    --cp-text-soft: #b0b0b0;
    --cp-accent: #fd8ea1;
    --cp-accent-hover: #fb7b91;
    --cp-accent-soft: rgba(253, 142, 161, 0.14);
    --cp-accent-fg: #1a1a1a;
    --cp-success: #4ade80;
    --cp-danger: #f87171;
    --cp-warning: #fbbf24;
    --cp-link: #4da6ff;
    --cp-shadow: 0 18px 48px rgba(0, 0, 0, 0.32);
    --cp-overlay: rgba(41, 41, 41, 0.88);
    --cp-panel: rgba(41, 41, 41, 0.72);
    --cp-panel-strong: rgba(41, 41, 41, 0.96);
    --cp-sheen: rgba(255, 255, 255, 0.04);
    --cp-highlight: rgba(253, 142, 161, 0.12);
  }
}
/* cp-tokens:end */"""

REQUIRED_TREE = {
    ".github/workflows/pages.yml",
    ".gitignore",
    "404.html",
    "README.md",
    "_config.yml",
    "_data/everett_truth.yml",
    "_everett_updates/2026-08-19-one-world-per-project.md",
    "_everett_updates/2026-08-19-the-web-model.md",
    "_everett_updates/2026-08-19-world-apps-direction.md",
    "_includes/everett-figure.html",
    "_includes/everett-footer.html",
    "_includes/everett-head.html",
    "_includes/everett-header.html",
    "_includes/everett-post-card.html",
    "_includes/everett-source-basis.html",
    "_includes/theme-boot.html",
    "_layouts/default.html",
    "_layouts/everett-post.html",
    "assets/css/site.css",
    "assets/images/brand/apple-touch-icon.png",
    "assets/images/brand/favicon.png",
    "assets/images/brand/favicon.svg",
    "assets/images/everett/full/board.png",
    "assets/images/everett/full/web-model.png",
    "assets/images/everett/full/world-apps-direction.png",
    "assets/images/everett/full/worlds-overview.png",
    "assets/images/everett/thumb/board.png",
    "assets/images/everett/thumb/web-model.png",
    "assets/images/everett/thumb/world-apps-direction.png",
    "assets/images/everett/thumb/worlds-overview.png",
    "assets/images/social/everett-og.png",
    "assets/js/everett-updates.js",
    "everett/feed.xml",
    "everett/index.html",
    "everett/updates/index.html",
    "index.html",
    "robots.txt",
    "scripts/verify_site.py",
    "sitemap.xml",
    "tools/everett-social-card.html",
}

POST_KEYS = {
    "layout", "title", "slug", "date", "summary", "description", "status",
    "status_label", "tags", "hero_image", "hero_thumbnail", "hero_width",
    "hero_height", "hero_alt", "hero_caption", "hero_kind", "og_image",
    "source_basis", "public_links",
}
STATUSES = {
    "product-thesis", "current-model", "design-direction", "shipping",
    "partial", "known-gap",
}
HERO_KINDS = {
    "current-product-screenshot", "historical-design-mockup", "design-direction",
}
EXPECTED_POSTS = [
    "one-world-per-project",
    "the-web-model",
    "world-apps-direction",
]
EXPECTED_POST_STATUS_LABELS = {
    "one-world-per-project": "Product thesis grounded in measured current evidence",
    "the-web-model": "Current product model",
    "world-apps-direction": "Design and MVP direction, not shipping",
}


class Checks:
    def __init__(self) -> None:
        self.total = 0
        self.failures: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        self.total += 1
        if not condition:
            self.failures.append(message)

    def finish(self) -> int:
        if self.failures:
            for failure in self.failures:
                print(f"FAIL: {failure}")
            print(f"{self.total - len(self.failures)} passed, {len(self.failures)} failed")
            return 1
        print(f"{self.total} passed, 0 failed")
        return 0


def png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()[:24]
    except OSError:
        return None
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def split_front_matter(path: Path) -> tuple[str, str] | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None
    return "\n".join(lines[1:end]), "\n".join(lines[end + 1:])


def front_matter_keys(front: str) -> set[str]:
    return {
        match.group(1)
        for line in front.splitlines()
        if (match := re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):", line))
    }


def scalar(front: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.*?)\s*$", front, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().strip("\"'")


def public_text_files(root: Path):
    skipped = {
        ".git", "_site", ".review", ".jekyll-cache", ".sass-cache",
        ".bundle", "vendor", "__pycache__",
    }
    binary_ext = {
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip",
        ".gz", ".woff", ".woff2", ".ttf", ".otf", ".dmg",
    }
    verifier = (root / "scripts/verify_site.py").resolve()
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in skipped for part in relative.parts):
            continue
        if path.resolve() == verifier or path.suffix.lower() in binary_ext:
            continue
        try:
            probe = path.read_bytes()[:4096]
        except OSError:
            continue
        if b"\0" in probe:
            continue
        yield path


def sensitive_markers(text: str) -> list[str]:
    findings = []
    private_url = "github" + ".com/" + "RagnarPitla/" + "everett"
    patterns = [
        (private_url, "private Everett repository URL"),
        ("/Users/", "local macOS absolute path"),
        ("/home/", "local Unix absolute path"),
        ("C:" + "\\Users\\", "local Windows absolute path"),
        ("-----BEGIN " + "PRIVATE KEY-----", "private key marker"),
    ]
    for marker, label in patterns:
        if marker.lower() in text.lower():
            findings.append(label)
    token_patterns = [
        re.compile("ghp" + r"_[A-Za-z0-9]{20,}"),
        re.compile("github" + r"_pat_[A-Za-z0-9_]{20,}"),
        re.compile("sk" + r"-[A-Za-z0-9]{20,}"),
        re.compile("AKIA" + r"[A-Z0-9]{16}"),
    ]
    if any(pattern.search(text) for pattern in token_patterns):
        findings.append("token-like secret")
    return findings


def css_declarations(block: str) -> list[tuple[str, str]]:
    return re.findall(r"(--cp-[\w-]+):\s*([^;]+);", block)


def source_verify(root: Path, checks: Checks) -> None:
    checks.check(root.is_dir(), f"source root does not exist: {root}")
    for rel in sorted(REQUIRED_TREE):
        checks.check((root / rel).is_file(), f"missing required file: {rel}")

    forbidden_names = {"Gemfile", "Gemfile.lock", ".nojekyll", "CNAME"}
    for path in root.rglob("*"):
        if ".git" in path.parts or ".review" in path.parts:
            continue
        checks.check(not path.is_symlink(), f"symlink is forbidden: {path.relative_to(root)}")
        if path.is_file():
            checks.check(path.name not in forbidden_names, f"forbidden file: {path.relative_to(root)}")

    tracked = ""
    try:
        tracked = subprocess.run(
            ["git", "-C", str(root), "ls-files"],
            check=True, capture_output=True, text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        pass
    for line in tracked.splitlines():
        checks.check(
            not re.match(r"^(?:_site|\.jekyll-cache|\.sass-cache|\.bundle|vendor)(?:/|$)", line),
            f"tracked build or cache output: {line}",
        )

    posts = sorted((root / "_everett_updates").glob("*.md"))
    checks.check(len(posts) == 3, "exactly three Everett update source documents are required")
    seen_dates: set[str] = set()
    seen_slugs: set[str] = set()
    newest_date: dt.date | None = None
    for post in posts:
        parsed = split_front_matter(post)
        checks.check(parsed is not None, f"invalid front matter delimiters: {post.name}")
        if not parsed:
            continue
        front, body = parsed
        keys = front_matter_keys(front)
        checks.check(POST_KEYS <= keys, f"missing front matter keys in {post.name}: {sorted(POST_KEYS - keys)}")
        status = scalar(front, "status")
        hero_kind = scalar(front, "hero_kind")
        slug = scalar(front, "slug") or ""
        date_value = scalar(front, "date") or ""
        checks.check(status in STATUSES, f"invalid status in {post.name}: {status}")
        checks.check(hero_kind in HERO_KINDS, f"invalid hero_kind in {post.name}: {hero_kind}")
        checks.check(slug not in seen_slugs and bool(slug), f"duplicate or empty slug: {slug}")
        checks.check(date_value not in seen_dates and bool(date_value), f"duplicate or empty date: {date_value}")
        seen_slugs.add(slug)
        seen_dates.add(date_value)
        try:
            post_date = dt.date.fromisoformat(date_value[:10])
            newest_date = max(newest_date, post_date) if newest_date else post_date
        except ValueError:
            checks.check(False, f"invalid date in {post.name}: {date_value}")
        checks.check(status not in re.findall(r"^\s*-\s+(.+?)\s*$", front, re.MULTILINE), f"status duplicated as tag in {post.name}")
        words = re.findall(r"\b[\w'-]+\b", re.sub(r"{%.*?%}", " ", body, flags=re.DOTALL))
        checks.check(800 <= len(words) <= 1400, f"{post.name} has {len(words)} words, expected 800-1400")
        checks.check("everett-figure.html" in body, f"{post.name} needs a contextual body figure")
        for key in ("hero_image", "hero_thumbnail", "og_image"):
            logical = scalar(front, key) or ""
            checks.check(logical.startswith("/") and ".." not in logical, f"invalid {key} path in {post.name}")
            checks.check((root / logical.lstrip("/")).is_file(), f"missing {key} file for {post.name}: {logical}")
        public_section = front.split("public_links:", 1)[-1]
        for url in re.findall(r"^\s+url:\s*[\"']?([^\"'\s]+)", public_section, re.MULTILINE):
            checks.check(url.startswith("https://"), f"non-HTTPS public link in {post.name}: {url}")

    truth_text = (root / "_data/everett_truth.yml").read_text(encoding="utf-8")
    truth_values = re.findall(r"^truth_as_of:\s*(\d{4}-\d{2}-\d{2})\s*$", truth_text, re.MULTILINE)
    checks.check(len(truth_values) == 1, "everett_truth.yml must contain exactly one truth_as_of value")
    if truth_values and newest_date:
        truth_date = dt.date.fromisoformat(truth_values[0])
        checks.check(newest_date >= truth_date, "newest post predates truth_as_of")
        checks.check((newest_date - truth_date).days <= 90, "truth_as_of is more than 90 days older than the newest post")

    config = (root / "_config.yml").read_text(encoding="utf-8")
    for marker in (
        "type: everett_updates",
        'site_section: "everett"',
        'schema_type: "article"',
    ):
        checks.check(marker in config, f"Everett collection defaults missing: {marker}")

    css_path = root / "assets/css/site.css"
    css = css_path.read_text(encoding="utf-8")
    checks.check(css.startswith(CP_TOKENS), "site.css does not preserve the exact cp token block")
    checks.check(css.count("/* cp-tokens:start */") == 1 and css.count("/* cp-tokens:end */") == 1, "cp token sentinels must occur exactly once")
    explicit = re.search(r'html\[data-theme="dark"\]\s*\{(.*?)\n\}', CP_TOKENS, re.DOTALL)
    fallback = re.search(r'html:not\(\[data-theme\]\)\s*\{(.*?)\n  \}', CP_TOKENS, re.DOTALL)
    checks.check(
        bool(explicit and fallback and css_declarations(explicit.group(1)) == css_declarations(fallback.group(1))),
        "explicit dark and no-JS fallback declarations differ",
    )
    outside = css[css.find("/* cp-tokens:end */") + len("/* cp-tokens:end */"):]
    checks.check(not re.search(r"--cp-[\w-]+\s*:", outside), "--cp-* variables may not be defined outside the token region")
    checks.check(not re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(", outside), "component CSS contains a literal color")
    checks.check(not re.search(r":\s*(?:black|white|red|blue|green|orange|purple|gray|grey)\b", outside, re.I), "component CSS contains a named color")
    checks.check(not re.search(r"@import|@font-face|url\s*\(", outside, re.I), "site.css contains an external/imported resource mechanism")
    checks.check(
        not re.search(r"color\s*:\s*var\(--cp-(?:link|warning|success|danger|text-muted)\)", outside),
        "forbidden contrast token used as text color",
    )
    checks.check("transform: none !important" not in outside, "reduced-motion CSS must not reveal transform-hidden content")
    checks.check(css_path.stat().st_size < 60 * 1024, "site.css exceeds 60 KiB")
    updates_js = (root / "assets/js/everett-updates.js").read_text(encoding="utf-8")
    checks.check(len(updates_js.encode("utf-8")) < 15 * 1024, "everett-updates.js exceeds 15 KiB")
    checks.check("replaceState" not in updates_js and "window.history" not in updates_js, "tag filter must not mutate browser history")

    checks.check((root / "_includes/theme-boot.html").read_text(encoding="utf-8").strip() == THEME_BOOT, "theme boot include differs from the required script")
    default_layout = (root / "_layouts/default.html").read_text(encoding="utf-8")
    head_include = (root / "_includes/everett-head.html").read_text(encoding="utf-8")
    checks.check("{% include everett-head.html %}" in default_layout, "default layout must include the shared head")
    checks.check(head_include.find("{% include theme-boot.html %}") < head_include.find('application/ld+json'), "theme boot must precede JSON-LD")

    expected_images = {
        "assets/images/everett/full/board.png": (1440, 900),
        "assets/images/everett/full/web-model.png": (1440, 900),
        "assets/images/everett/full/world-apps-direction.png": (1440, 900),
        "assets/images/everett/full/worlds-overview.png": (1440, 900),
        "assets/images/everett/thumb/board.png": (720, 450),
        "assets/images/everett/thumb/web-model.png": (720, 450),
        "assets/images/everett/thumb/world-apps-direction.png": (720, 450),
        "assets/images/everett/thumb/worlds-overview.png": (720, 450),
        "assets/images/social/everett-og.png": (1200, 630),
        "assets/images/brand/favicon.png": (64, 64),
        "assets/images/brand/apple-touch-icon.png": (180, 180),
    }
    for rel, dimensions in expected_images.items():
        checks.check(png_dimensions(root / rel) == dimensions, f"wrong PNG dimensions: {rel}")
    for path in (root / "assets/images/everett/full").glob("*.png"):
        checks.check(path.stat().st_size <= 1024 * 1024, f"full image exceeds 1 MiB: {path.name}")
    for path in (root / "assets/images/everett/thumb").glob("*.png"):
        checks.check(path.stat().st_size < 250 * 1024, f"thumbnail exceeds 250 KiB: {path.name}")
    checks.check((root / "assets/images/social/everett-og.png").stat().st_size < 500 * 1024, "OG image exceeds 500 KiB")
    asset_total = sum(path.stat().st_size for path in (root / "assets").rglob("*") if path.is_file())
    checks.check(asset_total < 4 * 1024 * 1024, f"assets exceed 4 MiB: {asset_total} bytes")

    external_resource = re.compile(
        r"<(?:script|img|source|iframe|audio|video)\b[^>]*(?:src|srcset)\s*=\s*[\"']https?://"
        r"|<link\b[^>]*rel\s*=\s*[\"'][^\"']*(?:stylesheet|icon)[^\"']*[\"'][^>]*href\s*=\s*[\"']https?://",
        re.I,
    )
    analytics = ("googletagmanager", "google-analytics", "segment.io", "plausible.io", "matomo", "mixpanel")
    for path in public_text_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(root)
        for finding in sensitive_markers(text):
            checks.check(False, f"{finding} in {rel}")
        checks.check(".." not in (scalar(split_front_matter(path)[0], "hero_image") or "") if path.suffix == ".md" and split_front_matter(path) else True, f"parent source path in {rel}")
        checks.check(not external_resource.search(text), f"third-party render-time resource in {rel}")
        checks.check(not any(marker in text.lower() for marker in analytics), f"analytics or tracker marker in {rel}")

    workflow = (root / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    for marker in (
        "actions/checkout@v7",
        "actions/jekyll-build-pages@v1.0.13",
        "actions/upload-pages-artifact@v5",
        "actions/deploy-pages@v5",
        "github.event_name == 'push' && github.ref == 'refs/heads/main'",
    ):
        checks.check(marker in workflow, f"workflow missing required marker: {marker}")
    checks.check("actions/configure-pages" not in workflow, "workflow must not use actions/configure-pages")
    checks.check(re.search(r"(?m)^permissions:\n  contents: read$", workflow) is not None, "workflow-level permissions must be contents: read")
    checks.check("pages: write" in workflow and "id-token: write" in workflow, "deploy job lacks Pages/OIDC permissions")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.h1_count = 0
        self.main_ids: list[str] = []
        self.body_classes: list[str] = []
        self.ids: set[str] = set()
        self.links: list[tuple[str, str]] = []
        self.resources: list[tuple[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.figure_depth = 0
        self.figure_stack: list[dict[str, object]] = []
        self.figures: list[dict[str, object]] = []
        self.first_focusable: tuple[str, dict[str, str]] | None = None
        self.title_parts: list[str] = []
        self.in_title = False
        self.meta: list[dict[str, str]] = []
        self.link_tags: list[dict[str, str]] = []
        self.json_blocks: list[str] = []
        self.in_json = False
        self.json_buffer: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        data = dict(attrs)
        if tag == "html":
            self.lang = data.get("lang", "")
        if tag == "h1":
            self.h1_count += 1
        if "id" in data:
            self.ids.add(data["id"])
        if tag == "main":
            self.main_ids.append(data.get("id", ""))
        if tag == "body":
            self.body_classes = (data.get("class") or "").split()
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            self.meta.append(data)
        if tag == "link":
            self.link_tags.append(data)
        if tag == "script" and data.get("type") == "application/ld+json":
            self.in_json = True
            self.json_buffer = []
        if tag == "figure":
            self.figure_depth += 1
            self.figure_stack.append({"images": 0, "caption": False})
        if tag == "figcaption" and self.figure_stack:
            self.figure_stack[-1]["caption"] = True
        if tag == "img":
            image = dict(data)
            image["_in_figure"] = "true" if self.figure_depth else "false"
            self.images.append(image)
            if self.figure_stack:
                self.figure_stack[-1]["images"] = int(self.figure_stack[-1]["images"]) + 1
        if tag == "a" and "href" in data:
            self.links.append(("href", data["href"]))
        if tag in {"script", "img", "source", "iframe", "audio", "video"}:
            for key in ("src", "srcset"):
                if data.get(key):
                    self.resources.append((key, data[key]))
        if tag == "link":
            rel = set((data.get("rel") or "").lower().split())
            if rel & {"stylesheet", "icon", "apple-touch-icon"} and data.get("href"):
                self.resources.append(("href", data["href"]))
        if not self.first_focusable:
            focusable = (
                (tag == "a" and "href" in data)
                or tag in {"button", "input", "select", "textarea"}
                or ("tabindex" in data and data["tabindex"] != "-1")
            )
            if focusable and "disabled" not in data:
                self.first_focusable = (tag, data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_json:
            self.in_json = False
            self.json_blocks.append("".join(self.json_buffer).strip())
        if tag == "figure" and self.figure_stack:
            self.figures.append(self.figure_stack.pop())
            self.figure_depth -= 1

    def handle_data(self, data: str) -> None:
        self.text_parts.append(data)
        if self.in_title:
            self.title_parts.append(data)
        if self.in_json:
            self.json_buffer.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())

    @property
    def text(self) -> str:
        return " ".join(" ".join(self.text_parts).split())


def route_for_html(root: Path, path: Path) -> str:
    rel = path.relative_to(root).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[:-10]
    return "/" + rel


def local_target(root: Path, value: str, current_route: str, origin: str) -> tuple[Path | None, str]:
    parsed = urlparse(urljoin(origin + current_route, value))
    if parsed.scheme in {"mailto", "tel", "data"}:
        return None, ""
    if parsed.scheme in {"http", "https"} and parsed.netloc != urlparse(origin).netloc:
        return None, ""
    logical = unquote(parsed.path)
    if logical.startswith("/chess-local-learning/"):
        return None, ""
    if logical.endswith("/"):
        target = root / logical.lstrip("/") / "index.html"
    else:
        target = root / logical.lstrip("/")
    return target, parsed.fragment


def built_verify(root: Path, origin: str, checks: Checks) -> None:
    expected = {
        "index.html",
        "everett/index.html",
        "everett/updates/index.html",
        "everett/updates/one-world-per-project/index.html",
        "everett/updates/the-web-model/index.html",
        "everett/updates/world-apps-direction/index.html",
        "everett/feed.xml",
        "sitemap.xml",
        "robots.txt",
        "404.html",
    }
    for rel in sorted(expected):
        checks.check((root / rel).is_file(), f"missing built output: {rel}")
    checks.check(not (root / "assets/css/style.css").exists(), "Primer style.css output is forbidden")

    pages: dict[str, PageParser] = {}
    raw_pages: dict[str, str] = {}
    titles: list[str] = []
    descriptions: list[str] = []
    for path in sorted(root.rglob("*.html")):
        raw = path.read_text(encoding="utf-8")
        route = route_for_html(root, path)
        parser = PageParser()
        parser.feed(raw)
        pages[route] = parser
        raw_pages[route] = raw
        titles.append(parser.title)
        desc = next((m.get("content", "") for m in parser.meta if m.get("name") == "description"), "")
        descriptions.append(desc)

        checks.check(parser.lang == "en-US", f"{route} must use lang=en-US")
        checks.check(parser.h1_count == 1, f"{route} has {parser.h1_count} H1 elements")
        checks.check(parser.main_ids == ["main"], f"{route} must have one main#main landmark")
        checks.check(
            bool(parser.first_focusable and parser.first_focusable[0] == "a"
                 and parser.first_focusable[1].get("href") == "#main"
                 and "skip-link" in parser.first_focusable[1].get("class", "")),
            f"{route} first focusable element must be Skip to content",
        )
        first_script = re.search(r"<script\b[^>]*>.*?</script>", raw, re.DOTALL | re.I)
        checks.check(bool(first_script and first_script.group(0).strip() == THEME_BOOT), f"{route} first script is not the exact theme boot script")

        canonical = next((tag.get("href", "") for tag in parser.link_tags if tag.get("rel") == "canonical"), "")
        checks.check(canonical == origin + route, f"wrong canonical on {route}: {canonical}")
        checks.check(bool(parser.title), f"missing title on {route}")
        checks.check(bool(desc), f"missing description on {route}")
        required_meta = {
            ("property", "og:title"), ("property", "og:description"), ("property", "og:url"),
            ("property", "og:type"), ("property", "og:image"), ("property", "og:image:alt"),
            ("name", "twitter:card"), ("name", "twitter:title"), ("name", "twitter:description"),
            ("name", "twitter:image"), ("name", "twitter:image:alt"),
        }
        present_meta = {
            (kind, meta.get(kind, ""))
            for meta in parser.meta
            for kind in ("name", "property")
            if meta.get(kind)
        }
        checks.check(required_meta <= present_meta, f"missing social metadata on {route}: {sorted(required_meta - present_meta)}")
        article_route = route.startswith("/everett/updates/") and route != "/everett/updates/"
        expected_og_type = "article" if article_route else "website"
        og_type = next(
            (meta.get("content", "") for meta in parser.meta if meta.get("property") == "og:type"),
            "",
        )
        checks.check(og_type == expected_og_type, f"wrong og:type on {route}: {og_type}")
        published = [
            meta.get("content", "")
            for meta in parser.meta
            if meta.get("property") == "article:published_time"
        ]
        article_tags = [
            meta.get("content", "")
            for meta in parser.meta
            if meta.get("property") == "article:tag"
        ]
        checks.check(
            bool(published) == article_route,
            f"article:published_time presence is wrong on {route}",
        )
        checks.check(
            bool(article_tags) == article_route,
            f"article:tag presence is wrong on {route}",
        )
        theme_colors = [m for m in parser.meta if m.get("name") == "theme-color"]
        checks.check(len(theme_colors) == 2, f"{route} needs light and dark theme-color metadata")
        rels = {" ".join((tag.get("rel") or "").split()): tag.get("href", "") for tag in parser.link_tags}
        checks.check(any("icon" in key for key in rels), f"{route} missing favicon")
        checks.check(any("apple-touch-icon" in key for key in rels), f"{route} missing Apple icon")
        checks.check(any(tag.get("type") == "application/atom+xml" for tag in parser.link_tags), f"{route} missing feed discovery")

        json_documents = []
        for block in parser.json_blocks:
            try:
                document = json.loads(block)
                valid = True
            except json.JSONDecodeError:
                valid = False
                document = None
            checks.check(valid, f"invalid JSON-LD on {route}")
            if valid:
                json_documents.append(document)
        checks.check(bool(parser.json_blocks), f"missing JSON-LD on {route}")
        if route == "/":
            expected_json_type = "WebSite"
        elif route == "/everett/":
            expected_json_type = "SoftwareApplication"
        elif article_route:
            expected_json_type = "Article"
        else:
            expected_json_type = "WebPage"
        json_types = {
            document.get("@type")
            for document in json_documents
            if isinstance(document, dict)
        }
        checks.check(
            expected_json_type in json_types,
            f"wrong JSON-LD type on {route}: expected {expected_json_type}, got {sorted(str(value) for value in json_types)}",
        )
        if article_route:
            slug = route.rstrip("/").rsplit("/", 1)[-1]
            status_label = EXPECTED_POST_STATUS_LABELS.get(slug, "")
            checks.check(status_label in parser.text, f"missing rendered status label on {route}")
            checks.check("everett-site" in parser.body_classes, f"{route} must render Everett chrome")
            checks.check(parser.title.endswith(" | Everett"), f"{route} title must end with | Everett")
            hrefs = {href for _, href in parser.links}
            for expected_href in (
                "/everett/",
                "/everett/#product-truth",
                "/everett/updates/",
                "/",
            ):
                checks.check(expected_href in hrefs, f"{route} missing Everett navigation link: {expected_href}")

        for image in parser.images:
            checks.check(bool(image.get("alt", "").strip()), f"image missing meaningful alt on {route}: {image.get('src')}")
            checks.check((image.get("width") or "").isdigit() and (image.get("height") or "").isdigit(), f"image missing numeric dimensions on {route}: {image.get('src')}")
            checks.check(image.get("_in_figure") == "true", f"image must be in a figure on {route}: {image.get('src')}")
        for figure in parser.figures:
            checks.check(bool(figure["images"]) and bool(figure["caption"]), f"figure without image and visible caption on {route}")

        checks.check("primer" not in raw.lower(), f"Primer reference on {route}")
        for finding in sensitive_markers(raw):
            checks.check(False, f"{finding} in built page {route}")

        for _, value in parser.resources:
            for candidate in value.split(","):
                url = candidate.strip().split()[0]
                parsed = urlparse(url)
                checks.check(not parsed.path.startswith("/ragnarpitla.github.io/"), f"repository-name baseurl duplication on {route}: {url}")
                checks.check(not (parsed.scheme in {"http", "https"} and parsed.netloc != urlparse(origin).netloc), f"third-party render resource on {route}: {url}")
                target, fragment = local_target(root, url, route, origin)
                if target is not None:
                    checks.check(target.is_file(), f"broken resource on {route}: {url}")
                    if fragment and target.suffix == ".html":
                        target_route = route_for_html(root, target)
                        checks.check(fragment in pages.get(target_route, PageParser()).ids, f"broken resource fragment on {route}: {url}")
        for _, href in parser.links:
            checks.check(not urlparse(href).path.startswith("/ragnarpitla.github.io/"), f"repository-name baseurl duplication on {route}: {href}")
            target, fragment = local_target(root, href, route, origin)
            if target is not None:
                checks.check(target.is_file(), f"broken link on {route}: {href}")
                if fragment and target.suffix == ".html":
                    target_route = route_for_html(root, target)
                    target_parser = pages.get(target_route)
                    if target_parser:
                        checks.check(fragment in target_parser.ids, f"broken link fragment on {route}: {href}")

    checks.check(len(set(titles)) == len(titles), "built HTML titles must be unique")
    checks.check(len(set(descriptions)) == len(descriptions), "built HTML descriptions must be unique")

    for route in ("/everett/", "/everett/updates/"):
        hrefs = [href for _, href in pages[route].links]
        positions = []
        for slug in EXPECTED_POSTS:
            target = f"/everett/updates/{slug}/"
            positions.append(next((i for i, href in enumerate(hrefs) if urlparse(href).path == target), -1))
        checks.check(all(index >= 0 for index in positions) and positions == sorted(positions), f"wrong post order on {route}")

    world_apps_routes = ["/everett/", "/everett/updates/", "/everett/updates/world-apps-direction/"]
    for route in world_apps_routes:
        text = pages[route].text.lower()
        checks.check(
            "design and mvp direction, not shipping" in text
            or "design direction, not shipping" in text
            or "design direction, not shipping behavior" in text,
            f"World Apps is not visibly marked as direction on {route}",
        )

    feed = root / "everett/feed.xml"
    try:
        feed_root = ET.parse(feed).getroot()
        atom = "{http://www.w3.org/2005/Atom}"
        entries = feed_root.findall(atom + "entry")
        feed_links = [entry.find(atom + "link").attrib.get("href", "") for entry in entries]
        feed_valid = feed_root.tag == atom + "feed"
    except (ET.ParseError, OSError, AttributeError):
        feed_valid = False
        feed_links = []
    checks.check(feed_valid, "feed.xml is not valid Atom 1.0")
    checks.check(feed_links == [f"{origin}/everett/updates/{slug}/" for slug in EXPECTED_POSTS], "feed entries are missing, relative, or out of order")

    try:
        sitemap_root = ET.parse(root / "sitemap.xml").getroot()
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        locations = {node.text for node in sitemap_root.findall(f"{ns}url/{ns}loc")}
        sitemap_valid = sitemap_root.tag == ns + "urlset"
    except (ET.ParseError, OSError):
        sitemap_valid = False
        locations = set()
    allowed = {
        origin + "/",
        origin + "/everett/",
        origin + "/everett/updates/",
        *(f"{origin}/everett/updates/{slug}/" for slug in EXPECTED_POSTS),
    }
    checks.check(sitemap_valid, "sitemap.xml is invalid XML")
    checks.check(locations == allowed, f"sitemap entries differ from exact allowed set: {sorted(locations ^ allowed)}")

    robots = (root / "robots.txt").read_text(encoding="utf-8").strip()
    checks.check("<" not in robots, "robots.txt contains HTML")
    checks.check("Allow: /" in robots, "robots.txt is missing Allow: /")
    checks.check(f"Sitemap: {origin}/sitemap.xml" in robots, "robots.txt points to the wrong sitemap")

    checks.check((root / "404.html").is_file(), "built 404 must be exactly _site/404.html")
    checks.check(
        any(meta.get("name") == "robots" and meta.get("content") == "noindex" for meta in pages["/404.html"].meta),
        "404 page must be noindex",
    )

    home = pages["/everett/"]
    initial_size = (root / "everett/index.html").stat().st_size
    for _, value in home.resources:
        for candidate in value.split(","):
            url = candidate.strip().split()[0]
            if any(image.get("src") == url and image.get("loading") == "lazy" for image in home.images):
                continue
            target, _ = local_target(root, url, "/everett/", origin)
            if target and target.is_file():
                initial_size += target.stat().st_size
    checks.check(initial_size < 900 * 1024, f"Everett homepage initial resources exceed 900 KiB: {initial_size}")

    scanned_text_files = list(public_text_files(root))
    scanned_relatives = {path.relative_to(root).as_posix() for path in scanned_text_files}
    for required in (
        "everett/feed.xml",
        "sitemap.xml",
        "robots.txt",
        "assets/css/site.css",
        "assets/js/everett-updates.js",
    ):
        checks.check(required in scanned_relatives, f"built privacy scan skipped required file: {required}")
    for path in scanned_text_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        checks.check("primer" not in text.lower(), f"Primer reference in built output: {path.relative_to(root)}")
        for finding in sensitive_markers(text):
            checks.check(False, f"{finding} in built output: {path.relative_to(root)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    source = sub.add_parser("source")
    source.add_argument("--root", required=True)
    built = sub.add_parser("built")
    built.add_argument("--root", required=True)
    built.add_argument("--origin", required=True)
    args = parser.parse_args()

    checks = Checks()
    root = Path(args.root).resolve()
    if args.mode == "source":
        source_verify(root, checks)
    else:
        built_verify(root, args.origin.rstrip("/"), checks)
    return checks.finish()


if __name__ == "__main__":
    sys.exit(main())
