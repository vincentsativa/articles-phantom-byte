#!/usr/bin/env python3
"""
PhantomByte SEO Maintenance Script
Auto-generates sitemap.xml, rss.xml, and llms.txt from article HTML files.
Validates SEO requirements. Submits new URLs to Google Indexing API.

Usage:
  python seo-maintenance.py              # Generate all + validate
  python seo-maintenance.py --sitemap    # Generate sitemap only
  python seo-maintenance.py --rss        # Generate RSS only
  python seo-maintenance.py --llms       # Generate llms.txt only
  python seo-maintenance.py --validate   # Validate SEO only
  python seo-maintenance.py --submit URL # Submit URL to Google Indexing API
  python seo-maintenance.py --submit-all # Submit all sitemap URLs to Google

This script is meant to be run BEFORE every deploy to ensure SEO assets are always current.
"""

import os
import sys
import re
import json
import glob
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import urllib.request
import urllib.error

# ─── Configuration ────────────────────────────────────────────────────────────

ARTICLES_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://articles.phantom-byte.com"
MAIN_SITE_URL = "https://phantom-byte.com"
SITEMAP_FILE = os.path.join(ARTICLES_DIR, "sitemap.xml")
RSS_FILE = os.path.join(ARTICLES_DIR, "rss.xml")
LLMS_FILE = os.path.join(ARTICLES_DIR, "llms.txt")

# Files to EXCLUDE from sitemap (not real articles)
EXCLUDE_FILES = {
    "index.html",
    "privacy.html",
    "terms.html",
    "test.html",
    "article-template.html",
    "article-template-v2.html",
    "article-template-v2-COPY.html",
    "article-template-v2-BACKUP-2026-03-28.html",
    "article-5-temp.html",
    "verify-systems.html",
}

# Duplicate articles — these are alternate versions of canonical articles.
# The canonical version is listed second.
DUPLICATE_ARTICLES = {
    "we-lost-47-minutes-session-persistence-lesson.html": "we-lost-47-minutes-session-persistence-langgraph.html",
    "we-lost-47-minutes-work-session-persistence-langgraph.html": "we-lost-47-minutes-session-persistence-langgraph.html",
    "ai-agent-session-persistence-patterns.html": "we-lost-47-minutes-session-persistence-langgraph.html",
    "ai-agent-session-persistence-best-practices.html": "we-lost-47-minutes-session-persistence-langgraph.html",
    "why-80-percent-multi-agent-ai-systems-fail.html": "why-80-percent-multi-agent-systems-fail.html",
    "alibaba-entered-agent-wars-openclaw.html": "alibaba-entered-agent-wars-openclaw-lessons.html",
}

CREDENTIALS_FILE = os.path.join(ARTICLES_DIR, "google-indexing-credentials.json")

# ─── HTML Metadata Extractor ──────────────────────────────────────────────────

