"""Text inputs, spin boxes, tags, otp and input groups."""


def build(x) -> str:
    c = x.c
    out = f"""
Input, SpinBox {{ background: {c.control}; border: 1px solid {c.border}; border-radius: {x.r('md')};
    padding: 0 10px; min-height: {x.h('medium')}; {x.font('body-medium')}
    selection-background-color: {c.selection}; selection-color: {c.selection_text}; }}
Input[fbSize="small"] {{ min-height: {x.h('small')}; padding: 0 8px; {x.font('body-small')} }}
Input[fbSize="large"] {{ min-height: {x.h('large')}; padding: 0 12px; {x.font('body-large')} }}
Input:hover, SpinBox:hover {{ border-color: {c.border_strong}; }}
Input:focus, SpinBox:focus {{ border: 2px solid {c.border_focus}; padding: 0 9px; }}
Input[fbSize="small"]:focus {{ padding: 0 7px; }}
Input[fbSize="large"]:focus {{ padding: 0 11px; }}
Input[specimen="hover"] {{ border-color: {c.border_strong}; }}
Input[specimen="focus"] {{ border: 2px solid {c.border_focus}; padding: 0 9px; }}
Input:read-only {{ background: {c.surface_tertiary}; color: {c.text_secondary}; }}
Input:disabled, SpinBox:disabled {{ background: {c.control_disabled}; color: {c.text_disabled}; border-color: {c.border_subtle}; }}
TextArea, CodeEditor, RichTextArea {{ background: {c.control}; border: 1px solid {c.border}; border-radius: {x.r('md')};
    padding: 6px 8px; {x.font('body-medium')} selection-background-color: {c.selection}; selection-color: {c.selection_text}; }}
TextArea:hover {{ border-color: {c.border_strong}; }}
TextArea:focus, RichTextArea:focus {{ border: 2px solid {c.border_focus}; padding: 5px 7px; }}
TextArea:disabled {{ background: {c.control_disabled}; color: {c.text_disabled}; border-color: {c.border_subtle}; }}
TextArea:read-only {{ background: {c.surface_tertiary}; color: {c.text_secondary}; }}

/* TagInput Styling */
QWidget[fbComponent="tagInput"] {{
    background: {c.control};
    border: 1px solid {c.border};
    border-radius: {x.r('md')};
    min-height: {x.h('medium')};
}}
QWidget[fbComponent="tagInput"]:hover {{
    border-color: {c.border_strong};
}}
QWidget[fbComponent="tagInput"] QLineEdit {{
    border: none;
    background: transparent;
    padding: 0 4px;
    color: {c.text_primary};
    {x.font('body-medium')}
}}
QWidget[fbComponent="tagBadge"] {{
    background: {c.surface_tertiary};
    border: 1px solid {c.border_subtle};
    border-radius: {x.r('sm')};
}}
QWidget[fbComponent="tagBadge"] QToolButton {{
    border: none;
    background: transparent;
    padding: 0;
}}
QWidget[fbComponent="tagBadge"] QToolButton:hover {{
    background: {c.ghost_hover};
    border-radius: 2px;
}}
"""
    for state, role in (("error", "error"), ("warning", "warning"), ("success", "success")):
        out += f"""
Input[validation="{state}"], TextArea[validation="{state}"] {{ border-color: {c[role]}; }}
Input[validation="{state}"]:hover, TextArea[validation="{state}"]:hover {{ border-color: {c[role + '-hover']}; }}
Input[validation="{state}"]:focus, TextArea[validation="{state}"]:focus {{ border-color: {c[role]}; }}
FieldMessage[state="{state}"] {{ color: {c[role + '-text']}; }}
"""
    out += f"""
FieldMessage {{ color: {c.text_tertiary}; {x.font('body-small')} }}
FieldLabel {{ color: {c.text_primary}; {x.font('label')} }}
InputGroup {{ background: {c.control}; border: 1px solid {c.border}; border-radius: {x.r('md')}; }}
InputGroup[focused="true"] {{ border: 1px solid {c.border_focus}; }}
InputGroup Input {{ border: none; background: transparent; border-radius: 0; min-height: {x.h('medium')}; }}
InputGroup Input:focus {{ border: none; padding: 0 10px; }}
InputGroup QLabel[addon="true"] {{ background: {c.surface_tertiary}; color: {c.text_secondary}; padding: 0 10px; {x.font('body-medium')} }}
InputGroup QLabel[addon="true"][side="start"] {{ border-right: 1px solid {c.border}; border-top-left-radius: {x.r('md')}; border-bottom-left-radius: {x.r('md')}; }}
InputGroup QLabel[addon="true"][side="end"] {{ border-left: 1px solid {c.border}; border-top-right-radius: {x.r('md')}; border-bottom-right-radius: {x.r('md')}; }}
SpinBox::up-button, SpinBox::down-button {{ width: 22px; border: none; background: transparent; subcontrol-origin: border; }}
SpinBox::up-button {{ subcontrol-position: top right; }}
SpinBox::down-button {{ subcontrol-position: bottom right; }}
SpinBox::up-button:hover, SpinBox::down-button:hover {{ background: {c.ghost_hover}; }}
SpinBox::up-arrow {{ image: url({x.asset('chevron-up', 'text-secondary')}); width: 12px; height: 12px; }}
SpinBox::down-arrow {{ image: url({x.asset('chevron-down', 'text-secondary')}); width: 12px; height: 12px; }}
SpinBox {{ padding-right: 24px; }}
SpinBox:focus {{ padding-right: 23px; }}
"""
    return out
