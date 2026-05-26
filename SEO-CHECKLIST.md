# SEO/GEO Checklist for PhantomByte Articles
**Quick Reference Guide** - Use this for every new article

---

## ✅ Pre-Publish Checklist (Every Article)

### Keyword Research (5 min):
- [ ] 1 Primary keyword identified
- [ ] 2-3 Secondary keywords selected
- [ ] 5+ Long-tail keyword variations noted
- [ ] Checked Google "People Also Ask" for related questions

### On-Page SEO:
- [ ] Primary keyword in `<title>` tag
- [ ] Primary keyword in first 100 words
- [ ] Primary keyword in H1 headline
- [ ] Secondary keywords in H2/H3 subheadings
- [ ] Meta description (150-160 chars, includes keyword)
- [ ] URL slug includes primary keyword

### Technical SEO:
- [ ] Open Graph tags filled (title, description, image)
- [ ] Twitter Card tags filled
- [ ] Article Schema (JSON-LD) added + customized
- [ ] FAQ Schema (JSON-LD) added + customized
- [ ] Canonical URL set
- [ ] Images have descriptive alt text (with keywords)
- [ ] Mobile-responsive (test on phone)
- [ ] Page loads in <3 seconds

### GEO Optimization:
- [ ] Executive Summary / TL;DR at top
- [ ] "Key Takeaways" box with bullet points
- [ ] FAQ section with 3-5 direct answers
- [ ] "What We Learned" section (authentic lessons)
- [ ] Definitive recommendations ("We recommend X because...")
- [ ] Comparison content (X vs Y) if applicable
- [ ] Specific data: error codes, dates, version numbers
- [ ] Citations/links to official documentation

### E-E-A-T (Trust Signals):
- [ ] Author bio (Vinny Barreca)
- [ ] Publish date visible
- [ ] Read time estimate
- [ ] Featured image with caption
- [ ] Internal links to other PhantomByte articles
- [ ] External links to authoritative sources
- [ ] Contact/about page accessible

### Content Quality:
- [ ] Hook in first paragraph (problem statement)
- [ ] Table of contents (if article >1000 words)
- [ ] screenshots/code examples where relevant
- [ ] Blockquotes for emphasis (1-2 max)
- [ ] Short paragraphs (2-4 sentences)
- [ ] Clear conclusion with call-to-action
- [ ] Email signup CTA at end
- [ ] "Buy Me a Coffee" CTA present

### Post-Publish:
- [ ] Submit URL to Google Search Console
- [ ] Share on social media (Twitter, LinkedIn)
- [ ] Add to email newsletter
- [ ] Monitor Search Console for indexing
- [ ] Track impressions/clicks after 7 days

---

## 🎯 Keyword Integration Template

**Replace bracketed placeholders in article-template.html:**

```
[ARTICLE TITLE] → Include primary keyword
[ARTICLE DESCRIPTION] → 150-160 chars, keyword + benefit
[PRIMARY KEYWORD] → Main target
[SECONDARY KEYWORDS] → Related terms
[ARTICLE-SLUG] → URL-friendly version of title
[FEATURED IMAGE URL] → Optimized image path
[PUBLISH DATE] → YYYY-MM-DD format
[WORD COUNT] → Actual count
[CATEGORY] → e.g., "Cloud Deployment", "DevOps", "Infrastructure"
```

---

## 🤖 GEO Answer Writing Formula

**For FAQ sections and direct answer paragraphs:**

```
Question: "[How do I fix Cloud Run 404 error]?"

Answer Structure:
1. Direct answer (first sentence): "To fix a Cloud Run 404 error, check your service URL and DNS configuration first."
2. Specific steps (numbered): "1. Verify service is running, 2. Check custom domain mapping, 3. Wait for SSL certificate"
3. Verifiable data: "SSL certificates typically take 5-30 minutes to issue on Cloud Run"
4. Common mistake: "Most 404 errors are caused by CNAME records pointing to the wrong target"
```

**Why this works for AI:**
- ✅ Direct answer first (AI extracts this)
- ✅ Numbered steps (easy to parse)
- ✅ Specific numbers/dates (AI trusts verifiable data)
- ✅ Addresses common pain point (shows expertise)

---

