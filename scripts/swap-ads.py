"""
Ad Swap Script for PhantomByte Articles
========================================
Swaps old ad creatives with new ad creatives across multiple HTML files.

Usage:
    python scripts/swap-ads.py

Backup:
    Always creates a backup before making changes.

Author: PhantomByte
Last updated: 2026-04-16
"""

import os
import re
import shutil
from datetime import datetime

# Configuration
ARTICLES_DIR = "C:/Users/Doter/workspace/articles"
BACKUP_DIR = f"C:/Users/Doter/workspace/articles/backup-ad-swap-{datetime.now().strftime('%Y-%m-%d')}"

# The new loan ad HTML (dark gradient with "Compare Best Personal Loans")
NEW_LOAN_AD = '''<div class="ad-creative" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 24px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 255, 136, 0.25); border: none;">
                            <p style="font-size: 0.7rem; color: #9D4EDD; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">⚡ Partner Offer</p>
                            <h4 style="margin: 0 0 12px 0; color: #ffffff; font-size: 1.3rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">Compare Best Personal Loans</h4>
                            <p style="margin: 0 0 16px 0; font-size: 0.95rem; line-height: 1.5; color: #e0e0e0; font-weight: 400;">Get the funding you need with competitive rates starting at 5.99% APR. Quick online application, no impact to credit score for checking.</p>
                            <div style="text-align: center;">
                                <span style="display: inline-block; padding: 11px 22px; background: linear-gradient(90deg, #00FF88 0%, #00cc6a 100%); color: #0a0a1a; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.95rem; box-shadow: 0 3px 10px rgba(0, 255, 136, 0.35); margin-bottom: 8px;">Check Your Rate</span>
                                <p style="margin: 0; font-size: 0.8rem; color: #a8a8c9; font-weight: 500;">🔒 Free to start</p>
                            </div>
                        </div>'''

# Files to process (relative paths from ARTICLES_DIR)
FILES_TO_PROCESS = [
    "300-raspberry-pi-dram-shortage-self-hosted-ai-economics.html",
    "86-enterprises-chasing-agentic-edge-ai.html",
    "ai-agent-reliability-production-monitoring.html",
    "ai-agent-session-persistence-patterns.html",
    "ai-chip-unbundling-turboquant-arm-meta-edge.html",
    "ai-infrastructure-shift-oracle-shopify-agentic-ai.html",
    "ai-orchestration-how-i-got-it-wrong-4-times.html",
    "ai-revolution-isnt-coming-its-yesterdays-news.html",
    "alibaba-entered-agent-wars-openclaw-lessons.html",
    "best-ai-agent-orchestration-beginners.html",
    "building-production-ready-mcp-servers-security-best-practices-2026.html",
    "claude-code-just-got-worse-for-real-engineering-work.html",
    "four-research-breakthroughs-ai-paralysis.html",
    "genius-to-useless-ai-agent.html",
    "global-agent-wars-china-subsidizing-openclaw-nvidia-nemoclaw.html",
    "how-ai-is-becoming-a-liberation-tool.html",
    "how-to-work-with-ai-agents-collaboration.html",
    "how-we-found-our-ai-breaking-point.html",
    "is-the-ai-honeymoon-over-inside-rprogramming-llm-ban.html",
    "perfect-storm-is-here-why-ai-offense-is-crushing-defense-and-which-companies-build-real-moats.html",
    "self-hosted-ai-security-local-llm-vulnerabilities.html",
    "the-50k-token-bomb-when-ai-cost-controls-fail.html",
    "the-512k-line-leak-claude-code-exposed-architecture.html",
    "the-900-month-question-sovereign-ai-april-4th-crackdown.html",
    "the-digital-cage-how-an-ai-algorithm-stole-five-months-from-angela-lipps.html",
    "the-rise-of-answer-engine-optimization-geo-aoe.html",
    "we-deployed-20-websites-cloud-run-brutal-truth-serverless.html",
    "we-lost-47-minutes-session-persistence-langgraph.html",
    "we-lost-47-minutes-session-persistence-lesson.html",
    "we-lost-47-minutes-work-session-persistence-langgraph.html",
    "when-your-ai-agent-runs-in-circles-debug-guide.html",
    "why-80-percent-multi-agent-ai-systems-fail.html",
    "why-80-percent-multi-agent-systems-fail.html",
    "why-openclaw-locally-beats-vps.html",
    "why-tufts-neuro-symbolic-ai-changes-everything.html",
    "why-your-ai-agent-went-paralyzed.html",
]

# Patterns to match old ads (purple gradient with various headers)
OLD_AD_PATTERNS = [
    # Purple gradient with "Build AI" text
    re.compile(
        r'<div class="ad-creative" style="background: linear-gradient\(135deg, #667eea 0%, #764ba2 100%\);[^>]*>.*?<h4 style="[^"]*">Build AI[^<]*</h4>.*?</div>\s*</div>\s*</a>\s*</div>\s*</div>',
        re.DOTALL
    ),
    # Purple gradient with "Partner Offer" (lightbulb emoji)
    re.compile(
        r'<div class="ad-creative" style="background: linear-gradient\(135deg, #667eea 0%, #764ba2 100%\);[^>]*>.*?&#128161; Partner Offer.*?</div>\s*</div>\s*</a>\s*</div>\s*</div>',
        re.DOTALL
    ),
    # Purple gradient with "Sponsored" text
    re.compile(
        r'<div class="ad-creative" style="background: linear-gradient\(135deg, #667eea 0%, #764ba2 100%\);[^>]*>.*?Sponsored.*?</div>\s*</div>\s*</a>\s*</div>\s*</div>',
        re.DOTALL
    ),
]

def create_backup():
    """Create a backup of all HTML files before making changes."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"[BACKUP] Creating backup directory: {BACKUP_DIR}")
        
        # Copy all HTML files to backup
        for filename in os.listdir(ARTICLES_DIR):
            if filename.endswith('.html'):
                src = os.path.join(ARTICLES_DIR, filename)
                dst = os.path.join(BACKUP_DIR, filename)
                shutil.copy2(src, dst)
        
        backup_count = len([f for f in os.listdir(BACKUP_DIR) if f.endswith('.html')])
        print(f"[BACKUP] Backed up {backup_count} HTML files")
    else:
        print(f"[BACKUP] Backup directory already exists: {BACKUP_DIR}")


def swap_ads():
    """Main function to swap ads in all specified files."""
    # Create backup first
    create_backup()
    
    count = 0
    for filename in FILES_TO_PROCESS:
        filepath = os.path.join(ARTICLES_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[WARN] File not found: {filename}")
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Replace old ads with new loan ad
        for pattern in OLD_AD_PATTERNS:
            content = pattern.sub(NEW_LOAN_AD + '</div></a></div></div>', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Updated: {filename}")
            count += 1
        else:
            print(f"[SKIP] No changes: {filename}")
    
    print(f"\n{'='*50}")
    print(f"Total files updated: {count}/{len(FILES_TO_PROCESS)}")
    print(f"Backup location: {BACKUP_DIR}")


if __name__ == "__main__":
    swap_ads()
