# Scenario tests

Three scenarios that test the thing Aomi claims to do, rather than the thing it
is made of. A file existing is not evidence; these are.

Each scenario states the input, the steps a person would follow, and what would
have to be true for it to pass.

---

## S1. A small build, from nothing to a gate that clears

**Input:** "Buat halaman jadwal klinik: daftar appointment hari ini, satu aksi
mencatat hasil, dan kosongkan state-nya."

**Expected route:** depth `Sketch`, because it is one screen. Aomi should not
produce `map.md` or run recon for this.

**Steps:** `aomi.py init`, fill `brief.md` and the design direction section of
`decisions.md`, build the page, `aomi.py audit`, `aomi.py contrast`, record both
in `proof.md`.

**Passes when:**

- the audit reports `clear` (85 or above) with no waived signal that is waived
  for a reason outside `brand`/`content`/`accessibility`/`hardware`/`legacy`;
- every text pair in `tokens.json` passes its threshold;
- the page has four states reachable without editing the database: filled,
  empty, loading, error;
- the Swap Test sentence in `proof.md` names something only this product does.

**Evidence in this repository:** `tests/fixtures/clean/page.html` is the result
of exactly this scenario, and `tests/fixtures/tokens.json` is its token file.
`AuditTest.test_clean_page_is_clear` and `ContrastTest` run them.

---

## S2. A page that fails, and a waiver that is argued

**Input:** a landing page with an indigo accent, an emoji in a launch button,
`hover:scale` on cards, "Trusted by 12,400 teams", and an image with no `alt`.

**Passes when:**

- the audit names the actual signals (SG01, SG05, SG06, SG13, SG15) and not
  others;
- the verdict is `blocked` and the command exits non-zero;
- adding a waiver for SG01 with `reason: brand` removes exactly that signal and
  raises the score by the weight times seven;
- a waiver with a made-up reason is rejected, reported, and does not count.

**Evidence:** `tests/fixtures/slop/page.html`, and the tests
`test_slop_page_is_blocked_and_names_the_signals`,
`test_waiver_removes_a_signal_and_lifts_the_score`.

---

## S3. A product, where scope is the hard part

**Input:** rebuild the booking flow of an existing scheduling product, as a
`Product` depth task.

**Expected route:** recon leaves a screen inventory with stable ids, a flow with
its step count, an inferred data model, and `features.csv` with must/should/could.
Architecture puts a uniqueness constraint in the database. Parity is scored
before ship.

**Passes when:**

- every state in the inventory has a row in the implementation or a written
  reason it was dropped;
- `parity` reports 100 on the must-haves, or the missing ones are named in
  `handoff.md` as accepted gaps;
- the double-booking path is covered by a test that fails when the constraint is
  removed;
- no screenshot, copy string, icon or colour from the reference product appears
  in the build.

**Evidence:** the tool side of this is `ParityTest`; the rest is a manual
scenario. It has **not** been executed end to end in this repository, because it
requires a real reference product and a real build. It is documented here so the
gap is visible rather than implied to be covered.

---

## What is deliberately not tested here

- Whether the design *feels* right. No scenario can settle that, and pretending
  otherwise is how a quality gate becomes theatre.
- Host behaviour on agents other than the one this repository was installed in.
  See `docs/compatibility.md`.
- Destructive or paid actions: no scenario in this repository deploys, charges or
  contacts anyone.

## Running the automated part

```bash
python3 -m unittest discover -s tests -v
```

The suite covers the command line, the fixtures above, the skill's own structure
(`doctor`), and one consistency test that reads `design/slop-gate.md` and
`scripts/aomi.py` and fails if a documented weight and an implemented weight
disagree.
