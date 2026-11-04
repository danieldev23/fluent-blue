# Changelog

All notable changes are documented here. The project follows [Semantic Versioning](https://semver.org/); until 1.0, breaking changes bump the minor version.

## Unreleased

### Added

- `Rating`: star rating with half steps, hover preview, keyboard control and a read-only mode.
- `RangeSlider`: a two-handle slider with keyboard and mouse control; the handles cannot cross.
- `Accordion`: collapsible sections, optionally exclusive.
- `Carousel`: slides with arrows, clickable dots, keyboard control and autoplay that pauses on hover, focus and while hidden.
- `Kbd`: keyboard shortcuts drawn as key caps.
- `VideoPlayer`: a themed player with seek, volume, speed, full screen and keyboard control, built on QtMultimedia. It degrades to an explanation where QtMultimedia cannot load.
- Icons `volume` and `volume-off`.

## 0.1.0 - 2026-11-04

### Added

- Design tokens for color, typography, spacing, radius, elevation and motion, with per-theme overrides.
- Runtime theme engine with light, dark and high-contrast themes, `system` following, and custom theme registration that derives a full ramp from one primary color.
- An original set of 131 SVG icons with theme-aware rendering, caching and icon registration.
- 103 components: buttons, inputs, selection, navigation, data display, a model/view `DataTable`, feedback, layout and advanced widgets (`DatePicker`, `Calendar`, `TimePicker`, `ColorPicker`, `FilePicker`, `ImageViewer`, `CodeEditor`, `LogViewer`, `TreeView`, `FileTree`, `Stepper`, `Wizard`, `RichTextEditor`).
- Fluent Blue Design Studio: an interactive showcase with live previews, generated Properties and Signals tabs, copyable code, an AI Prompt tab, a Themes page with a custom theme builder and a Playground.
- Briefs for AI coding agents (`AGENTS.md`, `llms.txt`, `docs/ai/components/`), generated from the source and checked by tests.
- Support for PyQt6 and PySide6 from one code base, tested on both.
- A UI audit (`scripts/ui_audit.py`) that measures clipped text, overlaps and rendered contrast on every Studio page, and a performance report (`scripts/perf_report.py`).
- Six runnable examples, documentation built with MkDocs Material, and CI for Linux, Windows and macOS.

### Performance

- Theme switching restyles the application in one pass and takes about 80 ms with the Studio open; it previously took more than three seconds with every page built.
- Icons, fonts and parsed colors are cached; hidden widgets refresh lazily when shown.
- Design Studio builds component pages progressively and frees hidden pages before a theme switch.
