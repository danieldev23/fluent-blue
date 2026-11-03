"""Select, combo box, checkbox, radio, slider."""


def build(x) -> str:
    c = x.c
    return f"""
Select {{ background: {c.control}; border: 1px solid {c.border}; border-radius: {x.r('md')}; padding: 0 28px 0 10px;
    min-height: {x.h('medium')}; {x.font('body-medium')} selection-background-color: {c.selection}; selection-color: {c.selection_text}; }}
Select[fbSize="small"] {{ min-height: {x.h('small')}; {x.font('body-small')} padding-left: 8px; }}
Select[fbSize="large"] {{ min-height: {x.h('large')}; {x.font('body-large')} padding-left: 12px; }}
Select:hover {{ border-color: {c.border_strong}; }}
Select:focus, Select:on {{ border: 1px solid {c.border_focus}; }}
Select:disabled {{ background: {c.control_disabled}; color: {c.text_disabled}; border-color: {c.border_subtle}; }}
Select::drop-down {{ border: none; width: 26px; subcontrol-position: right center; subcontrol-origin: padding; }}
Select::down-arrow {{ image: url({x.asset('chevron-down', 'text-tertiary')}); width: 14px; height: 14px; }}
Select::down-arrow:disabled {{ image: url({x.asset('chevron-down', 'text-disabled')}); }}
Select QLineEdit {{ background: transparent; border: none; padding: 0; {x.font('body-medium')} }}
Select QAbstractItemView {{ background: {c.surface_elevated}; border: 1px solid {c.border}; border-radius: {x.r('md')}; padding: 4px;
    outline: none; selection-background-color: {c.selection}; selection-color: {c.selection_text}; }}
Select QAbstractItemView::item {{ min-height: 28px; padding: 0 8px; border-radius: {x.r('sm')}; }}
Select QAbstractItemView::item:hover {{ background: {c.ghost_hover}; }}
MultiSelect {{ background: {c.control}; border: 1px solid {c.border}; border-radius: {x.r('md')}; text-align: left; padding: 0 28px 0 10px;
    min-height: {x.h('medium')}; {x.font('body-medium')} outline: none; }}
MultiSelect:hover {{ border-color: {c.border_strong}; }}
MultiSelect:focus {{ border: 1px solid {c.border_focus}; }}
MultiSelect:disabled {{ background: {c.control_disabled}; color: {c.text_disabled}; border-color: {c.border_subtle}; }}
MultiSelect[empty="true"] {{ color: {c.text_tertiary}; }}
QCheckBox, QRadioButton {{ spacing: 8px; {x.font('body-medium')} }}
QCheckBox:disabled, QRadioButton:disabled {{ color: {c.text_disabled}; }}
QCheckBox::indicator, QRadioButton::indicator {{ width: 14px; height: 14px; background: {c.control}; border: 1px solid {c.border_strong}; }}
QCheckBox::indicator {{ border-radius: {x.r('xs')}; }}
QRadioButton::indicator {{ border-radius: 8px; }}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {{ border-color: {c.primary}; background: {c.primary_subtle}; }}
QCheckBox::indicator:focus, QRadioButton::indicator:focus {{ border: 2px solid {c.border_focus}; width: 12px; height: 12px; }}
QCheckBox::indicator:checked {{ background: {c.primary}; border-color: {c.primary}; image: url({x.asset('check', 'on-primary')}); }}
QCheckBox::indicator:checked:hover {{ background: {c.primary_hover}; border-color: {c.primary_hover}; }}
QCheckBox::indicator:indeterminate {{ background: {c.primary}; border-color: {c.primary}; image: url({x.asset('minus', 'on-primary')}); }}
QRadioButton::indicator:checked {{ background: qradialgradient(cx:.5, cy:.5, radius:.5, fx:.5, fy:.5, stop:0 {c.on_primary}, stop:.42 {c.on_primary}, stop:.5 {c.primary}, stop:1 {c.primary});
    border-color: {c.primary}; }}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{ background: {c.control_disabled}; border-color: {c.border}; }}
QListView::indicator {{ width: 14px; height: 14px; background: {c.control}; border: 1px solid {c.border_strong}; border-radius: {x.r('xs')}; margin-right: 6px; }}
QListView::indicator:hover {{ border-color: {c.primary}; }}
QListView::indicator:checked {{ background: {c.primary}; border-color: {c.primary}; image: url({x.asset('check', 'on-primary')}); }}
QSlider {{ min-height: 20px; }}
QFrame[popupPanel="true"] {{ background: {c.surface_elevated}; border: 1px solid {c.border}; border-radius: {x.r('lg')}; }}
QSlider::groove:horizontal {{ height: 4px; background: {c.surface_tertiary}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {c.primary}; border-radius: 2px; }}
QSlider::handle:horizontal {{ width: 14px; height: 14px; margin: -6px 0; background: {c.on_primary}; border: 2px solid {c.primary}; border-radius: 8px; }}
QSlider::groove:vertical {{ width: 4px; background: {c.surface_tertiary}; border-radius: 2px; }}
QSlider::add-page:vertical {{ background: {c.primary}; border-radius: 2px; }}
QSlider::handle:vertical {{ width: 14px; height: 14px; margin: 0 -6px; background: {c.on_primary}; border: 2px solid {c.primary}; border-radius: 8px; }}
QSlider::handle:hover {{ border-color: {c.primary_hover}; background: {c.primary_subtle}; }}
QSlider::handle:focus {{ border-color: {c.primary_900}; }}
QSlider::sub-page:horizontal:disabled, QSlider::add-page:vertical:disabled {{ background: {c.border_strong}; }}
QSlider::handle:disabled {{ border-color: {c.border_strong}; background: {c.control_disabled}; }}
"""
