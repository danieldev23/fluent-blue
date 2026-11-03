# Fluent Blue: guide for AI coding agents

Fluent Blue is a design system for Python desktop applications on PyQt6 and PySide6.

## Rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.

## Quick start

```python
from fluent_blue import Button, Card, ThemeManager
from fluent_blue.compatibility.qt import QApplication, QVBoxLayout

app = QApplication([])
ThemeManager.set_theme("light")
card = Card()
layout = QVBoxLayout(card)
layout.addWidget(Button("Get Started", variant="primary"))
card.show()
app.exec()
```

## Component briefs

Read the brief for a component before you use or change it. Print one with `python -m fluent_blue.agent_prompts <Name>`.

### Buttons

- [`Button`](docs/ai/components/Button.md): A push button with variants, sizes, icons and a loading state.
- [`DangerButton`](docs/ai/components/DangerButton.md): A destructive action, such as deleting data.
- [`GhostButton`](docs/ai/components/GhostButton.md): A low-emphasis action for toolbars and dense layouts.
- [`IconButton`](docs/ai/components/IconButton.md): A square icon-only button.
- [`LoadingButton`](docs/ai/components/LoadingButton.md): A primary button with start() and stop() shortcuts for async work.
- [`OutlineButton`](docs/ai/components/OutlineButton.md): A brand-tinted action with less weight than PrimaryButton.
- [`PrimaryButton`](docs/ai/components/PrimaryButton.md): The single most important action in a view.
- [`SecondaryButton`](docs/ai/components/SecondaryButton.md): A standard action. This is the default look of Button.
- [`SplitButton`](docs/ai/components/SplitButton.md): Primary action on the left, a menu of related actions on the right.
- [`TextButton`](docs/ai/components/TextButton.md): A link-like action, typically inline with content.

### Inputs

- [`ClearableInput`](docs/ai/components/ClearableInput.md): An Input with the clear button on by default.
- [`FormField`](docs/ai/components/FormField.md): Label, control, helper text and error message as one unit.
- [`Input`](docs/ai/components/Input.md): A text input with icons, a clear button and validation state.
- [`InputGroup`](docs/ai/components/InputGroup.md): Joins an input with text or widget addons inside a single border.
- [`NumberInput`](docs/ai/components/NumberInput.md): A numeric input with bounds, steppers and arrow key support.
- [`OtpInput`](docs/ai/components/OtpInput.md): A multi-slot numeric OTP / 2FA code entry widget with auto-focus and paste support.
- [`PasswordInput`](docs/ai/components/PasswordInput.md): A masked input with a visibility toggle.
- [`SearchInput`](docs/ai/components/SearchInput.md): A clearable search field that debounces typing.
- [`TagInput`](docs/ai/components/TagInput.md): An input field that converts typed text into removable tags on Enter or comma.
- [`TextArea`](docs/ai/components/TextArea.md): A multi-line plain text input.

### Selection

- [`Checkbox`](docs/ai/components/Checkbox.md): A checkbox, with optional indeterminate state.
- [`ComboBox`](docs/ai/components/ComboBox.md): An editable Select with type-ahead; free text is allowed.
- [`MultiSelect`](docs/ai/components/MultiSelect.md): Choose any number of values from a checkable popup list.
- [`RadioButton`](docs/ai/components/RadioButton.md): A radio button. Use RadioGroup for the common case.
- [`RadioGroup`](docs/ai/components/RadioGroup.md): A set of mutually exclusive radio buttons.
- [`SegmentedControl`](docs/ai/components/SegmentedControl.md): A compact, mutually exclusive option strip.
- [`Select`](docs/ai/components/Select.md): Choose one value from a list.
- [`Slider`](docs/ai/components/Slider.md): A value slider.
- [`SpinBox`](docs/ai/components/SpinBox.md): An integer input with stepper buttons.
- [`Switch`](docs/ai/components/Switch.md): An animated on/off toggle.

### Navigation

