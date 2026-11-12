# Aomi's philosophy

Six statements. Everything else in this skill is a consequence of them.

## 1. Understanding is the first deliverable

A build that starts before there is a shared picture of the product costs more
than the hour it saved. Before writing code, say what you believe is being
built, in plain language, and get a yes. That paragraph is cheap; a rebuild is
not.

## 2. Decide once, in writing

Two decisions made in two places become four. Architecture and visual direction
are decided together, in one file, each with a reason and a rejected
alternative. A decision without an alternative is not a decision, it is a
default.

## 3. Design is a consequence, not a coat

Visual choices come from the product's job, its audience and the shape of its
content. A palette earns its place by surviving the room it will be read in. A
typeface earns its place by fitting the reading distance. A choice that cannot
be derived from any of that is decoration, and decoration is what the Slop Gate
removes.

## 4. The cheapest fix is upstream

Every hour of refinement at the end is a fee for a decision that was skipped at
the start. When refining, ask what decision would have prevented the problem,
and record it.

## 5. Measure what can be measured, write down what cannot

Contrast ratios, feature coverage, broken links, asset weight: tools answer
these, and no opinion should override a measurement. Tone, hierarchy, whether
something feels calm: tools cannot answer these. Write the judgment down so a
later reader can disagree with a sentence instead of a vibe.

## 6. Instructions cost context

Every line of guidance takes budget away from the actual work. Aomi is short on
purpose and modular: `SKILL.md` routes, and only the file the task needs is
read. A skill that must be read entirely before starting is a skill that will be
skimmed.

---

## The two intelligences

Aomi treats engineering and design as one discipline with two languages.

Engineering asks: *will this hold?* It answers with schemas, boundaries, error
paths, tests and measurements.

Design asks: *will this be understood?* It answers with hierarchy, type,
contrast, motion and language.

The failure they share is the same: a solution that is plausible in a screenshot
or a diagram and wrong in use. Aomi is built to catch that failure, in both
languages, before the user does.
