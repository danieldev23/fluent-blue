"""Native Qt widgets: windows, scrollbars, tooltips, menus, views, splitters."""


def build(x) -> str:
    c = x.c
    return f"""
QMainWindow, QDialog {{ background: {c.background}; }}
Modal {{ background: transparent; border: none; }}
QWidget {{ color: {c.text_primary}; }}
QWidget:disabled {{ color: {c.text_disabled}; }}
QToolTip {{ background: {c.surface_elevated}; color: {c.text_primary}; border: 1px solid {c.border};
    border-radius: {x.r('sm')}; padding: 4px 8px; {x.font('body-small')} }}
QAbstractScrollArea {{ background: transparent; border: none; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 0; }}
QScrollBar::handle {{ background: {c.scrollbar}; border-radius: 3px; margin: 2px; }}
QScrollBar::handle:vertical {{ min-height: 28px; }}
QScrollBar::handle:horizontal {{ min-width: 28px; }}
QScrollBar::handle:hover {{ background: {c.scrollbar_hover}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; background: none; border: none; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
QAbstractScrollArea::corner {{ background: transparent; }}
QSplitter::handle {{ background: {c.border_subtle}; }}
QSplitter::handle:hover {{ background: {c.primary}; }}
QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:vertical {{ height: 1px; }}
QHeaderView {{ background: {c.surface_secondary}; border: none; }}
QHeaderView::section {{ background: {c.surface_secondary}; color: {c.text_secondary}; border: none;
    border-bottom: 1px solid {c.border}; border-right: 1px solid {c.border_subtle};
    padding: 0 10px; min-height: 34px; {x.font('label')} }}
QHeaderView::section:hover {{ background: {c.surface_tertiary}; color: {c.text_primary}; }}
QHeaderView::down-arrow {{ image: url({x.asset('arrow-down', 'text-secondary')}); width: 12px; height: 12px; right: 6px; }}
QHeaderView::up-arrow {{ image: url({x.asset('arrow-up', 'text-secondary')}); width: 12px; height: 12px; right: 6px; }}
QTableView {{ background: {c.surface}; alternate-background-color: {c.surface_secondary};
    gridline-color: {c.border_subtle}; selection-background-color: {c.selection};
    selection-color: {c.selection_text}; outline: none; border: none; }}
QTableView::item {{ padding: 0 10px; border-bottom: 1px solid {c.border_subtle}; }}
QTableView::item:hover {{ background: {c.control_hover}; }}
QTableView::item:selected {{ background: {c.selection}; color: {c.selection_text}; }}
QListView, QTreeView {{ background: transparent; outline: none; border: none;
    selection-background-color: {c.selection}; selection-color: {c.selection_text}; }}
QListView::item, QTreeView::item {{ min-height: 28px; border-radius: {x.r('sm')}; padding: 0 4px; }}
QListView::item:hover, QTreeView::item:hover {{ background: {c.ghost_hover}; }}
QListView::item:selected, QTreeView::item:selected {{ background: {c.selection}; color: {c.selection_text}; }}
QTreeView::branch {{ background: transparent; }}
QTreeView::branch:has-children:closed {{ image: url({x.asset('chevron-right', 'text-tertiary')}); }}
QTreeView::branch:has-children:open {{ image: url({x.asset('chevron-down', 'text-tertiary')}); }}
QMenu {{ background: {c.surface_elevated}; border: 1px solid {c.border}; border-radius: {x.r('lg')}; padding: 4px; }}
QMenu::item {{ padding: 6px 28px 6px 10px; border-radius: {x.r('sm')}; {x.font('body-medium')} color: {c.text_primary}; }}
QMenu::item:selected {{ background: {c.ghost_hover}; }}
QMenu::item:disabled {{ color: {c.text_disabled}; background: transparent; }}
QMenu::icon {{ padding-left: 10px; }}
QMenu::separator {{ height: 1px; background: {c.border_subtle}; margin: 4px 6px; }}
QMenu::right-arrow {{ image: url({x.asset('chevron-right', 'text-tertiary')}); width: 12px; height: 12px; right: 8px; }}
QMenu::indicator {{ width: 14px; height: 14px; left: 6px; }}
QMenu::indicator:checked {{ image: url({x.asset('check', 'primary-text')}); }}

/* FluentWindow & Custom TitleBar */
QWidget[fbComponent="fluentWindow"] {{
    background: {c.surface};
    border: 1px solid {c.border};
}}
QWidget[fbComponent="titleBar"] {{
    background: {c.surface_secondary};
    border-bottom: 1px solid {c.border_subtle};
}}
QWidget[fbComponent="titleBar"] QLabel {{
    color: {c.text_primary};
}}
QToolButton[winBtn="min"], QToolButton[winBtn="max"] {{
    background: transparent;
    border: none;
}}
QToolButton[winBtn="min"]:hover, QToolButton[winBtn="max"]:hover {{
    background: {c.ghost_hover};
}}
QToolButton[winBtn="close"] {{
    background: transparent;
    border: none;
}}
QToolButton[winBtn="close"]:hover {{
    background: #E81123;
}}
"""
