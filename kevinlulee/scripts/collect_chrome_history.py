from collections import Counter
from typing import TypedDict, List
import json
import re
from urllib.parse import urlparse
import kevinlulee as kx


def create_meta(contents, frontmatter={}, type=None):
    dt1 = kx.DateAccess(contents[0])
    dt2 = kx.DateAccess(contents[-1])
    month1, year1 = dt1.month_name, dt1.year
    month2, year2 = dt2.month_name, dt2.year

    date_range = f"{month1} {year1} to {month2} {year2}"
    data = {
        "contents": contents,
        "meta": {
            "author": "Kevin Lee",
            "created_at": kx.strftime(),
            "date_range": date_range,
            "frontmatter": frontmatter,
            "type": type,
        },
    }
    return data


class ComputedHistoryEntry(TypedDict):
    url: str
    category: str
    time: int


class HistoryEntry(TypedDict):
    favicon_url: str
    page_transition_qualifier: str
    title: str
    url: str
    time_usec: int
    client_id: str


def dedupe_google_chrome_history(
    history_data: List[HistoryEntry],
) -> List[ComputedHistoryEntry]:
    """
    Deduplicates browser history entries based on title or URL and
    assigns categories using get_category().
    """
    seen_titles = set()
    seen_urls = set()
    result = []
    counter = Counter()

    for entry in history_data:
        title = entry.get("title")
        url = entry.get("url")

        domain = urlparse(url).netloc
        category = categorize(domain)
        counter[category] += 1
        # need more fine grain categories and also need to make the control a bit easier.
        if control.get(category) == False:
            # skip
            continue

        # Skip duplicates by title OR URL
        if title in seen_titles or url in seen_urls:
            continue

        seen_titles.add(title)
        seen_urls.add(url)

        result.append(
            {
                "url": url,
                "title": title,
                "category": category,
                "time": entry.get("time_usec"),
            }
        )

    return dict(contents=result, counts=dict(counter), meta=meta)


import re
from typing import Dict, Any, List, Tuple, Pattern

# ---------- Templates ----------
# Match when ANY domain label equals one of the keys (works for subdomains too).
DOMAIN_LABEL_EQ_TEMPLATE = r"(?:^|\.)(?:{keys})(?:\.[a-z0-9-]+)*\.[a-z]{2,}$"

# Exact host (or any of its subdomains) equals one of the keys (keys may include dots via regex).
EXACT_HOST_OR_SUBDOMAIN_TEMPLATE = r"(?:^|\.)(?:{keys})$"

# host:port form, where host is one of the keys.
HOST_PORT_TEMPLATE = r"^(?:{keys}):\d+$"

# Exact whole-string match for keys (e.g., regex IDs).
EXACT_FULL_TEMPLATE = r"^(?:{keys})$"

# TLD-based (e.g., *.gov, *.mil, *.edu); allows optional country suffix like .gov.uk
TLD_TEMPLATE = r"^[\w.-]+\.(?:{keys})(?:\.[a-z]{2})?$"

