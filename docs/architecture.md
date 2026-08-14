# Architecture

`filetree` keeps filesystem work separate from presentation:

```text
input path
  → CLI parsing
  → traversal and filtering
  → TreeNode / TreeStats
  → text renderer or JSON serializer
  → stdout
```

`filetree.cli` owns argument validation, exit codes, and selecting an output format. `filetree.traversal` uses `os.scandir` to efficiently enumerate each visible directory once, applies hidden-name and exclusion rules before recursing, and creates the renderer-neutral model in `filetree.model`.

Traversal deliberately uses `lstat`/`follow_symlinks=False`: links are reported as leaves instead of being traversed. This prevents accidental loops and avoids treating a linked directory differently on different platforms. Read errors on children are data attached to nodes; root failures are explicit `TraversalError` values for the CLI to report.

`filetree.render` is the only layer aware of connector glyphs or JSON. This makes future renderers (Markdown, HTML) and future node metadata (sizes, timestamps, Git state) additive. The current implementation holds the visible tree in memory, which keeps both renderers simple and enables JSON; `scandir` avoids loading directory metadata unnecessarily. For normal source repositories this offers a good complexity/performance tradeoff.
