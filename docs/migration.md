# Migration guide

## From plain Qt widgets

Fluent Blue components extend the Qt widgets you already use, so migration is incremental.

| You have | Use | Notes |
| --- | --- | --- |
| `QPushButton` | `Button` | `variant`, `size`, `icon`, `loading`; `clicked` is unchanged. |
| `QLineEdit` | `Input` | `placeholder`, `prefix_icon`, `clearable`, `validation`; wrap in `FormField` for a label and messages. |
| `QComboBox` | `Select` or `ComboBox` | Options as `"text"`, `(label, value)` or dicts; `value()` returns the Python value. |
| `QCheckBox`, `QRadioButton` | `Checkbox`, `RadioGroup` | `RadioGroup` reports `value_changed(object)`. |
| `QTableView` + model | `DataTable` | Pass dicts and `Column` specs; sorting, filtering, paging, selection and export are built in. |
| `QMessageBox` | `MessageDialog`, `ConfirmDialog` | `ConfirmDialog.ask(parent, title, message)` returns a bool. |
| `QStatusBar` messages | `Toast`, `Snackbar` | Non-blocking, themed, stacked. |
| Hand-written QSS | Tokens and themes | Delete per-widget stylesheets; register a theme with your brand `primary`. |

Keep using Qt layouts, or use `Stack`, `Grid` and `Container` for token-based spacing.

## From version 0.x to 0.y

Fluent Blue follows semantic versioning. Until 1.0, breaking changes bump the minor version and are listed under *Changed* or *Removed* in the [changelog](changelog.md), with the replacement for each removed API. Deprecated APIs emit a `DeprecationWarning` for at least one minor release before removal.

There are no migrations yet: 0.1.0 is the first release.