class ArticleMetadata:
    """Extract SEO-relevant metadata from an article HTML file."""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.slug = self.filename
        self.url = f"{SITE_URL}/{self.slug}"
        self.title = ""
        self.description = ""
        self.date_published = ""
        self.date_modified = ""
        self.category = ""
        self.keywords = ""
        self.word_count = 0
        self.author = "Vinny Barreca"
        self.canonical = self.url
        self.og_image = ""
        self.read_time = "PT5M"
        self.is_valid = True
        self.errors = []
        self.warnings = []
        
        self._extract()
    
    def _extract(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.is_valid = False
            self.errors.append(f"Cannot read file: {e}")
            return
        
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
        if title_match:
            self.title = title_match.group(1).strip()
            # Remove " - PhantomByte" suffix
            if self.title.endswith(" - PhantomByte"):
                self.title = self.title[:-14]
        
        # Extract meta description
        desc_match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content)
        if desc_match:
            self.description = desc_match.group(1)
        
        # Extract publish date
        date_match = re.search(r'property="article:published_time"\s+content="([^"]*)"', content)
        if date_match:
            self.date_published = date_match.group(1)
        else:
            # Try JSON-LD
            date_match = re.search(r'"datePublished":\s*"([^"]*)"', content)
            if date_match:
                self.date_published = date_match.group(1)
        
        # Extract modified date
        mod_match = re.search(r'property="article:modified_time"\s+content="([^"]*)"', content)
        if mod_match:
            self.date_modified = mod_match.group(1)
        else:
            date_mod_json = re.search(r'"dateModified":\s*"([^"]*)"', content)
            if date_mod_json:
                self.date_modified = date_mod_json.group(1)
            else:
                self.date_modified = self.date_published
        
        # Extract category
        cat_match = re.search(r'property="article:section"\s+content="([^"]*)"', content)
        if cat_match:
            self.category = cat_match.group(1)
        else:
            cat_json = re.search(r'"articleSection":\s*"([^"]*)"', content)
            if cat_json:
                self.category = cat_json.group(1)
            else:
                self.category = "AI Infrastructure"
        
        # Extract keywords
        kw_match = re.search(r'<meta\s+name="keywords"\s+content="([^"]*)"', content)
        if kw_match:
            self.keywords = kw_match.group(1)
        else:
            kw_json = re.search(r'"keywords":\s*"([^"]*)"', content)
            if kw_json:
                self.keywords = kw_json.group(1)
        
        # Extract word count
        wc_match = re.search(r'"wordCount":\s*"?(\d+)"?', content)
        if wc_match:
            self.word_count = int(wc_match.group(1))
        else:
            # Estimate from content
            body_match = re.search(r'<article[^>]*>(.*?)</article>', content, re.DOTALL)
            if body_match:
                text = re.sub(r'<[^>]+>', ' ', body_match.group(1))
                self.word_count = len(text.split())
        
        # Extract read time
        rt_match = re.search(r'"timeRequired":\s*"([^"]*)"', content)
        if rt_match:
            self.read_time = rt_match.group(1)
        
        # Extract canonical
        canon_match = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', content)
        if canon_match:
            self.canonical = canon_match.group(1)
        
        # Extract OG image
        og_match = re.search(r'property="og:image"\s+content="([^"]*)"', content)
        if og_match:
            self.og_image = og_match.group(1)
        
        # ─── VALIDATION ──────────────────────────────────────────────────
        if not self.title:
            self.errors.append("Missing <title> tag")
        elif len(self.title) > 60:
            self.warnings.append(f"Title too long ({len(self.title)} chars): {self.title[:60]}...")
        
        if not self.description:
            self.errors.append("Missing meta description")
        elif len(self.description) > 160:
            self.warnings.append(f"Description too long ({len(self.description)} chars)")
        elif len(self.description) < 120:
            self.warnings.append(f"Description too short ({len(self.description)} chars)")
        
        if not self.date_published:
            self.errors.append("Missing datePublished")
        
        if not self.category:
            self.warnings.append("Missing category")
        
        if not self.og_image:
            self.warnings.append("Missing OG image")
        
        if self.word_count > 0 and self.word_count < 1500:
            self.warnings.append(f"Thin content ({self.word_count} words)")
    
    def __repr__(self):
        return f"Article({self.slug}, date={self.date_published}, cat={self.category})"


# ─── Sitemap Generator ────────────────────────────────────────────────────────

def generate_sitemap(articles):
    """Generate sitemap.xml from article metadata."""
    print("\n🗺️  Generating sitemap.xml...")
    
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    
    # Homepage
    lines.append(f'  <url>')
    lines.append(f'    <loc>{SITE_URL}/</loc>')
    lines.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
    lines.append(f'    <changefreq>daily</changefreq>')
    lines.append(f'    <priority>1.0</priority>')
    lines.append(f'  </url>')
    
    # Privacy & Terms
    for page in ["privacy.html", "terms.html"]:
        if os.path.exists(os.path.join(ARTICLES_DIR, page)):
            lines.append(f'  <url>')
            lines.append(f'    <loc>{SITE_URL}/{page}</loc>')
            lines.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
            lines.append(f'    <changefreq>monthly</changefreq>')
            lines.append(f'    <priority>0.3</priority>')
            lines.append(f'  </url>')
    
    # Articles — sorted by date, newest first
    sorted_articles = sorted(articles, key=lambda a: a.date_published or "0000-00-00", reverse=True)
    
    for article in sorted_articles:
        date = article.date_published or datetime.now().strftime("%Y-%m-%d")
        lines.append(f'  <url>')
        lines.append(f'    <loc>{article.url}</loc>')
        lines.append(f'    <lastmod>{date}</lastmod>')
        lines.append(f'    <changefreq>monthly</changefreq>')
        lines.append(f'    <priority>0.8</priority>')
        lines.append(f'  </url>')
    
    lines.append('</urlset>')
    
    content = '\n'.join(lines)
    
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    url_count = len(articles) + 3  # homepage + privacy + terms
    print(f"✅ sitemap.xml generated with {url_count} URLs ({len(articles)} articles)")
    return url_count