- [`Breadcrumb`](docs/ai/components/Breadcrumb.md): A trail of links to parent locations; the last entry is the current page.
- [`CommandPalette`](docs/ai/components/CommandPalette.md): A searchable command launcher.
- [`DropdownMenu`](docs/ai/components/DropdownMenu.md): A button that opens a Menu.
- [`Menu`](docs/ai/components/Menu.md): A popup menu.
- [`MenuItem`](docs/ai/components/MenuItem.md): A menu entry.
- [`NavigationBar`](docs/ai/components/NavigationBar.md): A horizontal application bar with title, start, center and end regions.
- [`Pagination`](docs/ai/components/Pagination.md): Page navigation with ellipsis and optional range text.
- [`Sidebar`](docs/ai/components/Sidebar.md): A vertical, sectioned, collapsible navigation rail.
- [`SidebarItem`](docs/ai/components/SidebarItem.md): One navigation entry.
- [`TabBar`](docs/ai/components/TabBar.md): A standalone tab strip with an underline indicator.
- [`Tabs`](docs/ai/components/Tabs.md): Tabbed pages built on QTabWidget, using TabBar.

### Data Display

- [`Avatar`](docs/ai/components/Avatar.md): A user image or initials.
- [`AvatarGroup`](docs/ai/components/AvatarGroup.md): Overlapping avatars with a "+N" overflow.
- [`Badge`](docs/ai/components/Badge.md): A small status label or dot.
- [`BadgeOverlay`](docs/ai/components/BadgeOverlay.md): Wraps any child widget and pins a Badge to its top-right corner.
- [`Card`](docs/ai/components/Card.md): A content container.
- [`CircularProgress`](docs/ai/components/CircularProgress.md): A circular progress indicator, which also serves as a spinner.
- [`ConsoleWidget`](docs/ai/components/ConsoleWidget.md): A high-performance rich console / terminal widget for desktop tools and logging.
- [`Divider`](docs/ai/components/Divider.md): A separator line, optionally with centered text.
- [`EmptyState`](docs/ai/components/EmptyState.md): Explains why a view is empty and what to do next.
- [`ListItem`](docs/ai/components/ListItem.md): One row of a list.
- [`Popover`](docs/ai/components/Popover.md): A floating panel anchored to a widget. It closes on outside click or Escape.
- [`ProgressBar`](docs/ai/components/ProgressBar.md): A horizontal progress bar.
- [`Result`](docs/ai/components/Result.md): The outcome of an operation.
- [`Skeleton`](docs/ai/components/Skeleton.md): A placeholder with a soft shimmer while content loads. The timer stops while hidden.
- [`StatisticCard`](docs/ai/components/StatisticCard.md): A headline metric with trend.
- [`Tag`](docs/ai/components/Tag.md): A compact label for categories, optionally closable.
- [`Text`](docs/ai/components/Text.md): A label bound to a typography role and a text color role.
- [`Timeline`](docs/ai/components/Timeline.md): A vertical sequence of events.
- [`Tooltip`](docs/ai/components/Tooltip.md): Attach a rich, delayed tooltip to a widget. It also appears on keyboard focus.

### Data Tables

- [`Column`](docs/ai/components/Column.md): Describes one table column.
- [`DataTable`](docs/ai/components/DataTable.md): A table with sorting, filtering, paging, selection, column control and export.

### Feedback

- [`Alert`](docs/ai/components/Alert.md): An inline message in the page flow.
- [`ConfirmDialog`](docs/ai/components/ConfirmDialog.md): Ask the user to confirm an action.
- [`LoadingOverlay`](docs/ai/components/LoadingOverlay.md): Blocks a widget and shows a spinner while it is busy.
- [`MessageDialog`](docs/ai/components/MessageDialog.md): A modal with a status icon, a message and buttons.
- [`Notification`](docs/ai/components/Notification.md): A richer message with a title and an action, which stays until dismissed by default.
- [`ProgressDialog`](docs/ai/components/ProgressDialog.md): A modal that reports the progress of a long operation.
- [`Snackbar`](docs/ai/components/Snackbar.md): A single-line message at the bottom center, often offering an undo.
- [`Toast`](docs/ai/components/Toast.md): A brief, auto-dismissing message in the window's top right corner.

