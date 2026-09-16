---
name: Bug report
about: Report incorrect behavior, a crash, or a wrong mathematical result
title: "bug: "
labels: ["bug", "needs triage"]
assignees: []
---

## Description

A clear description of what goes wrong.

## Expected mathematical result

State the correct result and how you know it, for example a definition, a
theorem, a textbook value, or a hand computation.

## Actual result

State what discretus returned, including the exact output or traceback.

## Minimal reproduction

```python
from discretus import ...

# The smallest program that shows the problem.
```

## Environment

- discretus version (`python -c "import discretus; print(discretus.__version__)"`):
- Python version (`python --version`):
- Operating system:
- Installation method (pip, conda, from source):
- Optional extras installed (viz, docs, dev):

## Additional context

Add anything else that helps, such as the size of the input, whether the
problem is deterministic, or whether an earlier version behaved correctly.
