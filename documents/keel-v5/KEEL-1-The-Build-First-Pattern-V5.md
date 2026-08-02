# The Build-First Pattern

> "All good rules were written in blood."

Lay the KEEL before you sail. The foundation discipline for building with AI — for people who have judgment and intend to use it.

The tools now let one person build what used to take a team. That is the opportunity and the trap. The speed is intoxicating, and intoxicated builders skip foundations — then discover, weeks in, that the only copy of their work can vanish, that nothing was ever tested, or that a decision made in a chat window is gone. The people who will thrive in this era are not the fastest typists. They are the ones with the discipline to insist on solid ground before they build on it. That discipline is the asset a long career gives you. We call the foundation the KEEL — the first timber laid, the spine that keeps a boat upright when the weather turns. A project without one doesn't sail badly; it capsizes. This page is how to apply it.

Every principle below was paid for. The line beneath each is what it cost us — not a hypothetical. A scar.

## The one rule, if you remember nothing else

Lay the KEEL — version control, automated testing, automated deployment — BEFORE you plan a single feature, and before you start dreaming with an AI. Not after the prototype works. Not once it "gets serious." First. The foundation is a thirty-second setup on day one and a painful, error-prone retrofit on day ninety. You will never regret having it; you will always regret not having it.

## The ten principles (each learned the hard way)

### 1. One canonical copy. Exactly one.

Every project is a version-controlled repository with an offsite copy, from the first day. No "working folder plus backup folder," no pile of dated snapshots. The place you edit is the one true place.

**PAID FOR IN BLOOD:** Fourteen nearly-identical snapshot folders, no clear "real" copy — and we nearly edited a dead one. Worse: a whole working feature existed ONLY on the running server, committed nowhere. One power-cycle from gone.

### 2. Tests guard deployment. Always. From the first change.

A broken build must be physically unable to reach production. Automatic, not a habit you rely on remembering. It costs nothing on day one and is miserable to add later.

**PAID FOR IN BLOOD:** For weeks, anything we pushed could reach production whether it worked or not — nothing stood in the way. One bad afternoon from shipping a broken build to the system we depend on daily.

### 3. Deployment is automated, never by hand.

Merging your approved work is what ships it — not you running a command and hoping you did it right. Manual deploy is break-glass only. A step that depends on you remembering it will eventually be forgotten.

**PAID FOR IN BLOOD:** We deployed by hand for weeks while the automatic deploy we thought we had sat silently broken the entire time. Nobody knew, because nothing told us.

### 4. Secrets live in the platform, never in the code.

Passwords, keys, and tokens are held by the hosting platform and referenced by name. Never in a file, never committed, never pasted into a chat. A leaked secret is a bad day; a committed one is a bad year.

**PAID FOR IN BLOOD:** The automatic deploy was dead for one stupid reason — a single secret saved under the wrong NAME. One typo, and the whole safety system sat there looking perfectly fine. An afternoon gone.

### 5. Tests must be self-contained — no live services, no network.

The suite brings its own isolated world and pretends every outside service is present. That is what makes testing instant, free, and trustworthy. If a test needs the real world, it is a different kind of check that runs elsewhere.

**PAID FOR IN BLOOD:** Cost us nothing — and that's the point. Because our tests need no passwords and no internet, the whole safety system was trivial to build and runs in seconds, free, every time. The one we got right early. Do this one first.

### 6. Prove the safety net works — by tripping it, once.

On day one, deliberately break something and watch the system refuse to deploy it. Then fix it and watch it ship. A safety net you have never seen catch anything is a hope, not a guarantee.

**PAID FOR IN BLOOD:** We had "tests that guard deploys" on paper before we ever watched one actually block a bad build. Until you SEE it catch something, you don't have a net — you have a story about one.

### 7. Write the decision down before the work is done — you are building an asset, not a receipt.

A design agreed in conversation and never recorded does not exist. Capture what you chose and why, in the repository, before the work counts as finished. Include the alternative you rejected and what forced the call — a decision without its discarded options is a fact, not a decision, and facts don't teach anyone anything. And cite the evidence: the experiment, the measurement, the source. A decision backed by supposition is a guess with a document number.

That last part is what makes the log operable rather than merely readable. Give each decision its own numbered file — D-001, D-002 — piled up in the repository in the order you resolved them. Version control lets you go back to the last good commit. A numbered decision log lets you go back to the last good decision: find the exact entry where the reasoning stopped being sound, see what else was on the table before you knew what you know now, and restart from there. Later entries supersede earlier ones by name. Without the rejected options, "go back" means re-deriving the whole context from memory — and you can't, because you already know how it ended. It is a git history for the design.

