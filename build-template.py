#!/usr/bin/env python3
"""Build article-template-new.html from the approved V1 redesign file
by replacing the verifying-agents-specific chunks with placeholders."""
import re, sys, html

V1 = "verifying-agents-redesign-v1.html"
OUT = "article-template-new.html"

def find_tag(text, idx):
    """Return (tag_end_idx, tag_name, is_close, raw_tag) for the tag starting at idx (text[idx]=='<')."""
    end = text.index('>', idx)
    raw = text[idx:end+1]
    inner = text[idx+1:end].strip()
    is_close = inner.startswith('/')
    name = inner[1:].split()[0] if is_close else inner.split()[0]
    # strip trailing slash from name (self-closing)
    name = name.rstrip('/')
    return end+1, name, is_close, raw

def extract_block(text, start_idx, open_name, close_name):
    """Extract from start_idx (the '<' of the opening tag) through the matching close tag,
    skipping tags inside <pre>, <code>, <script>, <style>, and HTML comments."""
    i = text.index('>', start_idx) + 1
    depth = 1
    skip_stack = []  # names of regions whose tags we ignore
    n = len(text)
    while i < n and depth > 0:
        if text[i] == '<':
            if text.startswith('<!--', i):
                endc = text.index('-->', i)
                i = endc + 3
                continue
            tag_end, name, is_close, raw = find_tag(text, i)
            low = name.lower()
            # entering a skip region?
            if not is_close and low in ('pre','code','script','style') and not skip_stack:
                # only skip if it's a plain open tag (not self-closing)
                if not raw.rstrip('>').endswith('/'):
                    skip_stack.append(low)
                    i = tag_end
                    continue
            if skip_stack:
                # only watch for the close of the current skip region
                if is_close and low == skip_stack[-1]:
                    skip_stack.pop()
                i = tag_end
                continue
            # normal counting
            if not is_close and low == open_name:
                if not raw.rstrip('>').endswith('/'):
                    depth += 1
            elif is_close and low == close_name:
                depth -= 1
                if depth == 0:
                    return text[start_idx:tag_end]
            i = tag_end
        else:
            # advance to next '<'
            nxt = text.find('<', i)
            i = nxt if nxt != -1 else n
    return text[start_idx:i]

