# Accessibility

Not a phase at the end, and not a checkbox. Two rules cover most of it: everything
works from a keyboard, and nothing carries meaning by colour alone. The rest is
detail that follows from those.

## The gate

Run this before Sign. Every line is answerable with evidence, not confidence.

- [ ] Tab reaches every interactive element, in reading order, with a visible
      focus ring.
- [ ] Shift+Tab and Escape behave: nothing traps the keyboard except a modal.
- [ ] Every image has a decision: descriptive alt, empty alt if decorative,
      caption if it carries data.
- [ ] Every form control has a programmatic label, and errors are announced.
- [ ] Headings descend without skipping levels, and there is one `h1`.
- [ ] Landmarks exist: `nav`, `main`, `header`, `footer` (or ARIA equivalents).
- [ ] Text contrast passes at 4.5:1, large text at 3:1, in both themes.
- [ ] Non-text UI that carries meaning passes 3:1.
- [ ] Colour is never the only carrier of state.
- [ ] Nothing depends on hover for information on a touch device.
- [ ] Targets are at least 44×44px.
- [ ] The layout survives 200% zoom and 320px width without horizontal scrolling
      for prose.
- [ ] Motion respects `prefers-reduced-motion`.
- [ ] Media has captions or a transcript, if it carries the content.
- [ ] The page has a title that names the screen, and it updates on navigation.
- [ ] Language is declared, so screen readers pronounce it correctly.

## How to test it for real

1. Keyboard only: unplug the mouse and complete the primary task. This finds more
   bugs than any automated tool.
2. Zoom to 200% and repeat.
3. Screen reader on the primary flow: one of VoiceOver, NVDA or TalkBack. Listen
   for the two failures that matter: unlabelled controls, and focus that jumps.
4. Colour-blind check: view the state-bearing screens through a protanopia and
   deuteranopia filter.
5. Automated pass (axe or equivalent) for the mechanical checks, knowing it will
   not find the semantic ones.

## Failure patterns that pass automated checks

- A `div` with a click handler: reachable by mouse, invisible to keyboard.
- Icon-only buttons with no accessible name.
- A modal built from `position: fixed` with no focus management.
- Error messages that appear in colour but are never announced.
- Custom selects that lose the label association.
- Placeholder text used as a label.
- `aria-label` on a container, overriding its children's text for the reader.
- Carousels that auto-advance faster than a person can read.

## Reporting

In `aomi/proof.md`, each accessibility finding gets: what a keyboard or screen
reader user experiences, the smallest fix, and whether it blocks. "Blocks" means
the primary task cannot be completed. Everything else is scheduled, not skipped.
