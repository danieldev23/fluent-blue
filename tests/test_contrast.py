"""Every text pairing the components use must meet WCAG AA in every built-in theme."""
import pytest

from fluent_blue.core.palette import apply_overrides, contrast_ratio, dark_colors, high_contrast_colors, light_colors

THEMES = {"light": light_colors, "dark": dark_colors, "high-contrast": high_contrast_colors}
PAIRS = [
    ("text-primary", "surface"), ("text-secondary", "surface"), ("text-tertiary", "surface"),
    ("text-primary", "background"), ("text-secondary", "background"), ("text-tertiary", "surface-secondary"),
    ("text-secondary", "surface-tertiary"), ("primary-text", "surface"), ("primary-text", "primary-subtle"),
    ("on-primary", "primary"), ("on-primary", "primary-hover"), ("on-primary", "primary-pressed"),
    ("on-error", "error"), ("on-error", "error-hover"), ("selection-text", "selection"),
    ("success-text", "success-subtle"), ("warning-text", "warning-subtle"), ("error-text", "error-subtle"), ("info-text", "info-subtle"),
    ("success-text", "surface"), ("warning-text", "surface"), ("error-text", "surface"), ("info-text", "surface"),
]


@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize(("foreground", "background"), PAIRS)
def test_text_pair_meets_aa(theme, foreground, background):
    colors = THEMES[theme]()
    ratio = contrast_ratio(colors[foreground][:7], colors[background][:7])
    assert ratio >= 4.5, f"{foreground} on {background}: {ratio:.2f}"


def test_brand_ramp_keeps_its_value():
    assert light_colors()["primary-500"] == "#1677FF"


@pytest.mark.parametrize("base", [light_colors, dark_colors])
def test_custom_primary_stays_readable(base):
    colors = apply_overrides(base(), {"primary": "#7C3AED"}, base is dark_colors)
    assert contrast_ratio(colors["on-primary"], colors["primary"]) >= 4.5
    assert contrast_ratio(colors["on-primary"], colors["primary-hover"]) >= 4.5
    assert contrast_ratio(colors["primary-text"], colors["surface"]) >= 4.5
