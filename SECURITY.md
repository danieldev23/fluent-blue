# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |

## Reporting a vulnerability

Please do not open a public issue for security problems.

Use GitHub's private vulnerability reporting on this repository ("Security" tab, "Report a vulnerability"). Include the affected version, the binding and Qt version, a description of the impact and steps to reproduce.

You will receive an acknowledgement within 72 hours. We aim to publish a fix, or a mitigation, within 14 days of confirming a report, and we will credit you in the release notes unless you prefer otherwise.

## Scope notes

Fluent Blue is a UI library and runs no network code. The areas most relevant to security are:

- `fluent_blue.studio` executes catalog and Playground code with `exec`. The Playground runs code that the person typed themselves, in their own process; treat it like a Python console, and do not expose it to untrusted input.
- `FilePicker`, `FileTree` and the export functions of `DataTable` and `LogViewer` touch the file system only at paths the user chooses.
