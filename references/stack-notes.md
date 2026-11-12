# Stack notes

Aomi is stack-agnostic, but a few translations are worth writing down so the rules
do not get re-derived (or quietly ignored) per framework.

## Tailwind or utility CSS

- Put the scales in the theme and never use arbitrary values in a component.
  `p-[13px]` is a token that has not been named yet.
- Tokens by role, not by colour: `bg-surface`, `text-ink-muted`, `border-line`.
  `bg-gray-100` renames a decision into a shade, and the decision is lost.
- One component file per concept, with variants declared as data, not as
  concatenated conditionals.
- `hover:` styles: colour, border or shadow. Not `scale`, not `translate` on
  anything that sits in a grid.
- Dark mode via the token layer, never as a second set of utility classes per
  component.

## React and similar component runtimes

- Model view state as one discriminated value, not five booleans.
- Data fetching belongs to a query layer with an owner and an invalidation rule,
  not to a component's effect.
- Server state and form state are different problems. Solving both with one hook
  is how forms lose values on error.
- Memoise after measuring, not by default; a wrong dependency array is a bug that
  looks like a performance fix.
- Every list needs a stable key from the data, never the index.

## Plain HTML and CSS

- Semantic elements first: `nav`, `main`, `button`, `table`, `dialog`. A `div`
  with a click handler is a bug in accessibility terms.
- Custom properties for tokens, `clamp()` for fluid type, `:focus-visible` for
  rings, `prefers-reduced-motion` for the motion layer.
- One stylesheet layer order: tokens, reset, primitives, components, utilities.
  Unlayered CSS wins fights it should lose.

## Platform-hosted apps (no hand-written server)

When the app runs on a managed platform where entities, auth and hosting already
exist:

- The platform's schema is the database: constraints, field types and required
  fields carry the rules that migrations would otherwise carry.
- Row-level access is the authorisation function. State it in `decisions.md`, and
  test it by trying the request as the wrong user, not by reading the config.
- Backend functions are the boundary: validate there, not only in the client.
- Everything in `engineering/backend.md` about idempotency, secrets and deletion
  still applies; only the plumbing changes.

## Mobile and native

- Density and target size follow the platform's own guidance; Aomi's spacing scale
  maps to it rather than replacing it.
- Motion and haptics are feedback, subject to the same budget as web motion.
- Safe areas, keyboard avoidance and permission prompts are states, and each needs
  a designed refusal path.
