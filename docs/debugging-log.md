# Debugging Log

Running record of every non-trivial problem: what broke, why, and how it was fixed.
Written for two audiences — future-me debugging something similar, and interview stories ("tell me about a hard bug you solved").

## Entry template

```markdown
## YYYY-MM-DD — Short title of the problem

**Phase:** 1/2/3/4
**Symptom:** What you observed (error message, wrong behavior, nothing happening).
**Expected:** What should have happened.
**Investigation:** What you checked, in order. Dead ends count — they show process.
**Root cause:** The actual underlying problem.
**Fix:** What resolved it.
**Lesson:** One-liner takeaway.
```

---

<!-- Entries go below, newest first -->

## 2026-07-02 — "5 + #clamp_pitch" rejected in a dimension box

**Phase:** 1 (chassis plate CAD)
**Symptom:** Typing `5 + #clamp_pitch` into an Onshape dimension errored, even though `#clamp_pitch` alone worked fine.
**Root cause:** Unit strictness. A bare `5` in an expression is a unitless number; `#clamp_pitch` is a length (28.3 mm). Onshape refuses to add a number to a length — the same class of unit-mismatch error that killed the Mars Climate Orbiter.
**Fix:** `5mm + #clamp_pitch` — give every literal its units when mixing with variables.
**Lesson:** In engineering tools, units are part of the value, not decoration. Strictness that feels pedantic is protecting you.

## 2026-07-02 — Sketch linear pattern refused to go vertical

**Phase:** 1 (chassis plate CAD)
**Symptom:** Second direction of a *sketch* linear pattern kept duplicating holes horizontally no matter what was clicked.
**Fix / better tool:** Abandoned the sketch pattern; cut ONE hole, then used the *feature-level* Linear pattern, where directions are chosen by clicking actual plate edges (bottom edge = direction 1, left edge = direction 2) — unambiguous by construction.
**Lesson:** When a tool makes you guess (drag arrows, hidden angles), look for the variant that lets you point at real geometry instead. Feature patterns > sketch patterns for patterning cuts.

## 2026-07-02 — Motor pocket came out the wrong size in first CAD sketch

**Phase:** 1 (chassis CAD, test-fit coupon)
**Symptom:** Pocket in the Onshape sketch measured ~9.2 × 7 mm instead of the required 12.3 × 10.3 mm, despite "everything being dimensioned."
**Expected:** A 12.3 × 10.3 pocket, fully defined.
**Investigation:** All four dimensions were distances from the tile's edges to the pocket's edges (7, 20, 13, 23.792). The 23.792 with random decimals was the tell — that gap was just wherever the mouse happened to drop the rectangle, and the pocket's size became "whatever was left over."
**Root cause:** Over-dimensioned *position* (gaps from every edge) instead of dimensioning *size + position*. The feature's actual design intent — "this pocket is 12.3 wide because the motor is 12 wide" — wasn't captured anywhere in the sketch.
**Fix:** Deleted the top/right gap dimensions; dimensioned the pocket's own edges (12.3, 10.3) plus two position dims (7 from left, 20 from bottom). Sketch went fully defined (black) with the correct size.
**Lesson:** Dimension what you *mean*: a feature's size directly, then its position — never let a dimension be implied by leftovers. Blue lines = under-defined = something can still drift; weird decimals = a value nobody chose.