# ---------- Category specs (keys-only) ----------
# Each category defines one or more "groups", each with:
#   - keys: list[str]
#   - template: str (optional; defaults to DOMAIN_LABEL_EQ_TEMPLATE)
#   - keys_are_regex: bool (optional; default False)
CATEGORY_SPECS: Dict[str, Dict[str, Any]] = {
    "local-dev": {
        "groups": [
            {
                "keys": ["127.0.0.1", "localhost", "0.0.0.0"],
                "template": HOST_PORT_TEMPLATE,
            }
        ],
        "flags": re.I,
    },
    "chrome-ext-id": {
        "groups": [
            {
                "keys": [r"[a-p]{32}"],  # lowercase a–p only
                "keys_are_regex": True,
                "template": EXACT_FULL_TEMPLATE,
            }
        ],
        "flags": 0,  # case-sensitive
    },
    # NOTE: git-hosting before cloud-sandbox so github.com doesn't get mis-bucketed.
    "git-hosting": {
        "groups": [
            {
                "keys": [
                    "github",
                    "gitlab",
                    "codeberg",
                    "githubhelp",
                    "github-wiki-see",
                    "github--wiki--see-page",
                    "githubusercontent",
                ],
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            },
            {
                # Matches git.<anything>
                "keys": [r"git\.[\w.-]+"],
                "keys_are_regex": True,
                "template": EXACT_HOST_OR_SUBDOMAIN_TEMPLATE,
            },
        ],
        "flags": re.I,
    },
    "cloud-sandbox": {
        "groups": [
            {
                "keys": [
                    "codesandbox",
                    "csb",
                    "stackblitz",
                    "replit",
                    "vercel",
                    "webcontainer-api",
                ],
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            },
            {
                # app.github.dev and github.dev
                "keys": [r"(?:app\.)?github\.dev"],
                "keys_are_regex": True,
                "template": EXACT_HOST_OR_SUBDOMAIN_TEMPLATE,
            },
        ],
        "flags": re.I,
    },
    "cdn-static": {
        "groups": [
            {
                # Any label starting with "cdn" (e.g., cdn, cdn1, cdn-assets)
                "keys": [r"cdn[\w-]*"],
                "keys_are_regex": True,
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            },
            {
                "keys": [
                    "jsdelivr",
                    "pages",
                    "cloudfront",
                    "s3",
                    "blob",
                    "fonts",
                    "shopify",
                    "camo",
                ],
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            },
        ],
        "flags": re.I,
    },
    "dev-docs-registries": {
        "groups": [
            {
                # Broad but practical: any host with these labels anywhere
                "keys": [
                    "docs",
                    "developer",
                    "developers",
                    "readthedocs",
                    "pypi",
                    "npmjs",
                    "crates",
                    "packages",
                    "luarocks",
                    "go",
                    "jsr",
                    "python",
                    "docker",
                    "mozilla",
                    "flutter",
                    "scala-lang",
                    "sympy",
                    "unity3d",
                ],
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            }
        ],
        "flags": re.I,
    },
    "ai-platforms": {
        "groups": [
            {
                "keys": [
                    "openai",
                    "anthropic",
                    "deepseek",
                    "mistral",
                    "huggingface",
                    "modelcontextprotocol",
                    "claude",
                ],
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            },
            {
                # x.ai specifically (avoid catching x.com from social)
                "keys": [r"x\.ai"],
                "keys_are_regex": True,
                "template": EXACT_HOST_OR_SUBDOMAIN_TEMPLATE,
            },
        ],
        "flags": re.I,
    },
    "social-media": {
        "groups": [
            {
                "keys": [
                    "x",
                    "twitter",
                    "facebook",
                    "instagram",
                    "discord",
                    "bsky",
                    "yelp",
                    "linkedin",
                    "tiktok",
                    "pinterest",
                ],
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            }
        ],
        "flags": re.I,
    },
    "dev-communities": {
        "groups": [
            {
                "keys": [
                    "ycombinator",
                    "stackoverflow",
                    "superuser",
                    "serverfault",
                    "askubuntu",
                    "stackexchange",
                    "discuss",
                    "discourse",
                    "python",
                    "codecademy",
                    "codemirror",
                    "prosemirror",
                    "julialang",
                    "jupyter",
                    "nixos",
                    "sublimetext",
                    "django",
                    "freecodecamp",
                    "freebsd",
                    "docker",
                    "rust-lang",
                    "scala-lang",
                    "neovim",
                ],
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            }
        ],
        "flags": re.I,
    },
    "gov-edu-civic": {
        "groups": [
            {
                # *.gov / *.mil / *.edu
                "keys": ["gov", "mil", "edu"],
                "template": TLD_TEMPLATE,
            },
            {
                # Common NYC civics
                "keys": [
                    "vote.nyc",
                    "ny.gov",
                    "elections.ny.gov",
                    "dmv.ny.gov",
                    "nysenate.gov",
                    "nycvotes.org",
                ],
                "template": EXACT_HOST_OR_SUBDOMAIN_TEMPLATE,
            },
        ],
        "flags": re.I,
    },
    "entertainment-media": {
        "groups": [
            {
                "keys": [
                    "youtube",
                    "viki",
                    "crunchyroll",
                    "soundcloud",
                    "streamable",
                    "vocaroo",
                    "typeracer",
                    "jstris",
                    "lichess",
                    "webtoons",
                    "gamerant",
                    "hianime",
                    "aniwave",
                    "anicrush",
                    "anilab",
                    "kissasian",
                ],
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            }
        ],
        "flags": re.I,
    },
    "news-media": {
        "groups": [
            {
                "keys": [
                    "apnews",
                    "reuters",
                    "nytimes",
                    "washingtonpost",
                    "bloomberg",
                    "theguardian",
                    "arstechnica",
                    "time",
                    "wired",
                    "variety",
                    "cnn",
                    "bbc",
                    "cnbc",
                    "newsweek",
                    "theatlantic",
                    "npr",
                    "gothamist",
                    "brooklyneagle",
                    "yaledailynews",
                    "slate",
                    "sfgate",
                    "politico",
                    "gizmodo",
                    "phys",
                    "spectrum",
                    "wikipedia",
                    "wiktionary",
                ],
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            }
        ],
        "flags": re.I,
    },
    "ecommerce-payments": {
        "groups": [
            {
                "keys": [
                    "amazon",
                    "ebay",
                    "walmart",
                    "bestbuy",
                    "costco",
                    "etsy",
                    "paypal",
                    "stripe",
                    "newegg",
                    "aliexpress",
                    "alibaba",
                    "zappos",
                    "target",
                ],
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            }
        ],
        "flags": re.I,
    },
    "nsfw-piracy": {
        "groups": [
            {
                "keys": [
                    "123movies",
                    "putlocker",
                    "xnxx",
                    "missav",
                    "bongacams",
                    "stripchat",
                    "javtiful",
                    "javtrailers",
                    "jav",
                    "18jav",
                    "megacloud",
                    "rutube",
                ],
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            }
        ],
        "flags": re.I,
    },
    "forums": {
        "groups": [
            {
                "keys": ["reddit", "quora"],
                "template": DOMAIN_LABEL_EQ_TEMPLATE,
            }
        ],
        "flags": re.I,
    },
    # Fallback: keys-only catch-all
    "other": {
        "groups": [
            {
                "keys": [r".*"],
                "keys_are_regex": True,
                "template": EXACT_FULL_TEMPLATE,
            }
        ],
        "flags": re.I,
    },
}

