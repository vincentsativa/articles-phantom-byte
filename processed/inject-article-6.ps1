# Read the body content
$body = Get-Content -Path "C:\Users\Doter\workspace\articles\processed\article-6-body.html" -Raw -Encoding UTF8

# Read the template
$template = Get-Content -Path "C:\Users\Doter\workspace\articles\processed\article-6-the-ai-oversight-trap.html" -Raw -Encoding UTF8

# Find markers - use "Email Signup" comment
$introStart = $template.IndexOf("<!-- Introduction -->")
$emailSignupStart = $template.IndexOf("<!-- Email Signup -->")

# Extract parts to keep
$beforeIntro = $template.Substring(0, $introStart)
$afterSignup = $template.Substring($emailSignupStart)

# Build final HTML
$finalHtml = $beforeIntro + $body + $afterSignup

# Write to file
$finalHtml | Out-File -FilePath "C:\Users\Doter\workspace\articles\processed\article-6-the-ai-oversight-trap.html" -Encoding UTF8

Write-Host "Article 6 body injected successfully"
