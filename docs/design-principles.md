# Design principles

Fluent Blue aims to feel modern, premium, minimal and professional, and to stay usable first. These principles decide what goes into the library and what stays out.

## Usability over decoration

Every visual choice has to earn its place by making the interface clearer. There is no glassmorphism, no decorative gradient, and animation is limited to short, meaningful transitions (90 to 260 ms) that can be turned off with `configure(animations=False)`.

## One language on every screen

All components share the same spacing scale, typography roles, color tokens, control heights, interaction states, elevation rules and border treatment. A `Button`, a `Select` and an `Input` of the same size line up to the pixel. Design Studio shows these rules on the Foundations, Colors and Typography pages.

## Native to the desktop

Components extend Qt widgets wherever Qt already has the behaviour: `Input` is a `QLineEdit`, `Select` is a `QComboBox`, `DataTable` uses the model/view framework. Keyboard navigation, focus handling, accessibility names and platform conventions come from Qt, and the whole Qt API stays available.

## Tokens, not values

Components read tokens from the theme at construction and paint time; they never hardcode a color, a radius or a font. That is what makes runtime theme switching, custom brands and the high-contrast theme possible without touching components.

## Accessible by measurement, not by intent

Every text pairing in every built-in theme meets WCAG AA (4.5:1), and a test fails if a token change breaks that. A UI audit renders every Studio page and measures clipped text, overlapping widgets and the contrast of rendered pixels. Focus is visible on every interactive control, and icon-only controls carry accessible names.

## Clear hierarchy and density

Type roles from `display` to `caption`, surfaces from `background` to `surface-elevated`, and four elevation levels give each screen a readable order. Defaults favour information density suitable for professional tools, with `size="small"` variants for toolbars and `size="large"` for primary flows.

## Beautiful empty states and honest feedback

`EmptyState` and `Result` explain what will appear and what to do next. `Toast`, `Notification`, `Snackbar`, `Alert` and the dialogs each have one job, documented in their usage guidance, so feedback matches the moment.

## Independence

The visual identity, icons and artwork are original. The project takes inspiration from the discipline of mature design systems without copying their assets or branding.
