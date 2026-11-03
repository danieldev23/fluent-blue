"""Cards, badges, tags, text roles, list items, panels."""
from ...core.tokens import TYPOGRAPHY

TEXT_COLORS = ("text-primary", "text-secondary", "text-tertiary", "text-disabled", "text-inverse",
               "primary-text", "success-text", "warning-text", "error-text", "info-text", "brand-text", "brand-text-muted")
VARIANTS = ("success", "warning", "error", "info")


def build(x) -> str:
    c = x.c
    out = ""
    for style in TYPOGRAPHY:
        out += f'Text[textStyle="{style}"] {{ {x.font(style)} }}\n'
    out += f'Text[textStyle="monospace"] {{ {x.mono()} }}\n'
    for role in TEXT_COLORS:
        out += f'Text[textColor="{role}"] {{ color: {c[role]}; }}\n'
    out += f"""
Card, Panel, CollapsiblePanel {{ background: {c.surface}; border: 1px solid {c.border_subtle}; border-radius: {x.r('lg')}; }}
Card[hoverable="true"]:hover {{ border-color: {c.border_strong}; }}
Card:focus {{ border-color: {c.border_focus}; }}
Card[selected="true"] {{ border-color: {c.primary}; }}
Card[tone="secondary"] {{ background: {c.surface_secondary}; }}
Card[tone="brand"] {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {c.brand_gradient_start}, stop:1 {c.brand_gradient_end}); border: none; }}
Card[tone="brand"] QLabel {{ color: {c.on_primary}; background: transparent; }}
Badge {{ border-radius: 9px; padding: 0 7px; min-height: 18px; max-height: 18px; {x.font('caption')} font-weight: 600; }}
Badge[dot="true"] {{ border-radius: 4px; padding: 0; min-height: 8px; max-height: 8px; min-width: 8px; max-width: 8px; }}
Tag {{ border-radius: {x.r('sm')}; border: 1px solid {c.border}; background: {c.surface_secondary}; }}
Tag QLabel {{ background: transparent; border: none; {x.font('body-small')} color: {c.text_secondary}; }}
Tag QToolButton {{ background: transparent; border: none; border-radius: {x.r('xs')}; }}
Tag QToolButton:hover {{ background: {c.ghost_pressed}; }}
Tag QToolButton:focus {{ border: 1px solid {c.border_focus}; }}
"""
    neutral = (c.surface_tertiary, c.text_secondary, c.border)
    primary = (c.primary_subtle, c.primary_text, c.primary_border)
    for name, (bg, fg, bd) in {"neutral": neutral, "primary": primary}.items():
        out += f'Badge[variant="{name}"] {{ background: {bg}; color: {fg}; }}\n'
        out += f'Badge[variant="{name}"][dot="true"] {{ background: {fg}; }}\n'
        out += f'Tag[variant="{name}"] {{ background: {bg}; border-color: {bd}; }}\nTag[variant="{name}"] QLabel {{ color: {fg}; }}\n'
    for name in VARIANTS:
        out += f'Badge[variant="{name}"] {{ background: {c[name + "-subtle"]}; color: {c[name + "-text"]}; }}\n'
        out += f'Badge[variant="{name}"][dot="true"] {{ background: {c[name]}; }}\n'
        out += f'Tag[variant="{name}"] {{ background: {c[name + "-subtle"]}; border-color: {c[name + "-border"]}; }}\n'
        out += f'Tag[variant="{name}"] QLabel {{ color: {c[name + "-text"]}; }}\n'
    out += f"""
ListItem {{ background: transparent; border: 2px solid transparent; border-radius: {x.r('md')}; }}
ListItem[interactive="true"]:hover {{ background: {c.ghost_hover}; }}
ListItem:focus {{ border-color: {c.border_focus}; }}
ListItem[selected="true"] {{ background: {c.primary_subtle}; }}
FloatingTooltip {{ background: {c.gray_900}; border-radius: {x.r('sm')}; }}
FloatingTooltip QLabel {{ color: {c.gray_0}; background: transparent; {x.font('body-small')} padding: 4px 8px; }}
Panel QFrame#panelHeader, CollapsiblePanel QFrame#panelHeader {{ border-bottom: 1px solid {c.border_subtle}; background: transparent; }}
CollapsiblePanel QPushButton#panelToggle {{ background: transparent; border: none; text-align: left; padding: 10px 12px; {x.font('heading-5')} outline: none; border-radius: {x.r('lg')}; }}
CollapsiblePanel QPushButton#panelToggle:hover {{ background: {c.ghost_hover}; }}
CollapsiblePanel QPushButton#panelToggle:focus {{ color: {c.primary_text}; }}

/* ConsoleWidget Terminal */
QWidget[fbComponent="consoleWidget"] {{
    background: {c.surface_secondary};
    border: 1px solid {c.border};
    border-radius: {x.r('lg')};
    padding: 2px;
}}
QWidget[fbComponent="consoleWidget"] QPlainTextEdit {{
    background: {c.surface_primary};
    border: none;
    border-radius: {x.r('md')};
    padding: 8px;
    selection-background-color: {c.selection};
    selection-color: {c.selection_text};
}}
QWidget[fbComponent="consoleWidget"] QToolButton {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: {x.r('sm')};
    padding: 4px;
}}
QWidget[fbComponent="consoleWidget"] QToolButton:hover {{
    background: {c.ghost_hover};
    border-color: {c.border_subtle};
}}
"""
    return out
