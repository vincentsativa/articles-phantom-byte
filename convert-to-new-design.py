#!/usr/bin/env python3
"""Convert every legacy article HTML to the new V1 console design.

Strategy:
- Keep styles/main.css + styles/article.css + each article's own <style> blocks
  so all custom body classes (tables, zones, about-author, related-articles...)
  keep their styling. Inside-image placements (article-image-right) unchanged.
- Preserve the featured figure, top/bottom ad slots, and the ENTIRE article-body
  inner HTML byte-for-byte (raw extraction, no re-serialization).
- Preserve all <meta>, OG/Twitter, canonical, <title>, and JSON-LD blocks verbatim
  so seo-maintenance.py and SEO/analytics are untouched.
- Swap only the chrome: site-header -> new header+ticker+rail; article-header ->
  new article head; site-footer -> new footer; add constellation. GA + FCM push
  are site-wide identical (baked into template).
"""
import re, glob, os, html, sys
from datetime import datetime

TEMPLATE_FILE = "article-template-new.html"
EXCLUDE = {
    "index.html", "privacy.html", "terms.html", "test.html",
    "article-template.html", "article-template-v2.html", "article-template-v2-COPY.html",
    "article-template-v2-BACKUP-2026-03-28.html", "article-5-temp.html",
    "verify-systems.html", "index-template.html", "index-LEGACY-BACKUP.html",
    "article-template-new.html", "build-template.py", "convert-to-new-design.py",
}

def find_tag_end(text, idx):
    return text.index('>', idx) + 1

def extract_block(text, start_idx, open_name, close_name):
    """Extract from start_idx (the '<' of the opening tag) through the matching close,
    skipping tags inside <pre>, <code>, <script>, <style>, and HTML comments."""
    i = find_tag_end(text, start_idx)
    depth = 1
    skip = []
    n = len(text)
    while i < n and depth > 0:
        if text[i] == '<':
            if text.startswith('<!--', i):
                i = text.index('-->', i) + 3
                continue
            end = find_tag_end(text, i)
            inner = text[i+1:end-1].strip()
            is_close = inner.startswith('/')
            name = (inner[1:] if is_close else inner).split()[0].rstrip('/').lower()
            if not is_close and name in ('pre','code','script','style') and not skip and not text[i:end].rstrip('>').endswith('/'):
                skip.append(name); i = end; continue
            if skip:
                if is_close and name == skip[-1]:
                    skip.pop()
                i = end; continue
            if not is_close and name == open_name and not text[i:end].rstrip('>').endswith('/'):
                depth += 1
            elif is_close and name == close_name:
                depth -= 1
                if depth == 0:
                    return text[start_idx:end]
            i = end
        else:
            nxt = text.find('<', i); i = nxt if nxt != -1 else n
    return text[start_idx:i]

def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return html.unescape(s)

def first_match(pattern, text, flags=re.DOTALL):
    m = re.search(pattern, text, flags)
    return m.group(1) if m else None

def collect(pattern, text):
    return re.findall(pattern, text)

def make_deck(desc):
    if not desc:
        return ""
    if len(desc) <= 155:
        return desc
    return desc[:155].rsplit(' ', 1)[0] + '…'

def abbrev_level(level):
    if not level:
        return "Inter"
    m = {
        "intermediate": "Inter", "beginner": "Beg", "advanced": "Adv",
        "all": "All", "expert": "Expert",
    }
    return m.get(level.strip().lower(), level.strip()[:5])

def inject_h2_ids(body_html):
    """Inject id='sec-N' on <h2> tags that lack an id. Return (new_body, toc_items)."""
    toc = []
    counter = 0
    def repl(m):
        nonlocal counter
        attrs = m.group(1) or ""
        inner = m.group(2)
        if re.search(r'\bid\s*=', attrs):
            existing = re.search(r'\bid\s*=\s*"([^"]*)"', attrs)
            cid = existing.group(1) if existing else "sec-%d" % (len(toc)+1)
        else:
            counter += 1
            cid = "sec-%d" % counter
            attrs = attrs + ' id="%s"' % cid
        text = strip_tags(inner)
        if text:
            label = text if len(text) <= 48 else text[:47].rsplit(' ', 1)[0] + '…'
            toc.append((cid, label))
        return '<h2%s>%s</h2>' % (attrs, inner)
    new = re.sub(r'<h2([^>]*)>(.*?)</h2>', repl, body_html, flags=re.DOTALL)
    return new, toc

