# Changelog

The changelog lives at the repository root, in `CHANGELOG.md`, and is
included below in full. Keeping one copy means the file a maintainer edits
during a release is the file a reader sees here, so the published changelog
can never lag behind the released version.

How to read it:

- Entries are grouped under `Added`, `Changed`, `Deprecated`, `Removed`,
  `Fixed`, `Security`, `Performance`, and `Documentation`, in that order,
  and a heading is omitted when it has no entries.
- Every entry is written from the point of view of somebody upgrading. It
  names the interface, says what is different, and gives the replacement
  where existing code could break.
- The `Unreleased` section accumulates changes between releases. If a change
  you need is listed there, it is merged but not yet published, and you can
  install it from the main branch as described in
  [installation](installation.md).

What the version numbers promise, in short: within a major version the
public interface is backward compatible, a patch release never changes a
documented result, a minor release may add and deprecate interface but not
remove it, and a major release may remove interface that was deprecated at
least one minor release earlier. The full policy, including what counts as
public, is stated in the file itself.

```{include} ../CHANGELOG.md
:start-after: "# Changelog"
```
