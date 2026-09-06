# KEEL · A Guild Discipline for Building with AI — The Build-First Pattern (v9)

> Markdown transcript of `KEEL-Build-First-Pattern-Deck-V9.pptx`, filed here per Keel Principle 7 (a record nobody can find is a record that doesn't exist). The original slide deck is kept alongside this file as the source artifact.

Lay the KEEL before you sail. The foundation you build every project on. For people who have judgment and intend to use it.

## "All good rules were written in blood."

Every rule in this deck was paid for. Not a hypothetical — a scar.

## The moment we're in

The tools now let one person build what used to take a team. That is the opportunity — and the trap. The speed is intoxicating, and intoxicated builders skip foundations.

- **The only copy vanishes** — Work that lived in one place — gone.
- **Nothing was ever tested** — Broken code ships; nobody knows.
- **A decision is lost** — Agreed in a chat, never written down.
- **A record nobody can find** — Written down — in a file no one would think to open.

The people who thrive here are not the fastest typists. They are the ones with the discipline to insist on solid ground before they build on it.

## The one rule, if you remember nothing else

Lay the KEEL — version control, automated testing, automated deployment — BEFORE you plan a single feature, and before you dream with an AI. Not after the prototype works. Not once it "gets serious." First.

Thirty seconds on day one. A painful, error-prone retrofit on day ninety. You will never regret having it.

The KEEL: the first timber laid — the spine that keeps a boat upright when the weather turns. A project without one doesn't sail badly; it capsizes.

## Before anything else: three players

Two of them are AIs. Confusing the two AIs is the #1 beginner mistake. Forgetting the third player is the one nobody warns you about.

### The Planner vs. the Builder

**THE PLANNER** — Your AI chat (Claude / Grok, in a browser Project). In a sealed room. Sees NOTHING of your code by default — only what you carry in, and a repository you have explicitly connected. That distance is why it's right for THINKING: architecture, plans, catching the mistake you're about to make.

**THE BUILDER** — Claude Code / Grok build tool, on your laptop. Works as YOU. Once logged in it sees everything you see — files, repo, the live system — and can edit, test, ship. In the trenches. Right for DOING: writing code, running tests, deploying.

Plan with the one that can't build. Build with the one that shouldn't plan. Then turn the page — because neither of them can do your job.

## Build in the open. Go private when it goes real.

Your Builder reads a private repository fine — it logs in as you. Your Planner cannot: it can only connect directly to a repository that is PUBLIC.

**WHILE YOU BUILD — PUBLIC.** Nothing to protect yet: no credentials, no user data, no live system. The Planner is connected and reads your real, current code — so no morning ritual of packaging archives by hand. The price: nothing secret ever goes in a file. That is Principle 4, structurally enforced instead of merely intended.

**WHEN IT GOES REAL — PRIVATE.** Flip at the first of these, whichever comes first: the first real credential, the first real user data, the first live deploy. You lose the Planner's direct view, and pre-flight reverts to handing it a snapshot by hand. That is the right cost to pay — at that point, and not before.

We assumed private was simply the responsible default and never asked what it cost. It cost us the Planner's eyes — for weeks.

## The core: the eleven principles

Each one learned the hard way. Each with the scar that earned it.

### 1 — One canonical copy. Exactly one.

A version-controlled repository with an offsite copy, from day one. No "backup folder," no pile of snapshots. The place you edit is the one true place.

*Paid for in blood:* Fourteen near-identical snapshot folders — we nearly edited a dead one. A whole feature existed ONLY on the running server, committed nowhere. One power-cycle from gone.

### 2 — Tests guard deployment. Always. From the first change.

A broken build must be physically unable to reach production. Automatic — not a habit you rely on remembering.

*Paid for in blood:* For weeks, anything we pushed could reach production whether it worked or not. One bad afternoon from shipping a broken build to the system we depend on daily.

### 3 — Deployment is automated, never by hand.

Merging your approved work is what ships it — not you running a command and hoping. Manual deploy is break-glass only.

*Paid for in blood:* We deployed by hand for weeks while the automatic deploy we THOUGHT we had sat silently broken the entire time. Nobody knew, because nothing told us.

### 4 — Secrets live in the platform, never in the code.

Passwords, keys, tokens live in the hosting platform, referenced by name. Never in a file, never committed, never pasted into a chat.

*Paid for in blood:* The deploy was dead for one stupid reason — a single secret saved under the wrong NAME. One typo, and the whole safety system sat there looking fine. An afternoon gone.

### 5 — Tests must be self-contained — no live services, no network.

The suite brings its own isolated world. That's what makes testing instant, free, and trustworthy. Do this one first.

*Paid for in blood:* Cost us nothing — and that's the point. Because our tests need no passwords and no internet, the whole safety system was trivial to build and runs in seconds. The one we got right early.

### 6 — Prove the safety net works — by tripping it, once.

Break something deliberately and watch the system refuse to deploy it. Then fix it and watch it ship. Same move for every guard you write after: break what the test watches, confirm it goes red.

*Paid for in blood:* We had "tests that guard deploys" on paper before we watched one block a bad build. Later, one layer down: a guard we trusted passed no matter what we broke — because the value we broke it with was the answer it expected.

### 7 — Write it down where someone would look for it.

A design agreed in conversation and never recorded does not exist. But recording it is only half the job — a record nobody can find is a record that doesn't exist either. Discoverability is a property of the filename.

*Paid for in blood:* We wrote our decisions down faithfully — into docs/README.md, because that's the file that was already there. It worked, for us, because we invented the convention and remembered it. Nobody arriving at that repository would ever have found them.

A README is a greeting, not a container. So the project carries five named documents — and each one's name is the whole explanation of what is inside it.

#### The five documents

| File | Answers | Holds |
|---|---|---|
| `architecture.md` | "What am I looking at?" | The pieces, the boundaries, how data moves, and what is deliberately absent. |
| `decisions.md` | "Why is it like this?" | D-001, D-002 … what you chose, what forced it, what you rejected, the evidence. |
| `findings.md` | "How do we know?" | What was measured, when, how many observations, and where the raw record is. |
| `testplan.md` | "What would catch it if it broke?" | What is covered, what deliberately is not and why, and how each guard was proven able to fail. |
| `assumptions.md` | "What are we taking for granted?" | A-001, A-002 … what you are relying on without having decided to. Two bars: state the falsifying test, or it does not go in. |

The emptiness is the point as much as the content: an empty `findings.md` is legible. A missing findings section inside a README is invisible.

### 8 — Every claim carries how you know it — and a summary is not knowing.

Before a number goes in the record, name the artefact it came from: the log line, the query, the run link. Carry the sample size with it. Prefer the question whose answer could disqualify you.

*Paid for in blood:* Three claims reversed in one afternoon — every one already written down, every one true as stated and wrong in what it implied. Each was caught only by returning to the raw record.

### 9 — A failing check nobody is forced to obey is decoration.

The gate stops the deploy. Only branch protection stops the human. Require the check, require a pull request, allow no bypass — not even for you, the owner.

*Paid for in blood:* Our first deliberately-broken pull request showed a red X and sat there perfectly mergeable. The gate had worked exactly as designed and blocked nothing, because nothing obliged anyone to care.

### 10 — Build in the open. Go private when it goes real.

Public while you build, connected to your Planner. Private once the project is production-stable. The tripwires, whichever comes first: the first real credential, the first real user data, the first live deploy.

*Paid for in blood:* We spent weeks hand-carrying dated archives of our own code into the planning chat every morning, because we'd assumed private was the responsible default. Going public deleted the ritual, the folder of near-identical archives, and an entire class of "the AI is working from a stale copy" bugs — in one setting change.

The price of public is that nothing secret ever goes in a file — which is Principle 4, now structurally enforced instead of merely intended. (Corollary, filed alongside this principle in the deck: every absence is a category with a cause; reconcile both directions; two paths to one number get compared once, on purpose.)

## The one demo that matters: prove the gate

Principles 6 and 9, in five moves. This is the moment the whole discipline becomes real — do it once, on day one.

1. **Break it on purpose.** Write a test that FAILS. Push it on a branch.
2. **Watch it get blocked.** The system REFUSES to deploy. (If it ships anyway — your gate is fake.)
3. **Try to override it.** Scroll to Merge. It reads BLOCKED — for you, the owner.
4. **Fix it.** Correct the test so it passes. Merge it.
5. **Watch it ship.** This time it deploys — through the front door.

The gate stops the machine. Branch protection stops the human. You need both — and a net you've never seen fire is a hope, not a guarantee.

## The move that makes it stick

The temptation to skip the Keel is strongest at the exact instant you start planning with an AI — planning is the fun part. Willpower loses that fight. Move the enforcement earlier than the temptation.

- **Make starting right take 30 seconds.** A template or script that lays the whole Keel in one step — including the five empty documents with their headings already in place. The right way becomes the easy way.
- **Give the AI a standing order.** "Before we design anything, confirm the foundation exists — and if it doesn't, stop and build it first."

You turn the thing that tempts you to skip the Keel into the thing that guards it.

## The daily rituals — and they are YOUR job

The hardest part of a long project isn't any single day — it's picking the work back up without losing the thread. Nothing enforces these. No gate, no test, no red X. Neither AI can run them: neither has a clock, and neither knows the day ended.

Your continuity does not live in the conversation. It lives in the repository.

**POST-FLIGHT — end of session.** Commit the baton: have your AI write a session close-out (what got done, what's open, what's next). Then ask the question that keeps the five documents alive: "which of the five changed today?" Commit all of it. Uncommitted work is invisible to the Planner.

**PRE-FLIGHT — start of session.** Start fresh, upload nothing: start a BRAND-NEW chat, not yesterday's. The Planner is connected to the repository and already reads your real, current code. Then ask for a REPORTED grounding block, not a summary: highest entry number in each log, quoted from the header; open items read as output; live repo or snapshot, and what each can prove.

One session ran a week instead of closing daily. Nine documents dated the 6th and 7th landed on the 16th — including the rule deciding what the whole project is about. Nothing was lost. Either that was luck, or something is sitting there undetected, and from the inside those look alike.

## Why this is ours to teach

None of this is about being a programmer. It is about refusing to build on sand, insisting on ground truth before action, and writing down your reasoning so it outlives the moment. Judgment, in other words.

A long working life is where judgment comes from. The tools have finally caught up to the people who have it.

## The reversal

Doing it right — the full discipline — used to be a luxury. Writing the tests first. Documenting the decision. Setting up the gate on day one. It all cost senior-engineer hours a deadline wouldn't spend — so it got skipped. The skip was almost rational. Not anymore.

The AI scaffolds the tests in a minute, writes them from your design, drafts the close-out for free. The cost of the discipline just collapsed toward zero — while its value stayed exactly as high. Most people are using AI to skip the discipline faster. You can finally afford to keep it.

## Why this works where corporate process dies

**Process done to you** — ceremony imposed from above. In a big company, "process" becomes sign-off gates, mandatory fields, rituals nobody believes in. So people comply — or quietly route around it.

**Process you run for yourself** — every principle has a scar under it. You follow the one-copy rule because you've lost a feature to a vanished folder. You lay the gate because you've shipped a break. Not compliance — self-interest, made legible. It gets followed because each step visibly saves you from a pain you have actually felt.

## The honest part

This pattern is proven on ONE real system. A live, deployed, multi-service application — real bugs fixed, new subsystems shipped, all run through the gate. That is genuine evidence, not theory. But it is one project, with one person as the whole team.

It has since destroyed a production database and recovered it from a backup nobody had verified existed; published a number that could not be reproduced under any of five candidate rules; and cited a decision by a number that had been reassigned to a different decision. Every one of those is now a scar in this deck.

Battle-tested on one system. Amended by every failure it produced. Taught as exactly that.

## What that means — for you

Because the economics reversed, a person of sixty — with the judgment a long working life builds — is now as fit, or more fit, than any peer to carry an idea all the way to a working application. One that is stable. One that lasts.

The tools stopped rewarding the fastest hands. They started rewarding the soundest judgment. That was never the young engineer's edge. It is yours.

**Lay the Keel first. Then go build the thing you have been waiting your whole career to build.**

## And the third player is you

**What only you can do — neither AI can do any of it:** Rule. Ritualise. Destroy. Rulings on judgement calls, credentials, destructive operations, the two daily rituals, the decision to stop. Neither AI has a clock, so neither knows the day ended. Continuity lives in the gap between sessions — the one place both of them cannot reach.

**How each of you fails — three different failure modes:** Doing, reasoning, omission. The Builder fails by DOING — its mistakes are executed before anyone reads them. The Planner fails by REASONING — from a stale copy, a title it never opened; its mistakes arrive as fluent summaries. You fail by OMISSION — not doing something, and nothing goes red. There is no gate for it, no test, no red X. They carry the work. You carry the seams. When you are short of time, the seams are what you drop — because dropping them costs nothing today.

## When it outgrows your eyes (Part C)

Not day one. Come back here the first time an output grows past what you actually read row by row.

### Five moves for when nobody can check by eye (Principle 11, made operational)

Each one exists because a defect survived the transition looking exactly like a correct result.

1. **Absence has a cause.** Never a zero, never a blank. Never-fetched and came-back-empty must carry different values.
2. **Reconcile both ways.** Count the misses in BOTH directions. A one-directional check cannot see orphans.
3. **Two paths, compared.** Any quantity written down twice gets compared once, on purpose — the numbers, not summaries of them.
4. **Accept by reproduction.** A version string is a claim. Reproduce a known-good subset exactly — that is the acceptance test.
5. **Say what you lose.** Before you destroy anything: a COMPLETED backup exists; its age as exposure; what it does not cover. And never assert absence from a stale copy — a snapshot can prove a thing existed at a revision; it can never prove a thing does not exist.
