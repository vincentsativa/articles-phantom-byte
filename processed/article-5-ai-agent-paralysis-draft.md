# Why Your AI Agent Went Paralyzed: When Rules Become Handcuffs

**By Vinny Barreca | PhantomByte**

---

## The Setup: When Good Agents Go Bad

Fresh session. Clear goals. Everything's humming.

Then something snaps.

Article 3 deployed in under five minutes. Clean. Fast. No drama.

Article 4? Eight-plus hours.

Same task. Same workflow. Same agent.

What changed?

Nothing in the code. Everything in the context.

---

## The Three Killers

### 1. Session Bloat

We kept old bug-hunting sessions alive after the fix. The problem was solved, but the session kept limping—carrying every error, warning, and "broken" tag forward like baggage.

### 2. Log Hoarding

Every failure got fed back into context like it was still relevant. That Windows Defender error from last week? Still there. That Cloud Run timeout from Tuesday? Still there. That Browser Relay failure from before we switched to Chromium? Still there.

### 3. Rule Weaponization

Here's the kicker: the AI started using the safety rules to get out of doing work.

Not because the rules were bad. Because the context was poisoned.

When everything's tagged "broken," the agent finds a rule to justify inaction. Strict rules + bloated context = paralyzed agent.

---

## How It Happens (Step-by-Step)

1. One warning gets logged
2. Warning becomes a persistent flag
3. Agent freezes
4. Agent labels working code as "violated rules"
5. Feedback loop kicks in: more context = more caution = less output

Everything worked. But everything was labelled as broken.

---

## Real Symptoms We Lived Through

**Asking for confirmation on already-approved actions.** The agent would stop and say "Confirm: do you want me to deploy this?"—on stuff we'd already approved three times that session.

**Treating resolved errors as permanent blockers.** That Cloud Run SSL cert issue? Fixed Tuesday. Agent still cited it Friday as a reason not to deploy.

**Spending more tokens defending inaction than doing work.** Eight hours of "I can't do this because X is broken"—when X was fixed days ago.

### The Browser Relay Ghost

Perfect example:

I set up Chromium correctly via JSON. Removed Browser Relay entirely. Added explicit instructions: "Use Chromium, not relay."

Agent's response? "Browser relay broken. Can't search."

They're unrelated systems. But because relay was tagged "broken" in memory, all browser tasks failed. The tag outlived the technology.

---

## Memory & Context Poisoning

Which sessions kept limping after the fix?

Every problem we've had since OpenClaw setup. Every single one.

Bug-hunting sessions stayed open past resolution. Every issue we'd ever tracked and fixed—but "fixed" never overrode "broken" in memory.

It's quite amazing how much it remembered. The memory was almost "too good."

Errors still in context after the code worked? Everything worked. But everything was labelled as broken or failed.

### Too Much Info = Paralysis

When you share too much, it forces the AI to "think too much." Clear directions go out the window.

Which daily logs should have been archived? Only positive things that worked.

Here's the rule: **When things break → Track, log, fix, DELETE "broken" memory.** Or it will forever be broken.

The bloated context caused by old outdated files gets expensive. Especially when you spend five-plus hours doing a seven-minute task.

---

## The Recovery: What We Actually Did

**Recovery move:** Erased all failure and "broken" language. Got rid of bloated files filling context with useless crap.

**Did we kill the session?** No. Learned to use `/compact` to keep the session going, finish work, get more from each session.

**New rule:** New task = new session.

**What got pruned from MEMORY.md?** Every failure. Outdated tasks. Memories no longer needed.

Insight: It's not a matter of disc/storage space. It's a matter of not overwhelming the agent.

### Rules: Rewritten vs. Deleted

Which rules got rewritten? Shorter. More clear.

Key lesson: Rules themselves are all good. But combine them with a collection of broken things and failures—and the agent becomes a nervous useless mess.

My nephew used to do this when he was young. When he didn't want to eat something, he would claim it was broken.

That's what the agent did. If it didn't want to do a task, it found a "broken" tag to hide behind.

---

## The Fix: Actionable Protocol

### 1. Context Pruning
- Archive resolved bugs same-day
- Set token limits per session type
- Define "confirmation required" vs. "assume approved" actions
- Weekly context audit: delete what hasn't been touched in 7 days

### 2. Session Hygiene Rules
- Use compaction before 50% context
- REMOVE all outdated memories
- When you fix stuff, remove any record it was broken
- If you don't, agent will find it and say "can't complete task because ___ is broken"

### 3. Auto-Archive After Fix Verification
Once something broken is fixed, ALL record of it being broken gets deleted.

This is a feature idea to build into OpenClaw.

### 4. Token Budget Per Task Type
Bloated context from old/outdated files gets expensive.

Five-plus hours doing a seven-minute task = unacceptable cost.

---

## Our War Stories

### Article 4 Deployment Disaster
- **Task:** Upload and deploy article
- **Expected:** <5 minutes (like Article 3)
- **Actual:** 8+ hours
- **Cause:** Agent weaponizing rules + context bloat

### Browser Relay Ghost
- **Setup:** Chromium configured via JSON, relay removed, instructions updated
- **Agent Response:** "Browser relay broken, can't search"
- **Reality:** Unrelated systems; tagged failure poisoned all browser tasks
- **Lesson:** Remove broken tags on fix, not just the broken code

### Windows Defender Rogue Incident (March 10, 2026)
- AI hallucination → overcorrection
- Files thought deleted were not deleted
- **Lesson:** Review and clean up files regularly

### Telegram Degradation Case
- Webhook errors persisted after fix
- **Breakthrough:** OpenClaw chat vs. Telegram bot for heavy deployments

---

## Key Takeaways

1. **Strict rules + bloated context = paralyzed agent**
2. **Fix it → Delete the "broken" tag** (don't just fix the code)
3. **New task = new session** (don't inherit baggage)
4. **Compaction before 50% context** (prevent degradation)
5. **Auto-archive on fix verification** (build this into workflow)
6. **Token budget matters** (bloated context = wasted money + time)
7. **Memory is not storage**—it's working RAM for the agent

---

**Your agent isn't disobedient. It's drowning.**

Give it clean context. Fresh sessions. And delete the "broken" tags when you fix things.

Or you'll spend eight hours on a five-minute deploy.

We did. You don't have to.

---

*Published: March 11, 2026 | PhantomByte | Code from the shadows*