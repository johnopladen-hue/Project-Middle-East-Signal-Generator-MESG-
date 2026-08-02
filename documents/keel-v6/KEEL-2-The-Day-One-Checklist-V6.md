# KEEL — The Day-One Checklist (V6)

> "All good rules were written in blood."

> **What's new in v6:** two new steps inserted into Part B — **Step 9 (Findings log)** and **Step 10 (Test plan)** — sitting right after the decision log (Step 8), before secrets/tests/gate. Everything from the old Step 9 onward shifts up by two (old Step 9 → new Step 11, … old Step 15 → new Step 17). If you're cross-referencing a v5 session note that says "Steps 10–15," that maps to v6 Steps 12–17. Nothing else changed.

How to lay the Keel on a new project — the field manual for [The Build-First Pattern](../keel-v5/KEEL-1-The-Build-First-Pattern-V5.md) ([v6](./KEEL-1-The-Build-First-Pattern-V6.md)).

This is how you lay the Keel. The companion page, The Build-First Pattern, is the why. The Keel is your foundation — version control, tests, and automated deploy — laid before you build anything on top. Do these in order, push the buttons, check each proof before moving on.

## How to run this

- Do the steps in order, top to bottom. Don't jump ahead. Don't skip.
- Every step ends with **PROOF** — how you know it worked. If the proof doesn't happen, STOP on that step and fix it before going on. A skipped foundation step is invisible until it hurts, and by then it's expensive.
- Wherever you see `‹Project Name›`, use the exact same name, same spelling, every single time.
- You don't have to understand every word. Your AI Builder can run any command — paste the step, say "do this," check the proof.

## First, understand this — or nothing else makes sense

You will use **TWO different AIs**, and they see your work through completely different windows. Confusing them is the #1 beginner mistake.

