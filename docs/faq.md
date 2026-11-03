# FAQ

**Which binding should I choose?**
Either. The library is tested on both. PySide6 is LGPL-licensed and maintained by The Qt Company; PyQt6 is GPL or commercial. Your application's licensing decides.

**Can I use PyQt6 and PySide6 in the same process?**
No, and Fluent Blue refuses to try. It raises `BindingError` if both are imported.

**Do I have to call `ThemeManager.set_theme`?**
No. The first component applies the light theme. Call it to choose another theme or to follow the system.

**Why does the theme switch rebuild hidden pages in Design Studio?**
A stylesheet change visits every live widget. Studio drops hidden pages before a switch and rebuilds them on the next visit (about 40 ms), which keeps the switch at about 80 ms however many pages were opened. Your application can do the same with heavy, rarely shown views.

**Why are my colors slightly different from the brand value I passed?**
`register_theme` keeps `primary` exactly as given, but derives hover, pressed, subtle and text roles from it, and picks `on-primary` for contrast. Override any derived role explicitly if you need a specific value.

**How do I use my own icons?**
`register_icon("name", svg_markup)` or `register_icon_file("name", path)`. Use `currentColor` in the SVG where the theme color should apply, then pass the name anywhere an `icon` argument is accepted.

**Can I style a component with a stylesheet?**
Prefer props and token overrides. If you must, set rules on the application after `set_theme`, keyed by the same class names and dynamic properties the library uses (`Button[variant="ghost"]`), and reapply on `theme_changed`.

**Does `DataTable` handle large data?**
Yes. Rows stay in your list; sorting and filtering reorder integer indices. 100,000 rows build in about 100 ms and sort in about 40 ms on a laptop.

**Is Fluent Blue affiliated with Microsoft?**
No. It is an independent open-source project, inspired by the discipline of modern design systems, with its own visual identity, icons and artwork.

**How do I report a bug?**
Open an issue with the output of `python -c "import fluent_blue as f; print(f.BINDING, f.BINDING_VERSION, f.QT_VERSION)"`, your operating system, a minimal snippet and, for visual problems, a screenshot.
