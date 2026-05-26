"""
Sovereign AI Stack Ad Swap Script
==================================
Replaces PerformCB "Personal Loans" ads with Sovereign AI Stack CTA.
Removes ALL ad disclaimers (Partner Offer labels, PerformCB tracking, sponsored rels).
No disclaimers since this is Vinny's own free resource.

Usage:
    python scripts/swap-ads-v2.py           # Process ALL article HTML files
    python scripts/swap-ads-v2.py --dry-run # Preview changes without writing
    python scripts/swap-ads-v2.py --file <filename.html>  # Process single file

Author: PhantomByte
Last updated: 2026-05-15
"""

import os
import re
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Configuration
ARTICLES_DIR = Path("C:/Users/Doter/workspace/articles")
BACKUP_DIR = ARTICLES_DIR / f"backup-sovereign-ad-swap-{datetime.now().strftime('%Y-%m-%d')}"

# ============================================================
# NEW SOVEREIGN AI STACK AD CREATIVE
# ============================================================
# Uses the same visual style (dark gradient, green shadow) but
# NO PerformCB tracking, NO "Partner Offer" label, NO "sponsored" rels,
# NO disclaimers of any kind. This is Vinny's own free resource.

NEW_AD_TOP = '''            <!-- CTA Slot (Top) -->
            <div class="ad-slot ad-slot-article-top">
                <a href="https://sovereign-ai-stack.phantom-byte.com" target="_blank">
                    <div class="ad-creative" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 24px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 255, 136, 0.25); border: none;">
                        <p style="font-size: 0.7rem; color: #FF6B35; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">⚠️ Exit the Cloud</p>
                        <h4 style="margin: 0 0 12px 0; color: #ffffff; font-size: 1.3rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">Own Your Weights. Own Your Data.</h4>
                        <p style="margin: 0 0 16px 0; font-size: 0.95rem; line-height: 1.5; color: #e0e0e0; font-weight: 400;">The cloud AI era is a data-harvesting trap. Stop being the product and start being the owner. Build your local sovereign stack today.</p>
                        <div style="text-align: center;">
                            <span style="display: inline-block; padding: 11px 22px; background: linear-gradient(90deg, #00FF88 0%, #00cc6a 100%); color: #0a0a1a; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.95rem; box-shadow: 0 3px 10px rgba(0, 255, 136, 0.35);">Download The Blueprint</span>
                        </div>
                    </div>
                </a>
            </div>'''

NEW_AD_BOTTOM = '''            <!-- CTA Slot (Bottom) -->
            <div class="ad-slot ad-slot-article-bottom">
                <a href="https://sovereign-ai-stack.phantom-byte.com" target="_blank">
                    <div class="ad-creative" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 24px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 255, 136, 0.25); border: none;">
                        <p style="font-size: 0.7rem; color: #FF6B35; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">⚠️ Exit the Cloud</p>
                        <h4 style="margin: 0 0 12px 0; color: #ffffff; font-size: 1.3rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">Own Your Weights. Own Your Data.</h4>
                        <p style="margin: 0 0 16px 0; font-size: 0.95rem; line-height: 1.5; color: #e0e0e0; font-weight: 400;">The cloud AI era is a data-harvesting trap. Stop being the product and start being the owner. Build your local sovereign stack today.</p>
                        <div style="text-align: center;">
                            <span style="display: inline-block; padding: 11px 22px; background: linear-gradient(90deg, #00FF88 0%, #00cc6a 100%); color: #0a0a1a; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.95rem; box-shadow: 0 3px 10px rgba(0, 255, 136, 0.35);">Download The Blueprint</span>
                        </div>
                    </div>
                </a>
            </div>'''