## 📊 Example: First Article Optimization

**Article:** "Why We Rebuilt Everything From Scratch (Infrastructure First)"

**Primary Keyword:** "infrastructure first deployment strategy"

**Secondary Keywords:**
- "lessons learned cloud deployment"
- "rebuilding tech stack 2026"
- "PhantomByte deployment approach"

**Long-Tail Keywords:**
- "should you rebuild from scratch"
- "infrastructure vs tools first approach"
- "why cloud projects fail from start"
- "best practices for cloud deployment 2026"

**FAQ Questions to Include:**
1. "What does 'infrastructure first' mean?"
2. "Why did you rebuild from scratch?"
3. "Is it worth rebuilding a project?"
4. "What are the risks of rebuilding?"
5. "How long does it take to rebuild infrastructure?"

**Key Takeaways Box:**
- ✅ Infrastructure-first prevents costly mistakes later
- ✅ Tools are useless without solid foundation
- ✅ Rebuilding taught us 20+ deployment lessons
- ✅ This approach saves time long-term despite short-term pain

**What We Learned Section:**
> "Building tools first felt productive, but we were stacking features on a broken foundation. Rebuilding from scratch wasn't failure—it was the smartest investment we made. Now every deployment is predictable because the foundation is solid. If you're facing the same choice: rebuild early, rebuild often, and don't let sunk cost fallacy trap you in bad architecture."

---

## 🔍 Quick SEO Wins

### 5-Minute Optimizations:
1. Add primary keyword to H1
2. Write meta description (use formula: "[Keyword] - [Benefit]. Learn [specific outcome].")
3. Add 2-3 internal links to other articles
4. Rename featured image file with keyword (`cloud-run-deployment-tutorial.jpg` not `IMG_1234.jpg`)
5. Add alt text to all images

### 15-Minute Optimizations:
1. Research "People Also Ask" questions on Google
2. Add FAQ section with 3-5 questions
3. Create "Key Takeaways" box
4. Add comparison table (if applicable)
5. Write "What We Learned" section

### 30-Minute Optimizations:
1. Full keyword research (primary + secondary + long-tail)
2. Write executive summary/TL;DR
3. Add schema markup (JSON-LD)
4. Optimize all images (compress + rename + alt text)
5. Submit to Google Search Console

---

## 📈 Success Metrics to Track

### Week 1:
- [ ] Indexed by Google (check `site:articles.phantom-byte.com/article-slug`)
- [ ] Search Console shows impressions
- [ ] At least 10 pageviews

### Month 1:
- [ ] Ranking on page 2-3 for primary keyword
- [ ] 50+ pageviews
- [ ] 5+ email signups from article
- [ ] 1+ social shares

### Month 3:
- [ ] Ranking page 1 for long-tail keywords
- [ ] 200+ pageviews/month
- [ ] AI citations (search article title in ChatGPT/Perplexity)
- [ ] PerformingCB ad clicks/revenue

---

## 🚨 Common Mistakes to Avoid

### SEO Don'ts:
- ❌ Keyword stuffing (unnatural repetition)
- ❌ Duplicate meta descriptions across articles
- ❌ Hidden text or links
- ❌ Buying backlinks
- ❌ Ignoring mobile optimization

### GEO Don'ts:
- ❌ Vague answers ("it depends" without specifics)
- ❌ No definitive recommendations
- ❌ Missing data/numbers/citations
- ❌ No FAQ section
- ❌ Unclear structure (AI can't parse it)

### General Don'ts:
- ❌ Publishing without proofreading
- ❌ No featured image
- ❌ No author bio
- ❌ No internal linking
- ❌ No call-to-action

---

## 🎯 The Play (Remember This):

**Learn → Break → Fix → Write → Monetize → Repeat**

Every article is:
- A lesson documented
- A mistake transformed into value
- A piece of content that works for you 24/7
- A building block for PhantomByte authority
- A potential revenue stream (PerformCB + email list)

**Write like you're helping a friend. Optimize like you're building an asset.**

---

**Created:** March 4, 2026  
**Location:** `C:\Users\Doter\workspace\articles\SEO-CHECKLIST.md`  
**Reference:** `SEO-GEO-KEYWORD-STRATEGY.md` (full strategy document)
