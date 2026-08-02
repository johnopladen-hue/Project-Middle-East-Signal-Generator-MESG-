# KEEL — Quick Card

Lay the Keel before you build. "All good rules were written in blood." · Top to bottom. ✓ = proof — if it doesn't happen, STOP and fix it.

**TWO AIs, two windows.** PLANNER (browser chat) = sealed room, sees only what you hand it — plus a PUBLIC repo you connect → thinking. BUILDER (laptop tool) = works as you, sees everything, private or not → doing. Plan with one, build with the other. Build public so the Planner can see; go private when it goes real.

## PART A — Workshop

**1. Project + name**
- [ ] Create a Project in your AI chat. Name it. That name is THE name, everywhere.
- **PROOF:** named Project appears, you can click in.

**2. Repository**
- [ ] github.com → New → same name → set PUBLIC (you must choose it) → add README → Create.
- **PROOF:** GitHub page shows your name, the word Public, + README.

**3. Connect repo to Project**
- [ ] In the chat Project, add the GitHub repo as a source. This is why it's public.
- **PROOF:** ask "what files do you see?" → it lists your README back.

**4. Local workshop**
- [ ] VS Code terminal: make Projects folder (Win: `mkdir C:\Projects` / Mac: `mkdir -p ~/Projects`). Keep OUT of OneDrive/iCloud.
- [ ] Command Palette → Git: Clone → paste repo address → pick Projects → Open. Clone makes the project folder.
- **PROOF:** VS Code shows your project folder + README. THIS IS YOUR WORKSHOP.

**5. Builder**
- [ ] Open your laptop build tool; connect it to the repo (logs in as you).
- **PROOF:** Builder open, logged in, sees the repo.

**6. Planning brain**
- [ ] Pick the mid/upper all-rounder model — not cheapest, not top specialist.
- **PROOF:** chosen model shows as active.

**7. Project instructions**
- [ ] Fill the Project description. Know: this + AI docs here live CLOUD-ONLY. Cloud = planning; repo = permanent.
- **PROOF:** description filled; you know it's cloud-only until saved to repo.

## PART B — Lay the Keel

**8. Docs home + decision log**
- [ ] Make `docs/` + `README.md`: "decisions get written here before work is done."
- [ ] Make `docs/decisions/`. One decision per file, numbered D-001, D-002… Five fields: decision · context · options rejected · evidence · supersedes. The rejected options are what make it recoverable — "we were sound up to D-023" only works if D-023 lists what else was on the table.
- **PROOF:** open last week's decision → you can name what you rejected and what evidence backed it. Only know what you chose? That's an outcome, not a decision.
- Exploratory project? Work decision to decision — each entry supports or debunks an assumption, backed by research not supposition. The assumptions that survive become the premises of your TDDs.

**9. How you know**
- [ ] Every claim names its source artefact — log line, query, run link. Ask for the breakdown, not the total; ask what's available, not what's on.
- **PROOF:** pick a claim at random → reach the raw evidence in under a minute.

**10. Secrets out (public repo = no second chances)**
- [ ] `.gitignore` lists `.env` BEFORE first commit; all keys in the platform, by name only. Wire a secret-scanner into the gate.
- **PROOF:** search project → zero real keys.

**11. Self-contained tests (do early)**
- [ ] Tests run isolated — no internet, no services. Add one trivial test.
- **PROOF:** tests pass in seconds with internet OFF.

**12. The gate**
- [ ] Auto-deploy only if tests pass; ship by MERGING. Deploy token scoped + named exactly right.
- **PROOF:** (proven in step 13 — don't trust yet).

**13. PROVE the gate (never skip)**
- [ ] Push a FAILING test → watch deploy get blocked → fix → watch it ship.
- **PROOF:** you SAW it block bad, allow good.

**14. Make it BINDING**
- [ ] Branch protection on: require PR, require the check, no bypass — not even for you. Push straight to main and watch it get REFUSED.
- **PROOF:** a failing PR reads BLOCKED, not just "red X." The gate stops the deploy; only this stops the human.

**15. Hand-deploy dies**
- [ ] Merging is the only way to ship. Manual = emergencies only.
- **PROOF:** a merge reaches prod with no command from you.

## GO PRIVATE — at the first of these, whichever comes first

- [ ] first real credential · first real user data · first live deploy

Flipping to Private costs you the Planner's direct view of the repo — pre-flight reverts to handing it the close-out + a snapshot by hand:
```
git archive --format=tar.gz -o ‹name›-$(date +%Y%m%d).tar.gz HEAD
```

## DAILY RITUALS — every session

Never keep one chat open for days; continuity lives in the REPO, not the chat.

**Post-flight (close of session)**
- [ ] AI writes a session close-out → commit it to `docs/`. That's tomorrow's baton. Uncommitted = invisible to the Planner.

**Pre-flight (start of session)**
- [ ] New chat (not yesterday's). Upload nothing — the Planner already reads the connected repo.
- [ ] Tell it: "Read the latest close-out and [doc]. Where are we, what's next?"
- **PROOF:** it summarizes your state with no explaining from you. Grounded in a minute.