# ─── RSS Feed Generator ───────────────────────────────────────────────────────

def generate_rss(articles):
    """Generate rss.xml from article metadata."""
    print("\n📡 Generating rss.xml...")
    
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    sorted_articles = sorted(articles, key=lambda a: a.date_published or "0000-00-00", reverse=True)
    
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">',
        '  <channel>',
        f'    <title>PhantomByte Articles</title>',
        f'    <link>{SITE_URL}/</link>',
        f'    <description>AI Infrastructure • Agents • Orchestration Tutorials • Breakdowns • Insights That Ship</description>',
        f'    <language>en-us</language>',
        f'    <lastBuildDate>{now}</lastBuildDate>',
        f'    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>',
        f'    <image>',
        f'      <url>{SITE_URL}/images/article-1-main.jpg</url>',
        f'      <title>PhantomByte Articles</title>',
        f'      <link>{SITE_URL}/</link>',
        f'    </image>',
    ]
    
    # Include up to 50 most recent articles
    for article in sorted_articles[:50]:
        pub_date = article.date_published
        if pub_date:
            try:
                dt = datetime.strptime(pub_date, "%Y-%m-%d")
                rss_date = dt.strftime("%a, %d %b %Y 00:00:00 GMT")
            except:
                rss_date = now
        else:
            rss_date = now
        
        # Truncate description to 200 chars for RSS
        desc = article.description or article.title
        if len(desc) > 200:
            desc = desc[:197] + "..."
        
        lines.append(f'')
        lines.append(f'    <item>')
        lines.append(f'      <title>{_xml_escape(article.title)}</title>')
        lines.append(f'      <link>{article.url}</link>')
        lines.append(f'      <guid isPermaLink="true">{article.url}</guid>')
        lines.append(f'      <pubDate>{rss_date}</pubDate>')
        lines.append(f'      <category>{_xml_escape(article.category)}</category>')
        lines.append(f'      <author>vinny@phantom-byte.com (Vinny Barreca)</author>')
        lines.append(f'      <description>{_xml_escape(desc)}</description>')
        lines.append(f'    </item>')
    
    lines.append(f'  </channel>')
    lines.append('</rss>')
    
    content = '\n'.join(lines)
    
    with open(RSS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ rss.xml generated with {min(len(sorted_articles), 50)} articles")
    return min(len(sorted_articles), 50)


def _xml_escape(text):
    """Escape XML special characters."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    return text


# ─── llms.txt Generator ──────────────────────────────────────────────────────

def generate_llms(articles):
    """Generate llms.txt for AI search crawlers."""
    print("\n🤖 Generating llms.txt...")
    
    sorted_articles = sorted(articles, key=lambda a: a.date_published or "0000-00-00", reverse=True)
    
    lines = [
        f"# PhantomByte Articles",
        f"",
        f"> AI Infrastructure, Agents, Orchestration — Tutorials, Breakdowns, and Insights That Ship",
        f"",
        f"PhantomByte builds custom AI tools for small businesses. Our articles cover real-world deployments,",
        f"agent orchestration patterns, infrastructure lessons, and honest engineering breakdowns.",
        f"Written by Vinny Barreca. Updated regularly.",
        f"",
        f"## Articles ({len(sorted_articles)} total)",
        f"",
    ]
    
    for article in sorted_articles:
        date = article.date_published or "Unknown"
        lines.append(f"- [{article.title}]({article.url}): {article.description} ({date})")
    
    lines.append(f"")
    lines.append(f"## Free Tutorials")
    lines.append(f"")
    lines.append(f"- [The Sovereign AI Stack Blueprint](https://sovereign-ai-stack.phantom-byte.com/): Get the complete guide to building your own Sovereign AI Stack with Ollama, Hermes, and OpenClaw. Free tutorial for small business owners. (2026-05-15)")
    lines.append(f"")
    lines.append(f"## Navigation")
    lines.append(f"")
    lines.append(f"- [Home]({SITE_URL}/)")
    lines.append(f"- [Services]({MAIN_SITE_URL}/)")
    lines.append(f"- [About]({MAIN_SITE_URL}/about)")
    lines.append(f"- [RSS Feed]({SITE_URL}/rss.xml)")
    lines.append(f"- [Sitemap]({SITE_URL}/sitemap.xml)")
    
    content = '\n'.join(lines)
    
    with open(LLMS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ llms.txt generated with {len(sorted_articles)} articles")


# ─── SEO Validator ────────────────────────────────────────────────────────────

def validate_seo(articles):
    """Validate SEO requirements across all articles."""
    print("\n🔍 Validating SEO requirements...")
    
    errors = []
    warnings = []
    
    # Check sitemap matches articles
    sitemap_slugs = set()
    if os.path.exists(SITEMAP_FILE):
        with open(SITEMAP_FILE, 'r') as f:
            sitemap_content = f.read()
        sitemap_slugs = set(re.findall(r'<loc>https://articles\.phantom-byte\.com/([^<]+)</loc>', sitemap_content))
    
    article_slugs = {a.slug for a in articles}
    
    missing_from_sitemap = article_slugs - sitemap_slugs
    if missing_from_sitemap:
        errors.append(f"🔴 {len(missing_from_sitemap)} articles missing from sitemap: {missing_from_sitemap}")
    
    # Check required files
    for req_file in ['sitemap.xml', 'rss.xml', 'robots.txt', 'llms.txt']:
        path = os.path.join(ARTICLES_DIR, req_file)
        if not os.path.exists(path):
            errors.append(f"🔴 Missing required file: {req_file}")
    
    # Check missing OG images
    for img in ['og-featured.jpg', 'twitter-featured.jpg', 'phantombyte-logo.png']:
        path = os.path.join(ARTICLES_DIR, 'images', img)
        if not os.path.exists(path):
            warnings.append(f"🟡 Missing OG/social image: images/{img}")
    
    # Per-article validation
    for article in articles:
        if article.errors:
            errors.append(f"🔴 {article.slug}: {'; '.join(article.errors)}")
        if article.warnings:
            warnings.append(f"🟡 {article.slug}: {'; '.join(article.warnings)}")
    
    # RSS feed freshness
    if os.path.exists(RSS_FILE):
        with open(RSS_FILE, 'r') as f:
            rss_content = f.read()
        rss_date_match = re.search(r'<lastBuildDate>([^<]+)</lastBuildDate>', rss_content)
        if rss_date_match:
            try:
                rss_date = datetime.strptime(rss_date_match.group(1), "%a, %d %b %Y %H:%M:%S GMT")
                days_old = (datetime.now() - rss_date).days
                if days_old > 7:
                    warnings.append(f"🟡 RSS feed is {days_old} days old — regenerate it!")
            except:
                pass
    
    print(f"\n{'='*60}")
    print(f"SEO VALIDATION RESULTS")
    print(f"{'='*60}")
    print(f"Articles checked: {len(articles)}")
    print(f"Sitemap articles: {len(sitemap_slugs)}")
    print(f"Articles in sitemap: {len(sitemap_slugs & article_slugs)}")
    print(f"Articles missing from sitemap: {len(missing_from_sitemap)}")
    print(f"")
    
    if errors:
        print(f"🔴 ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
    
    if warnings:
        print(f"")
        print(f"🟡 WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")
    
    if not errors and not warnings:
        print("✅ All SEO checks passed!")
    
    return len(errors) == 0, errors, warnings


# ─── IndexNow + Sitemap Ping (Primary Indexing) ──────────────────────────────

INDEXNOW_KEY = "phantombyte2026"
INDEXNOW_KEY_URL = f"{SITE_URL}/{INDEXNOW_KEY}.txt"

INDEXNOW_ENDPOINTS = [
    "https://api.indexnow.org/IndexNow",
    "https://www.bing.com/indexnow",
    "https://indexes.yandex.com/indexnow",
]


def submit_to_indexnow(urls):
    """Submit URLs to search engines via IndexNow protocol.
    
    IndexNow is supported by Bing, Yandex, and others.
    It notifies search engines of new/updated content immediately.
    This is the PRIMARY indexing mechanism (works without API credentials).
    """
    if not urls:
        print("  No URLs to submit via IndexNow")
        return False
    
    print(f"\n  Submitting {len(urls)} URLs via IndexNow...")
    
    payload = json.dumps({
        "host": "articles.phantom-byte.com",
        "key": INDEXNOW_KEY,
        "keyLocation": INDEXNOW_KEY_URL,
        "urlList": urls
    }).encode('utf-8')
    
    success = False
    for endpoint in INDEXNOW_ENDPOINTS:
        try:
            req = urllib.request.Request(
                endpoint,
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            resp = urllib.request.urlopen(req, timeout=30)
            status = resp.status
            print(f"    {endpoint.split('/')[2]}: {status} OK")
            success = True
        except urllib.error.HTTPError as e:
            # 202 is also success for IndexNow
            if e.code == 202:
                print(f"    {endpoint.split('/')[2]}: 202 Accepted")
                success = True
            else:
                print(f"    {endpoint.split('/')[2]}: {e.code} {e.reason}")
        except Exception as e:
            print(f"    {endpoint.split('/')[2]}: Error - {str(e)[:80]}")
    
    return success


def ping_sitemaps():
    """Ping Google and Bing with updated sitemaps."""
    print("\n  Pinging search engines with sitemaps...")
    
    sitemaps = [
        (f"{SITE_URL}/sitemap.xml", "Articles"),
        (f"{MAIN_SITE_URL}/sitemap.xml", "Main site"),
    ]
    
    for sitemap_url, name in sitemaps:
        for engine, ping_url in [
            ("Google", f"https://www.google.com/ping?sitemap={sitemap_url}"),
            ("Bing", f"https://www.bing.com/ping?sitemap={sitemap_url}"),
        ]:
            try:
                resp = urllib.request.urlopen(ping_url, timeout=15)
                print(f"    {name} sitemap -> {engine}: {resp.status} OK")
            except Exception as e:
                print(f"    {name} sitemap -> {engine}: Error - {str(e)[:60]}")
    
    return True


# ─── Google Indexing API (Bonus - requires owner permission in GSC) ────────────

def submit_to_google(url):
    """Submit a URL to Google Indexing API (requires Owner permission in Search Console).
    
    Falls back gracefully if credentials are missing or permissions are wrong.
    IndexNow + sitemap pings handle the primary indexing.
    """
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"  [!] Google Indexing API not configured (no credentials file)")
        print(f"      IndexNow + sitemap pings handle indexing automatically.")
        print(f"      For faster indexing (1-24h), see INDEXING-API-FIX.md")
        return False
    
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        print("  [!] google-auth not installed. Run: pip install google-auth")
        return False
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=["https://www.googleapis.com/auth/indexing"]
        )
        
        session = AuthorizedSession(credentials)
        
        payload = {
            "url": url,
            "type": "URL_UPDATED"
        }
        
        response = session.post(
            "https://indexing.googleapis.com/v3/urlNotifications:publish",
            json=payload
        )
        
        if response.status_code == 200:
            print(f"  [OK] Google Indexing API: {url}")
            return True
        else:
            error_msg = response.text[:150]
            if "403" in str(response.status_code):
                print(f"  [!] Google API 403: Service account needs Owner permission in Search Console")
                print(f"      See INDEXING-API-FIX.md for fix steps")
            else:
                print(f"  [!] Google API error ({response.status_code}): {error_msg}")
            return False
    except Exception as e:
        print(f"  [!] Error: {e}")
        return False


def submit_all(articles):
    """Submit all articles to ALL indexing channels."""
    print("\n  Submitting to search engines...")
    
    # 1. IndexNow (primary, always works)
    article_urls = [a.url for a in articles]
    key_urls = [f"{SITE_URL}/", f"{SITE_URL}/sitemap.xml", f"{SITE_URL}/rss.xml"]
    all_urls = article_urls + key_urls
    
    # Submit in batches of 100 (IndexNow limit)
    for i in range(0, len(all_urls), 100):
        batch = all_urls[i:i+100]
        submit_to_indexnow(batch)
    
    # 2. Sitemap pings (Google + Bing)
    ping_sitemaps()
    
    # 3. Google Indexing API (bonus, may not work without Owner perm)
    google_ok = False
    if os.path.exists(CREDENTIALS_FILE):
        print("\n  Trying Google Indexing API...")
        for article in articles[:5]:  # Try first 5 to test
            if submit_to_google(article.url):
                google_ok = True
                break
        
        if google_ok:
            # If first test worked, submit the rest
            print(f"\n  Google API working! Submitting all {len(all_urls)} URLs...")
            for url in article_urls[5:]:
                submit_to_google(url)
            for url in key_urls:
                submit_to_google(url)
    
    print("\n  Submission complete!")
    print(f"    IndexNow: {len(all_urls)} URLs submitted to {len(INDEXNOW_ENDPOINTS)} engines")
    print(f"    Sitemaps: Pinged Google and Bing")
    print(f"    Google API: {'Used' if google_ok else 'Skipped (see INDEXING-API-FIX.md)'}")
    print(f"    Expected result: Articles indexed within 1-3 days")
    return True


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    
    do_sitemap = True
    do_rss = True
    do_llms = True
    do_validate = True
    do_submit = False
    do_submit_all = False
    submit_url = None
    
    if args:
        do_sitemap = do_rss = do_llms = do_validate = False
        for arg in args:
            if arg == "--sitemap":
                do_sitemap = True
            elif arg == "--rss":
                do_rss = True
            elif arg == "--llms":
                do_llms = True
            elif arg == "--validate":
                do_validate = True
            elif arg == "--submit":
                do_submit = True
                do_validate = False
            elif arg == "--submit-all":
                do_submit = True
                do_submit_all = True
                do_validate = False
            elif arg.startswith("--submit-url="):
                submit_url = arg.split("=", 1)[1]
                do_submit = True
                do_validate = False
            elif arg == "--all":
                do_sitemap = do_rss = do_llms = do_validate = True
            else:
                print(f"Unknown argument: {arg}")
                print("Usage: python seo-maintenance.py [--sitemap] [--rss] [--llms] [--validate] [--submit] [--submit-all]")
                sys.exit(1)
    
    print("═" * 60)
    print("  PhantomByte SEO Maintenance")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 60)
    
    # Collect all article files
    html_files = glob.glob(os.path.join(ARTICLES_DIR, "*.html"))
    
    articles = []
    for filepath in html_files:
        filename = os.path.basename(filepath)
        
        # Skip excluded files
        if filename in EXCLUDE_FILES:
            continue
        
        # Skip template files
        if filename.startswith("article-template") or filename == "article-5-temp.html":
            continue
        
        # Skip duplicates (they get a noindex canonical pointing to the original)
        if filename in DUPLICATE_ARTICLES:
            continue
        
        # Only include real articles (must have datePublished)
        article = ArticleMetadata(filepath)
        if article.date_published and article.title:
            articles.append(article)
        elif filename not in EXCLUDE_FILES:
            print(f"  ⚠️ Skipping {filename} (no date or title)")
    
    print(f"\n📄 Found {len(articles)} articles")
    
    if do_sitemap:
        generate_sitemap(articles)
    
    if do_rss:
        generate_rss(articles)
    
    if do_llms:
        generate_llms(articles)
    
    if do_validate:
        valid, errors, warnings = validate_seo(articles)
    
    if do_submit_all or do_submit:
        submit_all(articles)
    
    if submit_url:
        # Try Google API first, fall back to IndexNow
        if not submit_to_google(submit_url):
            submit_to_indexnow([submit_url])
            ping_sitemaps()
    
    print(f"\n{'═' * 60}")
    print(f"  Done! {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    main()