# Ordered: first match wins
CATEGORY_ORDER: List[str] = [
    "local-dev",
    "chrome-ext-id",
    "git-hosting",  # placed before cloud-sandbox on purpose
    "cloud-sandbox",
    "cdn-static",
    "dev-docs-registries",
    "ai-platforms",
    "social-media",
    "dev-communities",
    "gov-edu-civic",
    "entertainment-media",
    "news-media",
    "ecommerce-payments",
    "nsfw-piracy",
    "forums",
    "other",
]


def compile_category_patterns(
    specs: Dict[str, Dict[str, Any]],
    order: List[str],
) -> List[Tuple[str, Pattern]]:
    """
    Build an ordered list of (name, compiled_regex) from keys-only specs.
    Supports multiple groups per category; each group is OR'ed together.
    """
    compiled: List[Tuple[str, Pattern]] = []
    for name in order:
        spec = specs[name]
        flags = spec.get("flags", re.I)
        groups = spec.get("groups", [])
        if not groups:
            raise ValueError(
                f"Category '{name}' must define at least one group with 'keys'."
            )

        group_patterns: List[str] = []
        for g in groups:
            keys = g.get("keys", [])
            if not keys:
                continue
            keys_are_regex = g.get("keys_are_regex", False)
            template = g.get("template", DOMAIN_LABEL_EQ_TEMPLATE)

            if keys_are_regex:
                joined = "|".join(keys)
            else:
                # Normalize to lowercase (domains are case-insensitive) and escape metachars.
                joined = "|".join(re.escape(k.lower()) for k in keys)

            group_patterns.append(f"(?:{template.format(keys=joined)})")

        if not group_patterns:
            raise ValueError(f"Category '{name}' has no usable key groups.")

        pattern = "|".join(group_patterns)
        compiled.append((name, re.compile(pattern, flags)))

    return compiled


# Build the final ordered list for matching
CATEGORY_PATTERNS: List[Tuple[str, Pattern]] = compile_category_patterns(
    CATEGORY_SPECS, CATEGORY_ORDER
)


def classify_host(host: str) -> str:
    """Return the first category name that matches host; 'other' if none."""
    # Normalize host to lowercase for consistent matching.
    h = host.strip().lower()
    for name, rx in CATEGORY_PATTERNS:
        if rx.search(h):
            return name
    return "other"


def run():
    file = "/mnt/chromeos/MyFiles/Downloads/Takeout/Chrome/History.json"
    result = create_meta(
        dedupe_google_chrome_history(kx.readfile(file).get("Browser History")),
        type="collection",
    )
    name = result["meta"]["date_range"]
    cp_path = f"~/data/chrome-history/raw/{name}.json"
    dst_path = f"~/data/chrome-history/compiled/{name}.json"
    kx.writefile(dst_path, result)
    kx.cpfile(file, cp_path)
    # ~/data/chrome-history/


if __name__ == "__main__":
    run()
