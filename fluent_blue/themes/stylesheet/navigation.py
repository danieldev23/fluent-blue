"""Sidebar, top bar, breadcrumb, tabs, pagination, command palette."""


def build(x) -> str:
    c = x.c
    return f"""
Sidebar {{ background: {c.surface}; border-right: 1px solid {c.border_subtle}; }}
QLabel[sidebarSection="true"] {{ color: {c.text_tertiary}; {x.font('caption')} font-weight: 600; padding: 12px 10px 4px 10px; }}
SidebarItem {{ background: transparent; border: 2px solid transparent; border-radius: {x.r('md')}; padding: 0 8px; text-align: left;
    min-height: {x.h('medium', 4)}; color: {c.text_secondary}; {x.font('body-medium')} outline: none; }}
SidebarItem:hover {{ background: {c.ghost_hover}; color: {c.text_primary}; }}
SidebarItem:pressed {{ background: {c.ghost_pressed}; }}
SidebarItem:focus {{ border-color: {c.border_focus}; }}
SidebarItem:checked {{ background: {c.primary_subtle}; color: {c.primary_text}; font-weight: 600; }}
SidebarItem:disabled {{ color: {c.text_disabled}; }}
Sidebar[tone="brand"] {{ border: none; background: qlineargradient(x1:0, y1:0, x2:.4, y2:1, stop:0 {c.primary_700}, stop:.55 {c.primary}, stop:1 {c.primary_700}); }}
Sidebar[tone="brand"] QLabel[sidebarSection="true"] {{ color: {c.brand_text_muted}; }}
Sidebar[tone="brand"] SidebarItem {{ color: {c.brand_text_muted}; min-height: 26px; }}
Sidebar[tone="brand"] SidebarItem:hover {{ background: {c.brand_fill_hover}; color: {c.brand_text}; }}
Sidebar[tone="brand"] SidebarItem:pressed {{ background: {c.brand_fill_active}; }}
Sidebar[tone="brand"] SidebarItem:focus {{ border-color: {c.brand_text}; }}
Sidebar[tone="brand"] SidebarItem:checked {{ background: {c.brand_fill_active}; color: {c.brand_text}; }}
Sidebar[tone="brand"] QScrollBar::handle {{ background: {c.brand_fill_active}; }}
NavigationBar {{ background: {c.surface}; border-bottom: 1px solid {c.border_subtle}; }}
NavigationBar QLabel[navTitle="true"] {{ {x.font('heading-5')} }}
Breadcrumb QPushButton {{ background: transparent; border: none; padding: 0 2px; color: {c.text_tertiary}; {x.font('body-medium')} outline: none; }}
Breadcrumb QPushButton:hover {{ color: {c.primary_text}; }}
Breadcrumb QPushButton:focus {{ color: {c.primary_text}; text-decoration: underline; }}
Breadcrumb QLabel[current="true"] {{ color: {c.text_primary}; {x.font('body-medium')} font-weight: 500; }}
QTabWidget::pane {{ border: none; border-top: 1px solid {c.border_subtle}; }}
QTabWidget::tab-bar {{ left: 0; }}
TabBar {{ background: transparent; qproperty-drawBase: 0; outline: none; }}
TabBar::tab {{ background: transparent; color: {c.text_secondary}; padding: 8px 12px; margin-right: 4px; border: none;
    border-bottom: 2px solid transparent; {x.font('body-medium')} }}
TabBar::tab:hover {{ color: {c.text_primary}; border-bottom-color: {c.border_strong}; }}
TabBar::tab:selected {{ color: {c.primary_text}; border-bottom-color: {c.primary}; font-weight: 600; }}
TabBar::tab:focus {{ background: {c.primary_subtle}; }}
TabBar::tab:disabled {{ color: {c.text_disabled}; }}
TabBar::close-button {{ image: url({x.asset('close', 'text-tertiary')}); subcontrol-position: right; }}
Pagination QPushButton {{ background: transparent; border: 1px solid transparent; border-radius: {x.r('md')}; min-width: 28px; min-height: 26px;
    padding: 0 4px; color: {c.text_secondary}; {x.font('body-medium')} outline: none; }}
Pagination QPushButton:hover {{ background: {c.ghost_hover}; color: {c.text_primary}; }}
Pagination QPushButton:focus {{ border-color: {c.border_focus}; }}
Pagination QPushButton:checked {{ background: {c.primary}; color: {c.on_primary}; font-weight: 600; }}
Pagination QPushButton:disabled {{ background: transparent; color: {c.text_disabled}; }}
Pagination QLabel {{ color: {c.text_tertiary}; {x.font('body-small')} }}
CommandPalette QFrame#panel {{ background: {c.surface_elevated}; border: 1px solid {c.border}; border-radius: {x.r('xl')}; }}
CommandPalette QLineEdit {{ background: transparent; border: none; border-bottom: 1px solid {c.border_subtle}; padding: 14px 16px; {x.font('body-large')} }}
CommandPalette QListView {{ padding: 6px; }}
CommandPalette QLabel#hint {{ color: {c.text_tertiary}; {x.font('caption')} padding: 6px 16px; border-top: 1px solid {c.border_subtle}; }}
"""
