# Security Policy

## Supported versions

Security fixes are provided for the most recent minor release of the current
major version. Older minor releases receive fixes only when the issue is
severe and a straightforward backport exists.

| Version | Supported |
| --- | --- |
| 1.0.x | Yes |
| Older than 1.0 | No |

## Reporting a vulnerability

Please do not open a public issue for a security problem. Report it privately
by email to yunus.imanov@metropolia.fi with the subject line
`discretus security report`.

A useful report contains the affected version, the platform and interpreter
version, a description of the issue, a minimal reproduction, and an
assessment of the impact if you have one.

## Disclosure process

1. The report is acknowledged within five working days.
2. The issue is triaged and its severity assessed within ten working days.
3. A fix is prepared privately together with a regression test.
4. A patched release is published and the reporter is credited unless they
   prefer to remain anonymous.
5. Details are disclosed publicly after the release, normally within ninety
   days of the original report.

## Scope

discretus is a computational library with no mandatory third party
dependencies and no network access. The most relevant security concerns are
therefore untrusted input handling in the parsers and deserializers, namely
the propositional formula parser, the DIMACS reader, and the GraphML, GML,
JSON, and CSV readers. Resource exhaustion caused by deliberately large
inputs to those readers is in scope. Deliberate misuse of the pickle helper
on untrusted data is out of scope, because that limitation is documented in
the module itself.

The cryptographic primitives in `discretus.number_theory.crypto` are
provided for teaching and experimentation. They are not hardened against
side channel attacks and must not be used to protect real secrets. Reports
that a teaching primitive is unsuitable for production use are therefore
documentation issues rather than vulnerabilities.