- **The Planner** (your AI chat — Claude or Grok in a browser Project). In a sealed room. Sees nothing of your code by default — not your files, not your repository, not the live system. The only things it sees are what you carry in and hand it, and a repository you have explicitly connected. That distance is exactly why it's the right tool for thinking: architecture, plans, catching the mistake you're about to make.
- **The Builder** (Claude Code or Grok's build tool on your laptop). Works as you. Once logged in it sees everything you see — files, repository, live system — and can edit, test, and ship. In the trenches. The right tool for doing: writing code, running tests, deploying.

The whole discipline in one line: you PLAN with the Planner (distance, can't build), then hand the plan to the Builder (can build, shouldn't plan). Thinking happens in the sealed room where nobody types too soon. Building happens in the trenches. Neither can do the other's job — that's the point.

**Burn this in — the visibility rule.** Your BUILDER reads a private repository fine; it logs in as you. Your PLANNER cannot. The Planner can only connect directly to a repository that is **PUBLIC**. So you build in the open — public repository, connected to your Project — and you go private once the project is production-stable. Public while you build. Private when it goes real. The tripwires, whichever comes first: the first real credential, the first real user data, or the first live deploy. The price of public is that nothing secret ever goes in a file, from the very first commit.

## PART A — Set up the workshop

### Step 1 — Start the Project and name it

- [ ] Go to your AI chat website (Anthropic's Claude, or Grok).
- [ ] Create a new Project (not just a chat — a Project; it's a button/menu, usually on the left).
- [ ] Name it. This name is now THE name. Write it on paper. Every `‹Project Name›` below means this.

**PROOF:** your named Project appears in the list, and you can click into it.

### Step 2 — Create the online home (the repository)

- [ ] Go to github.com and sign in (free account if needed).
- [ ] Click the green **New** button to make a new repository.
- [ ] Repository name: type your `‹Project Name›` — exact same name, same spelling as Step 1.
- [ ] Set it to **PUBLIC**. You have to choose this — Private is the default. This is deliberate: your Planner can only connect to a public repository, and that connection is what makes every day after this one cheap.
- [ ] Check "Add a README file." Click Create repository.

**PROOF:** you're looking at a GitHub page showing your `‹Project Name›` at the top, the word Public beside it, and a README file.

Public feels wrong. Read this once. Public does not mean careless — it means the discipline is now enforced by the world instead of by your memory. There is nothing to protect yet: no credentials, no user data, no live system. You go private the moment any of those three appears. And the alternative is not "safer" — it is a Planner that cannot see your code, which you then compensate for by hand, every single morning, forever.

### Step 3 — Connect the repository to your Project

- [ ] In your chat Project, find the option to add a GitHub repository (it may sit under "project knowledge," "sources," or "connect").
- [ ] Connect the `‹Project Name›` repository you just made.

**PROOF:** ask the Planner "what files do you see in my repository?" and it lists your README back to you. It is now looking at your real code, not your description of it.

**PAID FOR IN BLOOD:** we spent weeks packaging our own code into a dated archive and uploading it by hand every morning — because we assumed private was the responsible default and never asked what it cost. It cost us the Planner's eyes, plus a folder of near-identical archives and a steady drip of "the AI is working from a stale copy" bugs. One setting deleted all of it.

### Step 4 — Build your local workshop (where the code lives on your computer)

So far everything is online. Now you make the real folder on your own machine where the work happens — and pull the repository down into it. One rule, both platforms: keep your projects OUT of any cloud-synced folder (OneDrive on Windows, iCloud's Desktop/Documents on Mac). Cloud sync fights git and hides files.

- [ ] Open VS Code.
- [ ] Open its built-in terminal: top menu Terminal → New Terminal.
- [ ] Make your Projects folder — type the line for your computer and press Enter:
  - Windows: `mkdir C:\Projects`
  - Mac: `mkdir -p ~/Projects`

  Why these spots: `C:\Projects` sits off the drive root, clear of OneDrive and short-path problems. `~/Projects` sits in your Mac Home folder, clear of iCloud sync, short and visible. Same idea both places — out of the cloud, easy to find. If it says the folder already exists, good; move on.
- [ ] Open VS Code's Command Palette — Windows: Ctrl+Shift+P / Mac: Cmd+Shift+P — type `Git: Clone`, pick it.
- [ ] Paste your repository's web address. (On GitHub, the green Code button gives you the address to copy.)
- [ ] When it asks WHERE to put it, choose your Projects folder. VS Code creates a `‹Project Name›` folder inside it and pulls the README down automatically. (Don't pre-make the `‹Project Name›` folder yourself — the clone makes it, or you'll end up with a folder inside a folder.)
- [ ] When it asks "Open the cloned repository?", click Open.

**PROOF:** VS Code shows your `‹Project Name›` folder with README.md in it, sitting inside Projects on your computer and connected to your online repository. THIS IS YOUR WORKSHOP.

### Step 5 — Open your Builder

- [ ] On your laptop, open your AI building tool (Claude Code, or Grok's build tool — match it to the chat from Step 1).
- [ ] Connect it to your GitHub account and the `‹Project Name›` repository when it asks (it walks you through login).

**PROOF:** the Builder is open, logged in, and can see your `‹Project Name›` repository.

### Step 6 — Choose your planning brain

- [ ] Pick which AI model does the thinking. Choose a strong all-rounder — mid-to-upper tier.

Future-proof translation (model names change, this rule doesn't): every provider offers a ladder — a fast-cheap tier at the bottom, a heavyweight specialist at the top, a strong all-rounder in the middle. Pick the all-rounder. These names are training wheels — use them until the choice is second nature, then you won't need them. Unsure? Ask the tool: "Which of your models is the best balance of capable and affordable for planning a software project?"

**PROOF:** the tool shows your chosen model as active.

### Step 7 — Fill in the Project instructions (and understand where they live)

- [ ] In your chat Project, find the instructions / description area (may be "custom instructions," "project knowledge," or "set up").
- [ ] Write a few plain sentences on what this project is. (Ask the AI to help word it.)
- [ ] Burn this in: everything typed here — instructions AND any documents the AI creates in the Project — lives ONLY in the cloud, on the AI company's website. NOT on your laptop, NOT in your repository. Cloud Project = planning space. Repository = permanent record. Anything that must survive gets saved into the repository (Part B sets up where).

**PROOF:** your Project has a description, and you understand it's cloud-only until saved into the repo.

## PART B — Lay the Keel (before you build a single feature)

### Step 8 — A safe place for decisions (build the log that becomes your design story)

- [ ] In your repository, create a folder called `docs/`, and inside it a folder called `docs/decisions/`.
- [ ] Create `docs/README.md` with the governing rules, plainly: (1) "Every design decision gets written down in `docs/decisions/` BEFORE the work it describes is finished." (2) "Every claim records the artefact it came from." (Rule 2 is Step 12 — write it now, practise it there.)
- [ ] One decision, one file, numbered in the order you resolve them: D-001, D-002, D-003. They pile up. That numbering is not decoration — it is what lets you say "we were sound up to D-023" and navigate straight to it.
- [ ] Each entry carries five things. Have your Builder make you a template with these fields:
  - The **decision** — what you chose, in one sentence.
  - The **context** — what question forced it, and what you knew at the time.
  - The **options rejected** — the real alternatives, not strawmen. This is the field that makes the log recoverable; without it, going back means re-deriving everything from memory, which you cannot do once you know the ending.
  - The **evidence** — the experiment, measurement, or source that supports it. A decision backed by supposition is a guess with a document number.
  - **Supersedes** — the earlier D-number this overturns, if any. Leave it blank until you need it; the day you need it, it is the whole point.

**PROOF:** pick a decision you made last week and open its file. You can name what you rejected, why, and what evidence backed the call. If you can only name what you chose, you recorded an outcome, not a decision — and you cannot recover from it later.

**PAID FOR IN BLOOD:** a decision made in a chat and never written down came back a day later as a confident, WRONG note — and sent us chasing a bug already fixed. The project we logged properly end to end gave us the opposite: at the close we could walk the whole design evolution in order, and when one call proved wrong we could name the exact entry and restart from the option we had written down and passed over. You cannot write that afterwards. Once you know the answer you narrate a straight line, and the straight line is a lie.

Some projects are exploratory — plan for it. If the design is genuinely unknown at the start, the work is not "build the next thing," it is resolve the next assumption: form it, test it, and record it as supported or debunked. Each of those is a D-entry. Run decision to decision, backed by real research rather than supposition. Then — and this is the part people miss — the assumptions that survived are the premises your technical design documents get built on. The debunked ones are what stop you writing a beautiful specification on a foundation nobody ever tested. Exploratory and constructive work are phases, not rival methods. Know which one you are in.

### Step 9 — A safe place for findings *(new in v6)*

- [ ] Create `docs/findings.md` (or your project's equivalent docs folder) — one running log, dated entries, newest last.
- [ ] Each entry carries four things: **date**, **context** (what you were doing), **finding** (what you learned), **implication** (what it changes going forward).
- [ ] This is not the decision log and not a bug tracker. It's for the dead end, the surprising constraint, the technique that worked better or worse than expected, the claim that turned out to be true-but-misleading. Anything that isn't obvious from reading the code, and that you'd want a teammate — or yourself in six months — to already know.

**PROOF:** pick something surprising you learned this week. It's already a dated entry in `findings.md`, not just a thing you remember for now.

**PAID FOR IN BLOOD:** without a place for this, findings either get bolted awkwardly onto the decision log (where they don't belong — they're not decisions) or evaporate the moment the person who noticed them moves on to the next task. The exact failure Principle 8 warns about — a plausible claim that turns out to hide the thing that mattered — is only catchable in hindsight if someone wrote down that it happened.

### Step 10 — A safe place for the test plan *(new in v6)*

- [ ] Create `docs/test_plan.md` — one table, not prose.
- [ ] Columns: Test ID, Component/Feature, Test Type, Description, Expected Result, Status, Date, Notes.
- [ ] Add a row *when you write the test*, not after the fact. An empty table is an honest starting point; a table you "backfill later" never gets backfilled.

**PROOF:** open `test_plan.md` and point at the row for the last test you wrote. If there isn't one, the table is already behind reality — fix that before writing the next test.

**PAID FOR IN BLOOD:** "the suite is green" and "the thing that matters is tested" are different claims, and Principle 2 only guarantees the first one. A visible, up-to-date table is what lets anyone — including the AI — answer "is X actually covered?" without reading every test file.

### Step 11 — Lock secrets out of the code (non-negotiable in a public repo)

- [ ] Create a file named `.gitignore` BEFORE your first real commit. Make sure it lists `.env` and any file holding secrets. (Ask your Builder exactly what to put in it.)
- [ ] Put every password, key, and token in your hosting platform's secrets area — never in a file inside the project. In documents, refer to a secret by NAME only, never by value.
- [ ] Add an automatic secret-scanner to your gate (Step 14) so a commit carrying a key is refused the same way a failing test is refused. Ask your Builder to wire this in — it is a few lines.

**PROOF:** search your whole project for a real password or key. You find NONE. They all live in the platform, by name only.

**PAID FOR IN BLOOD:** one secret saved under the wrong NAME silently broke our entire deployment for an afternoon. Everything looked fine. It wasn't. Never in the code — and check the name twice.

### Step 12 — Write down HOW you know, not just what you concluded

- [ ] In `docs/README.md`, keep the second rule visible: every claim records the artefact it came from — the log line, the query, the run link.
- [ ] Practise it once, right now, on something you already believe about your project. Go find the actual record. (About half the time it says something slightly different from what you remembered.)
- [ ] When your AI reports a result, ask "what would I have to look at to see that myself?" If it can't point at something, the result is a guess wearing a number.
- [ ] Prefer the question that could disqualify you. Ask what is available, not just what is on. Ask for the breakdown, not the total.

**PROOF:** pick any claim in your notes at random. You can reach the raw evidence behind it in under a minute. If you can't, it was never a finding.

**PAID FOR IN BLOOD:** we reversed three confidently-written claims in a single afternoon. Not one was a lie — each was a true summary that hid the thing that mattered. The counts were right and the severity was missing. The parameters were on the GPU and the memory had already overflowed. The extension wasn't enabled — and also wasn't installed at all, which changed every option we had. A summary is where the disqualifying detail goes to die.

### Step 13 — Self-contained tests (do this one early — it makes all the rest easy)

- [ ] Set up the test framework so tests run in their own isolated world — no internet, no real services, no passwords required.
- [ ] Write one tiny throwaway test that checks something obvious (like 1 + 1 == 2), just so the machinery exists and runs. Give it a row in `test_plan.md` (Step 10).

**PROOF:** you run the tests and they pass in seconds WITH your internet turned OFF.

**PAID FOR IN BLOOD:** the one we got RIGHT early: because our tests need nothing from the outside world, the whole safety system was trivial to build and runs free, in seconds, every time. Do this one first and everything downstream is easier.

### Step 14 — Build the gate (tests must pass before anything ships)

- [ ] Set up automatic deployment with a hard rule: work ships only if tests pass first, and shipping happens by merging approved work — not by running a command.
- [ ] Create the deploy credential scoped to deploy only (not full access). Save it in the platform under the EXACT name the config expects. (Have your Builder confirm the name matches — a mismatched name is the #1 silent failure.)

**PROOF:** comes in Step 15. Do not trust the gate yet. Prove it.

**PAID FOR IN BLOOD:** for weeks, anything we pushed could reach production whether it worked or not — nothing stood in the way. One bad afternoon from shipping garbage to the system we depend on daily.

### Step 15 — PROVE the gate works (never skip this — it is the whole point)

- [ ] Deliberately write a test that FAILS. Push it on a branch. Log it as a row in `test_plan.md` too — a deliberately-failing proof test is still a test.
- [ ] Watch the system REFUSE to deploy it. (If it ships anyway, your gate is fake — stop, fix Step 14.)
- [ ] Now fix the test so it passes. Merge it.
- [ ] Watch it deploy correctly this time.

**PROOF:** you have watched, with your own eyes, the gate BLOCK a bad build and ALLOW a good one.

**PAID FOR IN BLOOD:** we had "tests that guard deploys" on paper before we ever watched one actually stop a bad build. Until you SEE it catch something, you don't have a safety net — you have a story about one.

### Step 16 — Make the check BINDING (the gate stops the deploy; only this stops the human)

- [ ] Turn on branch protection for your main line: require a pull request, require the test check to pass, and allow no bypass — including for you, the owner.
- [ ] Try to push directly to main. Watch it get REFUSED.
- [ ] Look at a pull request with a failing check. It must read BLOCKED, not merely "has a red X."

**PROOF:** you tried to push straight to main and the system said no — to you, the owner, with full permissions.

**PAID FOR IN BLOOD:** we proved our gate by breaking a test on purpose, and it worked — the deploy was skipped. Then we looked closer: the pull request still showed as perfectly mergeable. A red X and a green Merge button, side by side. The gate had stopped the machine and nothing had stopped the person. One tired evening from clicking straight through our own safety system. Turning on protection flipped that same PR to BLOCKED. Two different mechanisms — you need both.

### Step 17 — Stop deploying by hand, forever

- [ ] Kill any habit or note that says "run the deploy command after changes."
- [ ] From now on: merging approved work is the only way things ship. Manual deploy is break-glass only (real emergencies).

**PROOF:** you make a real change, merge it, and it reaches production WITHOUT you running any deploy command.

**PAID FOR IN BLOOD:** we typed the deploy command by hand for WEEKS while the automatic one sat silently broken. Nobody knew, because nothing told us. Let the machine do it, every time.

## The Keel is laid

- [ ] Every PROOF above happened. If any didn't, go back to that step — never sail on a cracked keel.
- [ ] Only now do you start planning your first real feature.

The keel is laid; now you sail. Everything you build from here stands on solid ground. Now go build the thing you've been waiting your whole career to build.

## WHEN TO GO PRIVATE

You built in the open so your Planner could see your work. That trade stops paying the moment the project becomes real. Flip the repository to Private when the first of these happens — whichever comes first:

- [ ] The first real credential — any key, token, or password that touches a real account, even in an environment file you have (correctly) gitignored.
- [ ] The first real user data — anyone's information but your own test rows.
- [ ] The first live deploy — the moment something you'd be upset to lose is running for real.

What changes when you flip it: your Planner loses direct sight of the repository. The Opening Ritual below reverts to handing it your close-out and a code snapshot by hand. That is the cost, and it is the right cost to pay at that point — it is also exactly the friction you avoided for the whole build phase by starting public.

**PROOF:** the repo reads Private, and your next planning session starts by handing the Planner the close-out yourself.

## THE DAILY RITUALS — how to work a project over days and weeks

The most worthwhile projects take days or weeks. The hardest part isn't any single day — it's picking the work back up, day after day, without losing the thread. These two rituals are how. Run them like pre-flight and post-flight checks.

### Why you do NOT keep one chat open for days

The tempting mistake: you did good work in a chat, the AI "knows" your project now, and starting fresh tomorrow feels like throwing that away. So you keep the same session alive for days, afraid to close it.

That fear is backwards. Every AI has limited memory for a single conversation. A session running for days doesn't preserve context — it quietly sheds the oldest parts first, forgetting your foundational decisions while keeping this morning's trivia. It gets slower and dumber as it bloats. And your entire project history is trapped in one chat log you're afraid to close — the least durable place it could possibly live.

The truth that sets you free: your continuity does not live in the conversation. It lives in the repository. The chat is a disposable scratchpad. The repo — code, docs, close-out notes — is permanent. Because the durable state is in the repo, you can close every chat with zero fear and start fresh every day.

### The Closing Ritual — end of every work session (post-flight)

- [ ] Ask your AI to write a session close-out: what got done today, what's still open, what's next.
- [ ] Save (commit) it into your repository's `docs/` area.

**PROOF:** the close-out is in the repo. This is the baton you hand to tomorrow's fresh start.

This ritual is now load-bearing. Because the Planner reads the repository directly, anything you have NOT committed is invisible to it. Uncommitted work might as well not exist. Commit the close-out, or tomorrow starts blind.

### The Opening Ritual — start of every work session (pre-flight)

- [ ] Start a brand-new chat. Do NOT reopen yesterday's. (Your context is safe in the repo; a fresh chat is faster and sharper.)
- [ ] Upload nothing. Your Project is connected to the repository — the Planner is already looking at your real, current code.
- [ ] Tell the Planner: "Read the latest session close-out and [the design doc we're working on]. Tell me where we are and what's next."

**PROOF:** the AI summarizes your current state accurately WITHOUT you explaining it, and without you handing it a single file. You're grounded in under a minute. Now plan the day.

What changed, and why: an earlier version of this ritual had you run a command every morning to package your code into a dated archive and upload it by hand. That was the workaround for a Planner that couldn't see your repository. Connect a public repository once, in Step 3, and the workaround disappears — along with the folder of near-identical archives it left behind. Once you go private, this step reverts to handing the Planner your close-out and a snapshot by hand:

```
git archive --format=tar.gz -o ‹Project Name›-$(date +%Y%m%d).tar.gz HEAD
```

Keep this manual. Lay the Keel once per project (Parts A and B). Run the Daily Rituals every session, forever. It never costs more than the time it saves.