NEW_AD_INDEX = '''            <!-- CTA Slot -->
            <section class="ad-slot ad-slot-horizontal">
                <a href="https://sovereign-ai-stack.phantom-byte.com" target="_blank">
                    <div class="ad-creative" style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 24px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 255, 136, 0.25); border: none; max-width: 728px; margin: 0 auto;">
                        <p style="font-size: 0.7rem; color: #FF6B35; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">⚠️ Exit the Cloud</p>
                        <h4 style="margin: 0 0 12px 0; color: #ffffff; font-size: 1.3rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">Own Your Weights. Own Your Data.</h4>
                        <p style="margin: 0 0 16px 0; font-size: 0.95rem; line-height: 1.5; color: #e0e0e0; font-weight: 400;">The cloud AI era is a data-harvesting trap. Stop being the product and start being the owner. Build your local sovereign stack today.</p>
                        <div style="text-align: center;">
                            <span style="display: inline-block; padding: 11px 22px; background: linear-gradient(90deg, #00FF88 0%, #00cc6a 100%); color: #0a0a1a; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.95rem; box-shadow: 0 3px 10px rgba(0, 255, 136, 0.35);">Download The Blueprint</span>
                        </div>
                    </div>
                </a>
            </section>'''

# ============================================================
# REGEX PATTERNS - Match old ad blocks to replace entirely
# ============================================================

# Article Top Ad Slot: matches from opening <div class="ad-slot ad-slot-article-top">
# through all PerformCB/Personal Loans content until closing </div> before next section
AD_TOP_PATTERN = re.compile(
    r'<!-- Ad Slot \(Top[^>]*\) -->\s*'
    r'<div class="ad-slot ad-slot-article-top">.*?'
    r'</div>\s*</a>\s*</div>\s*</div>',
    re.DOTALL
)

# Article Bottom Ad Slot
AD_BOTTOM_PATTERN = re.compile(
    r'<!-- Ad Slot \(Bottom[^>]*\) -->\s*'
    r'<div class="ad-slot ad-slot-article-bottom">.*?'
    r'</div>\s*</a>\s*</div>\s*</div>',
    re.DOTALL
)

# Also match cleaner bottom ad format (no extra closing tags)
AD_BOTTOM_CLEAN_PATTERN = re.compile(
    r'<!-- Ad Slot \(Bottom[^>]*\) -->\s*'
    r'<div class="ad-slot ad-slot-article-bottom">.*?'
    r'</div>\s*</div>\s*</a>\s*</div>\s*</div>',
    re.DOTALL
)

# Index/Horizontal Ad Slot
AD_INDEX_PATTERN = re.compile(
    r'<!-- Ad Slot \(Bottom[^>]*\) -->\s*'
    r'<section class="ad-slot ad-slot-horizontal">.*?'
    r'</section>',
    re.DOTALL
)

# Catch any remaining ad-performcb divs (shouldn't remain after above replacements)
PERFORMCB_CLEANUP = re.compile(
    r'<div class="ad-performcb"[^>]*>',
    re.DOTALL
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_backup(files_to_process):
    """Create a backup of all HTML files before making changes."""
    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        print(f"[BACKUP] Creating backup directory: {BACKUP_DIR}")
        
        count = 0
        for filepath in files_to_process:
            dst = BACKUP_DIR / filepath.name
            shutil.copy2(filepath, dst)
            count += 1
        
        print(f"[BACKUP] Backed up {count} HTML files")
    else:
        print(f"[BACKUP] Backup directory already exists: {BACKUP_DIR}")


def process_file(filepath, dry_run=False):
    """Process a single HTML file, replacing old ads with Sovereign AI Stack CTA."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    # Replace article top ad
    if AD_TOP_PATTERN.search(content):
        content = AD_TOP_PATTERN.sub(NEW_AD_TOP, content)
        changes.append("top ad")
    
    # Replace article bottom ad (try both patterns)
    if AD_BOTTOM_PATTERN.search(content):
        content = AD_BOTTOM_PATTERN.sub(NEW_AD_BOTTOM, content)
        changes.append("bottom ad")
    elif AD_BOTTOM_CLEAN_PATTERN.search(content):
        content = AD_BOTTOM_CLEAN_PATTERN.sub(NEW_AD_BOTTOM, content)
        changes.append("bottom ad (clean)")
    
    # Replace index/horizontal ad
    if AD_INDEX_PATTERN.search(content):
        content = AD_INDEX_PATTERN.sub(NEW_AD_INDEX, content)
        changes.append("horizontal/index ad")
    
    # Cleanup any remaining ad-performcb divs
    if PERFORMCB_CLEANUP.search(content):
        content = PERFORMCB_CLEANUP.sub('', content)
        changes.append("performcb cleanup")
    
    if content != original:
        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        return True, changes
    else:
        return False, changes


def process_index(dry_run=False):
    """Process index.html specifically."""
    index_path = ARTICLES_DIR / "index.html"
    if not index_path.exists():
        print("[WARN] index.html not found")
        return False
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    if AD_INDEX_PATTERN.search(content):
        content = AD_INDEX_PATTERN.sub(NEW_AD_INDEX, content)
        changes.append("index/horizontal ad")
    
    if PERFORMCB_CLEANUP.search(content):
        content = PERFORMCB_CLEANUP.sub('', content)
        changes.append("performcb cleanup")
    
    if content != original:
        if not dry_run:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return True, changes
    return False, changes


def collect_all_html_files():
    """Collect all HTML files to process (articles + index)."""
    files = []
    
    # All .html files in articles dir (excluding special pages)
    for f in ARTICLES_DIR.glob("*.html"):
        name = f.name
        # Skip privacy, terms, and other non-article pages
        if name in ("index.html", "privacy.html", "terms.html", "404.html"):
            continue
        files.append(f)
    
    return files


def verify_changes(filepath):
    """Quick verification that a file has been updated correctly."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "PerformCB removed": "ad-performcb" not in content,
        "Partner Offer removed": "Partner Offer" not in content,
        "nofollow sponsored removed": 'rel="nofollow sponsored"' not in content,
        "noklnk removed": "noklnk.com" not in content,
        "Sovereign link present": "sovereign-ai-stack.phantom-byte.com" in content,
        "Exit the Cloud present": "Exit the Cloud" in content,
        "Own Your Weights present": "Own Your Weights" in content,
    }
    
    all_pass = all(checks.values())
    return all_pass, checks


