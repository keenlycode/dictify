# Changelog

## 4.0.0

- `Model` now behaves as a `MutableMapping` instead of subclassing `dict`.
- Model fields are now annotation-first: `name: str = Field(...)` is the preferred declaration style.
- Declared model fields support descriptor-style attribute access alongside mapping access.
- Undeclared public attributes now follow `strict` in the same way as undeclared keys.
- The minimum supported Python version is now `3.12`.
- Runtime support for annotated `Field(...)` model declarations is complete, but static type checker support is still limited and may require `cast(Any, Field(...))` depending on the checker.