def build_toc(toc_items):
    if not toc_items:
        return '<ul class="toc" id="toc"><li class="arch-empty">No sections</li></ul>'
    items = []
    for cid, label in toc_items:
        items.append('<li><a href="#%s" data-target="%s">%s</a></li>' % (cid, cid, html.escape(label)))
    return '<ul class="toc" id="toc">' + ''.join(items) + '</ul>'

def convert_file(path, template, dry=False):
    raw = open(path, encoding='utf-8').read()
    # skip if already new design
    if '<aside class="rail"' in raw:
        return ("skip-new", None)
    if '<div class="article-body">' not in raw or '<header class="article-header">' not in raw:
        return ("skip-notarticle", None)

    out = template

    # ---- HEAD chunks (verbatim) ----
    # Collect ALL <meta> and <link> tags from the original <head>, in document order,
    # excluding site-wide tags already in the template (charset, viewport, author,
    # theme-color, favicon) and stylesheet links (re-added by template). This preserves
    # description, keywords, robots, p:domain_verify, OG, article:*, twitter:*, canonical,
    # alternate, etc. byte-for-byte.
    head_match = re.search(r'<head>(.*?)</head>', raw, re.DOTALL)
    head_html = head_match.group(1) if head_match else raw
    meta_bits = []
    skip_meta_names = {"viewport", "author", "theme-color"}
    for tag in re.findall(r'<meta\s[^>]*>', head_html):
        nm = re.search(r'name="([^"]+)"', tag)
        if nm and nm.group(1).lower() in skip_meta_names:
            continue
        if re.search(r'charset\s*=', tag):
            continue
        meta_bits.append(tag)
    for tag in re.findall(r'<link\s[^>]*>', head_html):
        rel = re.search(r'rel="([^"]+)"', tag)
        if rel and rel.group(1).lower() in {"stylesheet", "icon", "shortcut icon", "preload", "preconnect", "dns-prefetch"}:
            continue
        meta_bits.append(tag)
    head_meta = "\n".join(meta_bits)
    desc = first_match(r'<meta\s+name="description"\s+content="([^"]*)"', raw)

    title_tag = first_match(r'<title>(.*?)</title>', raw)
    title_tag = '<title>%s</title>' % title_tag if title_tag else '<title>PhantomByte</title>'

    jsonld = "\n".join(re.findall(r'<script\s+type="application/ld\+json">.*?</script>', raw, re.DOTALL))

    # article-specific <style> blocks (exclude phantombyte-push-styles)
    style_blocks = []
    for m in re.findall(r'<style(\s[^>]*)?>.*?</style>', raw, re.DOTALL):
        if 'id="phantombyte-push-styles"' in m[:60]:
            continue
        style_blocks.append(m)
    article_styles = "\n".join(style_blocks)

    # ---- metadata ----
    category = strip_tags(first_match(r'<span class="article-category">(.*?)</span>', raw) or "")
    if not category:
        category = first_match(r'property="article:section"\s+content="([^"]*)"', raw) or "AI Infrastructure"
    h1_inner = first_match(r'<h1 class="article-title">(.*?)</h1>', raw) or ""
    title_text = strip_tags(h1_inner)
    pub_date_text = strip_tags(first_match(r'<span class="publish-date">(.*?)</span>', raw) or "")
    read_time_text = strip_tags(first_match(r'<span class="read-time">(.*?)</span>', raw) or "")
    rt_num = (re.search(r'(\d+)', read_time_text) or re.search(r'"timeRequired":\s*"PT(\d+)M"', raw))
    read_time = (rt_num.group(1) + " min") if rt_num else "8 min"
    read_time_upper = rt_num.group(1) if rt_num else "8"
    # date ticker from meta
    date_iso = first_match(r'property="article:published_time"\s+content="([^"]*)"', raw) \
               or first_match(r'"datePublished":\s*"([^"]*)"', raw) or ""
    date_ticker = ""
    if date_iso:
        try:
            dt = datetime.strptime(date_iso[:10], "%Y-%m-%d")
            date_ticker = dt.strftime("%b %d %Y").upper()
        except Exception:
            date_ticker = ""
    if not date_ticker and pub_date_text:
        date_ticker = pub_date_text.upper()
    date_display = pub_date_text
    if not date_display and date_iso:
        try:
            dt = datetime.strptime(date_iso[:10], "%Y-%m-%d")
            date_display = dt.strftime("%B ") + str(dt.day) + dt.strftime(", %Y")
        except Exception:
            date_display = ""

    wordc = first_match(r'"wordCount":\s*"?(\d+)"?', raw)
    words = format(int(wordc), ",") if wordc else ""
    level = first_match(r'"proficiencyLevel":\s*"([^"]*)"', raw) or ""
    level_abbr = abbrev_level(level)

    # article number from featured image
    feat_img = first_match(r'<figure class="article-featured-image">.*?src="([^"]+)"', raw, re.DOTALL)
    note_num = ""
    if feat_img:
        nm = re.search(r'article-(\d+)-', feat_img)
        if nm:
            note_num = nm.group(1)
    if not note_num:
        nm = re.search(r'article-(\d+)-', raw)
        if nm:
            note_num = nm.group(1)

    # ---- body chunks (verbatim, balanced) ----
    m = re.search(r'<figure class="article-featured-image"', raw)
    featured = extract_block(raw, m.start(), 'figure', 'figure') if m else ""
    m = re.search(r'<div class="ad-slot ad-slot-article-top"', raw)
    top_ad = extract_block(raw, m.start(), 'div', 'div') if m else ""
    m = re.search(r'<div class="article-body"', raw)
    body_full = extract_block(raw, m.start(), 'div', 'div') if m else ""
    m = re.search(r'<div class="ad-slot ad-slot-article-bottom"', raw)
    bottom_ad = extract_block(raw, m.start(), 'div', 'div') if m else ""

    # inject h2 ids + build toc
    body_with_ids, toc_items = inject_h2_ids(body_full)
    toc_html = build_toc(toc_items)

    # deck
    deck = make_deck(desc)
    if not deck:
        cap = first_match(r'<figcaption class="image-caption">(.*?)</figcaption>', raw, re.DOTALL)
        deck = make_deck(strip_tags(cap or "")) if cap else title_text

    # ---- fill placeholders ----
    out = out.replace("{{HEAD_META}}", head_meta)
    out = out.replace("{{TITLE_TAG}}", title_tag)
    out = out.replace("{{JSONLD}}", jsonld)
    out = out.replace("{{ARTICLE_STYLES}}", article_styles)
    out = out.replace("{{NOTE_NUM}}", note_num)
    out = out.replace("{{CATEGORY_UPPER}}", html.escape(category.upper()))
    out = out.replace("{{CATEGORY}}", html.escape(category))
    out = out.replace("{{READ_TIME_UPPER}}", html.escape(read_time_upper))
    out = out.replace("{{DATE_TICKER}}", html.escape(date_ticker))
    out = out.replace("{{DATE_DISPLAY}}", html.escape(date_display))
    out = out.replace("{{READ_TIME}}", html.escape(read_time))
    out = out.replace("{{WORDS}}", html.escape(words))
    out = out.replace("{{LEVEL_ABBR}}", html.escape(level_abbr))
    out = out.replace("{{TOC}}", toc_html)
    out = out.replace("{{TITLE}}", html.escape(title_text))
    out = out.replace("{{DECK}}", html.escape(deck))
    out = out.replace("{{FEATURED_FIGURE}}", featured)
    out = out.replace("{{TOP_AD}}", top_ad)
    out = out.replace("{{ARTICLE_BODY}}", body_with_ids)
    out = out.replace("{{BOTTOM_AD}}", bottom_ad)

    # safety: no unfilled placeholders
    leftover = re.findall(r'{{[A-Z_]+}}', out)
    if leftover:
        return ("error-placeholders", leftover)

    if not dry:
        open(path, 'w', encoding='utf-8').write(out)
    return ("ok", out)

def main():
    template = open(TEMPLATE_FILE, encoding='utf-8').read()
    args = sys.argv[1:]
    if args and args[0] == "--test":
        # convert one file to a test output without overwriting
        src = args[1]
        res, content = convert_file(src, template, dry=True)
        if res == "ok":
            outp = "__test_converted.html"
            open(outp, 'w', encoding='utf-8').write(content)
            print("TEST wrote", outp, "from", src, "size", len(content))
        else:
            print("TEST", src, "->", res)
        return
    files = sorted(glob.glob("*.html"))
    ok = skip_new = skip_na = errors = 0
    for f in files:
        if f in EXCLUDE or f.startswith("verifying-agents-redesign"):
            continue
        res, extra = convert_file(f, template)
        if res == "ok":
            ok += 1
        elif res == "skip-new":
            skip_new += 1
        elif res == "skip-notarticle":
            skip_na += 1
        else:
            errors += 1
            print("ERROR", f, "->", res, extra)
    print("Converted: %d | skipped (already new): %d | skipped (not article): %d | errors: %d" % (ok, skip_new, skip_na, errors))

if __name__ == '__main__':
    main()