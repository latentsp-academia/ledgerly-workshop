# Value objects (house style for services/ and payments/)

- Business logic for a ticket goes in a `services/` function. Routes only map HTTP in and out.
- Every **new** class holding data is
  `@dataclass(frozen=True, slots=True, kw_only=True)`:
  - `frozen`: a result can't be mutated after a service hands it back.
  - `kw_only`: two int fields (e.g. `amount_cents`, `invoice_id`) can't be swapped positionally.
    That exact bug shipped once (LED-077).
  - `slots`: no stray attributes.
- Services return value objects, **never dicts** (no `dict`, `Mapping`, `TypedDict`, `NamedTuple`).
  The API maps value objects to pydantic response models.
- Exceptions are exempt. Older classes (`Invoice`, `Line`) predate this rule; don't copy them,
  and don't rewrite them unless the ticket asks.
- `services/reports.py` is legacy (dicts and floats). It is not an example.