def main():
    t = open(V1, encoding='utf-8').read()

    # 1) <title>
    t = re.sub(r'<title>.*?</title>', '{{TITLE_TAG}}', t, count=1, flags=re.DOTALL)

    # 2) head meta block: description + keywords (per-article) and OG..canonical block
    t = re.sub(r'<meta name="description" content="[^"]*">\n'
               r'<meta name="keywords" content="[^"]*">\n', '', t, count=1)
    t = re.sub(r'<!-- Open Graph / Facebook -->.*?<link rel="canonical" [^>]*>',
               '{{HEAD_META}}', t, count=1, flags=re.DOTALL)

    # 3) JSON-LD TechArticle block
    t = re.sub(r'<!-- ARTICLE SCHEMA MARKUP.*?</script>\n', '{{JSONLD}}\n',
               t, count=1, flags=re.DOTALL)

    # 4) Insert external CSS + article-specific styles placeholder just before the inline <style>
    inline_style_anchor = '<style>\n*{margin:0;padding:0;box-sizing:border-box}'
    assert inline_style_anchor in t, "inline style anchor not found"
    t = t.replace(inline_style_anchor,
                  '<!-- Article content styling (preserved from original articles) -->\n'
                  '<link rel="stylesheet" href="styles/main.css">\n'
                  '<link rel="stylesheet" href="styles/article.css">\n'
                  '{{ARTICLE_STYLES}}\n'
                  '<!-- New console/chrome design (V1) -->\n'
                  '<style>\n*{margin:0;padding:0;box-sizing:border-box}', 1)

    # 5) Ticker
    t = t.replace('<span class="live"><span class="dot"></span>NOTE #111</span>',
                  '<span class="live"><span class="dot"></span>NOTE #{{NOTE_NUM}}</span>')
    t = t.replace('SECTION: <span class="cat">AI INFRASTRUCTURE</span>',
                  'SECTION: <span class="cat">{{CATEGORY_UPPER}}</span>')
    t = t.replace('<span class="next">8 MIN READ · JUN 27 2026</span>',
                  '<span class="next">{{READ_TIME_UPPER}} MIN READ · {{DATE_TICKER}}</span>')

    # 6) sec-kicker + category badge
    t = t.replace('// field note 111', '// field note {{NOTE_NUM}}')
    t = t.replace('<span class="article-category">AI Infrastructure</span>',
                  '<span class="article-category">{{CATEGORY}}</span>')

    # 7) h1 + deck
    t = re.sub(r'<h1 class="article-title">.*?</h1>',
               '<h1 class="article-title">{{TITLE}}</h1>', t, count=1, flags=re.DOTALL)
    t = re.sub(r'<p class="article-deck">.*?</p>',
               '<p class="article-deck">{{DECK}}</p>', t, count=1, flags=re.DOTALL)

    # 8) operator card date + meta grid
    t = t.replace('<div class="ac-date">June 27, 2026</div>',
                  '<div class="ac-date">{{DATE_DISPLAY}}</div>')
    t = t.replace('<div class="v">8 min</div>', '<div class="v">{{READ_TIME}}</div>')
    t = t.replace('<div class="v">1,700</div>', '<div class="v">{{WORDS}}</div>')
    t = t.replace('<div class="v">Inter</div>', '<div class="v">{{LEVEL_ABBR}}</div>')
    t = t.replace('<div class="v">#111</div>', '<div class="v">#{{NOTE_NUM}}</div>')

    # 9) TOC
    t = re.sub(r'<ul class="toc" id="toc">.*?</ul>', '{{TOC}}', t, count=1, flags=re.DOTALL)

    # 10) featured figure (balanced <figure>)
    m = re.search(r'<figure class="figure"', t)
    assert m, "figure not found"
    fig = extract_block(t, m.start(), 'figure', 'figure')
    t = t.replace(fig, '{{FEATURED_FIGURE}}', 1)

    # 11) top ad slot (balanced div)
    m = re.search(r'<div class="ad-slot ad-slot-article-top"', t)
    assert m, "top ad not found"
    top = extract_block(t, m.start(), 'div', 'div')
    t = t.replace(top, '{{TOP_AD}}', 1)

    # 12) article body (balanced div)
    m = re.search(r'<div class="article-body">', t)
    assert m, "article-body not found"
    body = extract_block(t, m.start(), 'div', 'div')
    t = t.replace(body, '{{ARTICLE_BODY}}', 1)

    # 13) bottom ad slot (balanced div)
    m = re.search(r'<div class="ad-slot ad-slot-article-bottom"', t)
    assert m, "bottom ad not found"
    bot = extract_block(t, m.start(), 'div', 'div')
    t = t.replace(bot, '{{BOTTOM_AD}}', 1)

    # 14) add scroll-margin for h2[id] so TOC jumps aren't hidden under sticky header
    t = t.replace('section[id]{scroll-margin-top:104px}',
                  'section[id]{scroll-margin-top:104px}\nh2[id]{scroll-margin-top:112px}')

    open(OUT, 'w', encoding='utf-8').write(t)

    # report placeholders present
    ph = sorted(set(re.findall(r'{{[A-Z_]+}}', t)))
    print("Template written:", OUT, "size", len(t))
    print("Placeholders:", ph)
    leftover = []
    for needle in ['Verifying Agents', 'NOTE #111', 'AI INFRASTRUCTURE', 'field note 111',
                   'June 27, 2026', '8 min</div>', '1,700', '#111', 'article-111-main.jpg']:
        if needle in t:
            leftover.append(needle)
    print("Leftover verifying-agents content (should be empty):", leftover)

if __name__ == '__main__':
    main()