# ============================================================
# MAIN
# ============================================================

def main():
    dry_run = "--dry-run" in sys.argv
    single_file = None
    
    # Parse --file argument
    for i, arg in enumerate(sys.argv):
        if arg == "--file" and i + 1 < len(sys.argv):
            single_file = ARTICLES_DIR / sys.argv[i + 1]
            break
    
    mode = "DRY RUN" if dry_run else "LIVE"
    
    if single_file:
        # Process a single file
        print(f"[{mode}] Processing single file: {single_file.name}")
        print("=" * 60)
        
        if not single_file.exists():
            print(f"[ERROR] File not found: {single_file}")
            return
        
        if not dry_run:
            create_backup([single_file])
        
        changed, changes = process_file(single_file, dry_run=dry_run)
        
        if changed:
            print(f"[OK] Updated: {single_file.name}")
            print(f"     Changes: {', '.join(changes)}")
            
            if not dry_run:
                passed, checks = verify_changes(single_file)
                print(f"\n[VERIFY] All checks passed: {passed}")
                for check, result in checks.items():
                    status = "✅" if result else "❌"
                    print(f"     {status} {check}")
        else:
            print(f"[SKIP] No ad slots found in: {single_file.name}")
        
    else:
        # Process all files
        files = collect_all_html_files()
        print(f"[{mode}] Processing {len(files)} article HTML files + index.html")
        print("=" * 60)
        
        if not dry_run:
            create_backup(files + [ARTICLES_DIR / "index.html"])
        
        updated = 0
        skipped = 0
        
        # Process articles
        for filepath in sorted(files):
            changed, changes = process_file(filepath, dry_run=dry_run)
            if changed:
                print(f"[OK] {filepath.name} ({', '.join(changes)})")
                updated += 1
            else:
                skipped += 1
        
        # Process index
        idx_changed, idx_changes = process_index(dry_run=dry_run)
        if idx_changed:
            print(f"[OK] index.html ({', '.join(idx_changes)})")
            updated += 1
        
        print(f"\n{'=' * 60}")
        print(f"Articles updated: {updated}/{len(files)} (skipped: {skipped})")
        print(f"Index updated: {'Yes' if idx_changed else 'No'}")
        
        if not dry_run:
            print(f"Backup location: {BACKUP_DIR}")
            
            # Quick verify on a sample
            sample = files[0] if files else None
            if sample:
                passed, checks = verify_changes(sample)
                print(f"\n[VERIFY] Sample check ({sample.name}): {'ALL PASSED ✅' if passed else 'SOME FAILED ❌'}")
                for check, result in checks.items():
                    status = "✅" if result else "❌"
                    print(f"     {status} {check}")


if __name__ == "__main__":
    main()
