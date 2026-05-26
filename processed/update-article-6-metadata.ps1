# Update Article 6 Metadata - Simple Version

$file = "C:\Users\Doter\workspace\articles\processed\the-ai-oversight-trap.html"
$content = Get-Content -Path $file -Raw -Encoding UTF8

# Replace title
$content = $content.Replace('<title>How My AI Agent Went From Genius to Useless (And How I Fixed It) - PhantomByte</title>', '<title>The AI Oversight Trap: What Amazon Just Learned (We Already Solved) - PhantomByte</title>')

# Replace meta description
$content = $content.Replace('<meta name="description" content="How my AI agent went from genius to useless in 3 weeks. Real lessons on context bloat, session management, and fixing broken AI agents. Learn the 6 changes that saved me.">', '<meta name="description" content="Amazon just discovered what we learned through four painful iterations: AI-generated code without proper oversight leads to catastrophic failures. We built a complete system design that prevents the problem at the root.">')

# Replace keywords
$content = $content.Replace('<meta name="keywords" content="AI agent context bloat, AI agent session management, OpenClaw tutorial, AI performance degradation, Grok Heavy, Kimi K2.5, Qwen 3.5, PhantomByte">', '<meta name="keywords" content="AI oversight trap, Amazon AI outages, AI session management, context monitoring, auto-save AI, broken language, PhantomByte, system design AI">')

# Replace og:title
$content = $content.Replace('<meta property="og:title" content="How My AI Agent Went From Genius to Useless (And How I Fixed It)">', '<meta property="og:title" content="The AI Oversight Trap: What Amazon Just Learned (We Already Solved)">')

# Replace og:description
$content = $content.Replace('<meta property="og:description" content="I had a genius AI agent. Three weeks later, it couldn&apos;t set a reminder. The problem wasn&apos;t the model, it was me.">', '<meta property="og:description" content="Amazon just discovered what we learned through four painful iterations: AI-generated code without proper oversight, session management, and architectural guardrails leads to catastrophic failures.">')

# Replace og:image
$content = $content.Replace('<meta property="og:image" content="https://articles.phantom-byte.com/images/genius-to-useless-main.jpg">', '<meta property="og:image" content="https://articles.phantom-byte.com/images/article-6-main.jpg">')

# Replace og:url
$content = $content.Replace('<meta property="og:url" content="https://articles.phantom-byte.com/genius-to-useless-ai-agent">', '<meta property="og:url" content="https://articles.phantom-byte.com/the-ai-oversight-trap">')

# Replace twitter:title
$content = $content.Replace('<meta property="twitter:title" content="How My AI Agent Went From Genius to Useless (And How I Fixed It)">', '<meta property="twitter:title" content="The AI Oversight Trap: What Amazon Just Learned (We Already Solved)">')

# Replace twitter:description
$content = $content.Replace('<meta property="twitter:description" content="I had a genius AI agent. Three weeks later, it couldn&apos;t set a reminder. The problem wasn&apos;t the model, it was me.">', '<meta property="twitter:description" content="Amazon just discovered what we learned through four painful iterations: AI-generated code without proper oversight leads to catastrophic failures">')

# Replace twitter:image
$content = $content.Replace('<meta property="twitter:image" content="https://articles.phantom-byte.com/images/genius-to-useless-main.jpg">', '<meta property="twitter:image" content="https://articles.phantom-byte.com/images/article-6-main.jpg">')

# Replace canonical
$content = $content.Replace('<link rel="canonical" href="https://articles.phantom-byte.com/genius-to-useless-ai-agent">', '<link rel="canonical" href="https://articles.phantom-byte.com/the-ai-oversight-trap">')

# Replace date
$content = $content.Replace('content="2026-03-05"', 'content="2026-03-13"')

# Replace section
$content = $content.Replace('<meta property="article:section" content="AI Agents">', '<meta property="article:section" content="AI Infrastructure">')

# Replace articleSection in JSON-LD
$content = $content.Replace('"articleSection": "AI Agents"', '"articleSection": "AI Infrastructure"')

# Replace image in JSON-LD
$content = $content.Replace('"url": "https://articles.phantom-byte.com/images/genius-to-useless-main.jpg"', '"url": "https://articles.phantom-byte.com/images/article-6-main.jpg"')

# Replace mainEntityOfPage @id
$content = $content.Replace('"@id": "https://articles.phantom-byte.com/genius-to-useless-ai-agent"', '"@id": "https://articles.phantom-byte.com/the-ai-oversight-trap"')

# Write
$content | Out-File -FilePath $file -Encoding UTF8 -NoNewline

Write-Host "Article 6 metadata updated successfully"