### Layout

- [`CollapsiblePanel`](docs/ai/components/CollapsiblePanel.md): A panel whose content expands and collapses.
- [`Container`](docs/ai/components/Container.md): Centers content and limits its width, keeping long lines readable on wide screens.
- [`Drawer`](docs/ai/components/Drawer.md): A panel that slides in from the edge of a window.
- [`FluentWindow`](docs/ai/components/FluentWindow.md): A frameless base window styled with Fluent Blue design language.
- [`Grid`](docs/ai/components/Grid.md): A grid with a fixed column count, or responsive columns from a minimum width.
- [`Modal`](docs/ai/components/Modal.md): A themed modal dialog over a dimmed parent window.
- [`Panel`](docs/ai/components/Panel.md): A titled section with a header action area.
- [`ScrollArea`](docs/ai/components/ScrollArea.md): A frameless scroll area with themed scrollbars and a resizable content widget.
- [`Splitter`](docs/ai/components/Splitter.md): A resizable split view.
- [`Stack`](docs/ai/components/Stack.md): Arranges children in a row or column with token spacing.
- [`TitleBar`](docs/ai/components/TitleBar.md): Custom titlebar with native-like window management buttons, draggable area, and branding.

### Advanced Components

- [`Calendar`](docs/ai/components/Calendar.md): A month view. Arrow keys move, Enter selects and Page Up/Down change the month.
- [`CodeEditor`](docs/ai/components/CodeEditor.md): A code editor with line numbers, syntax colors and smart indentation.
- [`ColorPicker`](docs/ai/components/ColorPicker.md): A swatch button that opens a saturation/value square, hue bar, hex field and presets.
- [`DatePicker`](docs/ai/components/DatePicker.md): A date field with a popup calendar.
- [`FilePicker`](docs/ai/components/FilePicker.md): A path field with a browse button and drag and drop.
- [`FileTree`](docs/ai/components/FileTree.md): A lazily loaded file system tree, using QFileSystemModel.
- [`ImageViewer`](docs/ai/components/ImageViewer.md): An image viewer with zoom, pan, rotate and fit.
- [`LogViewer`](docs/ai/components/LogViewer.md): A live log view with level filtering, search and tailing.
- [`RichTextEditor`](docs/ai/components/RichTextEditor.md): A rich text editor with a formatting toolbar.
- [`Stepper`](docs/ai/components/Stepper.md): Shows progress through ordered steps. Arrow keys move when clickable.
- [`TimePicker`](docs/ai/components/TimePicker.md): A time field with hour and minute columns.
- [`TreeView`](docs/ai/components/TreeView.md): A tree from nested dicts, with built-in filtering.
- [`Wizard`](docs/ai/components/Wizard.md): A multi-step flow with a stepper, validation and navigation.

### Uncatalogued

- [`Command`](docs/ai/components/Command.md): An entry in the palette. action runs when the command is chosen.
- [`DataTableModel`](docs/ai/components/DataTableModel.md): Serves rows after filter, sort and page.
- [`FieldLabel`](docs/ai/components/FieldLabel.md): The label of a FormField.
- [`FieldMessage`](docs/ai/components/FieldMessage.md): Helper or validation text under a field.
- [`FloatingTooltip`](docs/ai/components/FloatingTooltip.md): The window drawn by Tooltip.
- [`RichTextArea`](docs/ai/components/RichTextArea.md): The editing surface of RichTextEditor.
- [`SyntaxHighlighter`](docs/ai/components/SyntaxHighlighter.md): Regex-based highlighter whose colors come from theme roles.
- [`TimePopup`](docs/ai/components/TimePopup.md): Hour and minute columns used by TimePicker.
- [`ToastCard`](docs/ai/components/ToastCard.md): The card behind Toast, Notification and Snackbar.