Do this for a whole project and you end up holding something you never set out to build: the complete design story, in sequence, reasoning intact. That artifact has a market value the code doesn't. It is what you show when someone asks how you think.

**PAID FOR IN BLOOD:** a decision made in a chat and never written down came back a day later as a confident, WRONG note — and sent us chasing a bug already fixed. But the real lesson came from the project we logged properly end to end: at the close we could walk the entire design evolution, decision by decision, and explain every turn — and when one call turned out wrong, we could name the exact entry where it went wrong and recover from the option we'd written down and passed over. Nobody can write that retroactively. Once you know the answer, you narrate a straight line — and the straight line is a lie.

A judgment call, not a rule — what is your unit of work? Some projects are exploratory: the design is unknown at the start, and the work is resolving one open question at a time by experiment. There you move decision to decision, and each entry either supports or debunks an assumption. Some projects are constructive: the design is largely settled, and the work is building the next known thing against a technical design document. There the TDD is the unit. Most projects are both, in phases — and the two are not rivals. The surviving assumptions from your exploratory phase are exactly the premises your TDDs get built on; the debunked ones are what stop you specifying something on a foundation nobody tested. Know which phase you are in before you choose the shape of the work.

### 8. Every claim carries how you know it — and a summary is not knowing.

A written record fixes a claim in place; it does not make it true. Before a number or a status goes into the record, name the artefact it came from — the log line, the query output, the run link. If you cannot name it, you are recording a belief. And prefer the question whose answer could disqualify you: ask what is available, not just what is on; ask for the breakdown, not the total.

**PAID FOR IN BLOOD:** Three claims reversed in one afternoon — every one already written down, every one true as stated and wrong in what it implied. "All parameters on the GPU" was true, and missed that the model had already spilled past physical memory. "217 hardware errors" was true, and missed that only four were fatal. "The extension isn't enabled" was true, and missed that it wasn't installed at all — which killed two of our four options the moment we asked the better question. Each was caught only by returning to the raw record.

### 9. A failing check nobody is forced to obey is decoration.

The gate stops the deploy. Only branch protection stops the human. Require the check, require a pull request, and allow no bypass — not even for you, the owner. Without that, a red X is a suggestion.

**PAID FOR IN BLOOD:** Our first deliberately-broken pull request showed a red X and sat there perfectly mergeable. The gate had worked exactly as designed and blocked nothing, because nothing obliged anyone to care. We turned on protection and watched the same PR flip to BLOCKED. Two different mechanisms. You need both.

### 10. Build in the open. Go private when it goes real.

Your Builder logs in as you and reads a private repository fine. Your Planner cannot — it can only connect directly to a repository that is PUBLIC. So the repository is public while you build, connected to your Planner, and it goes private once the project is production-stable. The concrete tripwires, whichever comes first: the first real credential, the first real user data, or the first live deploy. The price of public is that nothing secret ever goes in a file — which is Principle 4, now structurally enforced instead of merely intended.

**PAID FOR IN BLOOD:** We spent weeks hand-carrying dated archives of our own code into the planning chat every morning, because we'd assumed private was simply the responsible default and never asked what it cost. It cost us our Planner's eyes. Going public deleted the ritual, the folder of near-identical archives, and an entire class of "the AI is working from a stale copy" bugs — in one setting change.

## The move that makes it stick with AI

The temptation to skip the Keel is strongest at exactly the instant you start planning with an AI — planning is the fun part, and the foundation feels like a detour between you and it. Willpower loses that fight, so do not rely on it. Move the enforcement earlier than the temptation.

Make starting correctly take thirty seconds — a template or script that lays the whole Keel in one step, so beginning the right way is easier than beginning the wrong way. And give the AI a standing instruction: before we design anything, confirm the foundation exists — and if it doesn't, stop and build it first. You turn the very thing that tempts you to skip the foundation into the thing that guards it.

## Why this is ours to teach

None of this is about being a programmer. It is about refusing to build on sand, insisting on ground truth before action, and writing down your reasoning so it outlives the moment — judgment, in other words. A long working life is where judgment comes from, and the tools have finally caught up to the people who have it. Lay the Keel first. Then go build the thing you have been waiting your whole career to build.
