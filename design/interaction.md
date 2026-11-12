# Interaction and motion

Motion is feedback, or it is noise. The test is simple: if the animation is
removed, does the user lose information? If yes, keep it. If no, cut it or make
it shorter.

## Budget

Animate a minority of the interface: hovers, entrances of things that appeared
because of the user's action, and state changes that would otherwise be
ambiguous. A page where everything fades in on scroll is a page where nothing is
emphasised.

## Timing

| change | duration | easing |
| --- | --- | --- |
| hover, small state | 100–140ms | ease-out |
| button press | 80–120ms | ease-out |
| popover, tooltip | 130–180ms | ease-out in, faster out |
| panel, sheet | 200–260ms | ease-out in, ease-in out |
| page or route change | 0–160ms | prefer none |
| anything above 300ms | justify it in a sentence |

Exit animations run at about 70% of the entrance duration. A slow exit makes the
interface feel reluctant.

## Properties

Transform and opacity only. Animating width, height, top or left forces layout on
every frame and will stutter on the device the user actually owns. Use
`will-change` sparingly and remove it after.

## Reduced motion

Every spatial animation has a `prefers-reduced-motion: reduce` counterpart:
duration near zero, or a cross-fade instead of a movement. This is not optional
and it is not a nicety; it is the difference between usable and unusable for
people with vestibular sensitivity. A missing counterpart is a weight-3 signal in
the Slop Gate.

## Feedback the interface owes the user

- **Every action gets an acknowledgement within 100ms**, even if the work takes a
  second. Silent buttons get double-clicked.
- **Long work shows progress or a state**, and can be left: the user should be
  able to navigate away without losing the operation.
- **Destructive actions confirm, and the confirmation names the object.** "Delete
  project" is not a confirmation; "Delete *Clinic schedule 2026*? This removes 14
  appointments." is.
- **Undo beats a confirmation dialog** wherever the operation is reversible.
- **Optimistic updates must have a rollback** that is visible, with the reason.

## Focus and keyboard

- Focus is always visible, with a 2px ring at 3:1 against both the element and
  its background. Never `outline: none` without a replacement.
- Focus order follows reading order; the DOM order is the truth.
- Dialogs trap focus, restore it on close, and close on Escape.
- Shortcuts are discoverable, do not fire while typing in a field, and never
  override the browser's own.

## Transitions between states

A state change that moves content (filter, sort, expand) needs to be legible: the
changed element gets a brief highlight, or the list animates from its old
position. A list that silently reorders under the cursor is a bug, not a feature.

## What to leave out

- Parallax and scroll-jacking.
- Infinite ambient movement, looping gradients, floating decoration.
- Typewriter effects that delay real content.
- Count-up numbers on data the user came to read.
- Bounce easing on anything a user triggers repeatedly.
