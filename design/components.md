# Components

A component is a promise about behaviour. Build the promise once, in one place,
then reuse it so the promise cannot drift.

## Inventory before markup

Before writing a component, list the ones the product actually needs. A typical
app needs eight to twelve, not forty. Then, for each, write its states. A
component without a written state list will ship with five states instead of
eight, and the missing three will be the ones users hit.

```
Button      default hover focus active disabled loading
Input       default focus filled disabled invalid readonly helper
Select      default open searching empty multi-value error
Row         default hover selected focused dragging empty
Panel       closed opening open closing error
Table       sorting filtered empty partial-error loading-busy
Notice      info success warning danger, dismissible or not
Dialog      default confirm destructive busy, with focus trap
```

## One scale, several values

Radius and elevation are scales that express hierarchy, not signatures applied
everywhere.

| layer | radius | elevation |
| --- | --- | --- |
| input, badge, chip | small | none, a 1px line |
| card, row group | medium | one soft step |
| panel, popover | large | one step above cards |
| dialog, sheet | extra large | highest, plus a scrim |
| pill, avatar | full | none |

A single radius on every surface is the most common tell that a component library
was never designed, only installed.

## Hierarchy of actions

Per region: one filled button, any number of outlined or text actions, and a
destructive action that is never filled. Order in the DOM follows importance,
not looks. If a screen needs four filled buttons, it has four primary actions and
therefore none.

## Inputs

- A visible label, programmatically associated. A placeholder is not a label: it
  vanishes on the first keystroke.
- Validation on blur and on submit, not on every keystroke.
- The error message says what to do, sits next to the field, and is announced.
- Success is visible but quiet; do not celebrate a correct field.
- Group related fields; a long form with no grouping is a tax on the user.
- Persist what the user typed when validation fails, always.

## Tables and lists

- Decide the sort, the default order and the empty case before building.
- Numbers are right-aligned and tabular; text is left-aligned.
- Row actions appear on hover only if they are also reachable by keyboard and
  visible on touch.
- Long lists virtualise only after measuring; premature virtualisation breaks
  find-in-page and screen readers.
- A row that is a link behaves like a link: real anchor, middle-clickable.

## Empty, loading and error

These are not edge cases; for a new user they are the product.

- **Empty**: say what would be here, why it is not, and the one action that
  fills it. Never an illustration with no instruction.
- **Loading**: a skeleton that matches the real layout for anything over 300ms;
  a spinner only for actions, with the label preserved.
- **Error**: what happened, whether it is the user's fault, and the retry.
  Keep the partial data on screen.

## Consistency rules that actually prevent drift

- One spacing scale, one radius scale, one elevation scale, one motion set. A
  component may not invent a value.
- Tokens only in components: no raw hex, no magic pixels. A missing value is a
  token to add, not a literal to inline.
- Variants are declared, not improvised: if a component needs a new look, it gets
  a named variant, so the difference is intentional and searchable.
- If two components look the same and behave differently, one of them is wrong.
