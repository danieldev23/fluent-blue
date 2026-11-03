"""Buttons, split buttons and segmented controls."""


def _variant(sel, bg, fg, border, hover_bg, press_bg, hover_border=None, press_border=None, focus_border=None, c=None):
    fb = focus_border if focus_border is not None else (hover_border or border)
    return f"""
{sel} {{ background: {bg}; color: {c[fg]}; border: 1px solid {border}; }}
{sel}:hover {{ background: {hover_bg}; border-color: {hover_border or border}; }}
{sel}:pressed {{ background: {press_bg}; border-color: {press_border or hover_border or border}; }}
{sel}:focus {{ border-color: {fb}; outline: none; }}
{sel}:disabled {{ color: {c['text-disabled']}; }}
"""


def build(x) -> str:
    c = x.c
    out = f"""
Button {{ border: 1px solid transparent; border-radius: {x.r('md')}; padding: 0 14px; {x.font('button')}
    min-height: {x.h('medium', 2)}; outline: none; }}
Button[fbSize="small"] {{ min-height: {x.h('small', 2)}; padding: 0 10px; {x.font('body-small')} font-weight: 500; }}
Button[fbSize="large"] {{ min-height: {x.h('large', 2)}; padding: 0 18px; {x.font('body-large')} font-weight: 500; }}
Button:disabled {{ background: {c.control_disabled}; border-color: transparent; }}
IconButton {{ padding: 0; }}
IconButton[fbSize="small"] {{ padding: 0; }}
IconButton[fbSize="large"] {{ padding: 0; }}
Button::menu-indicator {{ image: url({x.asset('chevron-down', 'text-secondary')}); width: 14px; height: 14px;
    subcontrol-position: right center; subcontrol-origin: padding; right: 6px; }}
Button[hasMenu="true"] {{ padding-right: 24px; }}
Button[variant="text"][hasMenu="true"] {{ padding-right: 22px; }}
Button[variant="primary"]::menu-indicator, Button[variant="danger"]::menu-indicator {{ image: url({x.asset('chevron-down', 'on-primary')}); }}
"""
    out += _variant('Button[variant="primary"]', c.primary, "on-primary", "transparent", c.primary_hover, c.primary_pressed, focus_border="transparent", c=c)
    out += f'Button[variant="primary"]:disabled {{ background: {c.control_disabled}; }}\n'
    out += _variant('Button[variant="secondary"]', c.control, "text-primary", c.border, c.control_hover, c.control_pressed, c.border_strong, focus_border=c.border_strong, c=c)
    out += f'Button[variant="secondary"]:disabled {{ background: {c.control_disabled}; border-color: {c.border_subtle}; }}\n'
    out += _variant('Button[variant="outline"]', "transparent", "text-primary", c.border, c.control_hover, c.control_pressed, c.border_strong, focus_border=c.border_strong, c=c)
    out += f'Button[variant="outline"]:disabled {{ background: transparent; border-color: {c.border_subtle}; }}\n'
    out += _variant('Button[variant="ghost"]', "transparent", "text-secondary", "transparent", c.ghost_hover, c.ghost_pressed, focus_border="transparent", c=c)
    out += f'Button[variant="ghost"]:hover {{ color: {c.text_primary}; }}\nButton[variant="ghost"]:disabled {{ background: transparent; }}\n'
    out += f'Button[variant="ghost"]:checked {{ background: {c.primary_subtle}; color: {c.primary_text}; }}\n'
    out += _variant('Button[variant="text"]', "transparent", "primary-text", "transparent", "transparent", "transparent", focus_border="transparent", c=c)
    out += f'Button[variant="text"] {{ padding: 0 4px; }}\nButton[variant="text"]:hover {{ color: {c.primary}; }}\nButton[variant="text"]:disabled {{ background: transparent; }}\n'
    out += _variant('Button[variant="danger"]', c.error, "on-error", "transparent", c.error_hover, c.error_pressed, focus_border="transparent", c=c)
    out += f'Button[variant="danger"]:disabled {{ background: {c.control_disabled}; }}\n'
    out += f"""
Button[splitPart="main"] {{ border-top-right-radius: 0; border-bottom-right-radius: 0; }}
Button[splitPart="arrow"] {{ border-top-left-radius: 0; border-bottom-left-radius: 0; margin-left: 1px; }}
SegmentedControl {{ background: {c.surface_tertiary}; border-radius: {x.r('md')}; }}
SegmentedControl QPushButton {{ background: transparent; border: none; border-radius: {x.r('sm')}; padding: 0 8px;
    min-height: {x.h('small', 0)}; color: {c.text_secondary}; {x.font('button')} outline: none; }}
SegmentedControl QPushButton:hover {{ color: {c.text_primary}; }}
SegmentedControl QPushButton:focus {{ border: 2px solid {c.border_focus}; padding: 0 6px; }}
SegmentedControl QPushButton:checked {{ background: {c.surface_elevated}; color: {c.primary_text}; font-weight: 600; }}
SegmentedControl QPushButton:disabled {{ color: {c.text_disabled}; }}
"""
    return out
