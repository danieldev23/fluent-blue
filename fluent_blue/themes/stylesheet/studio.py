"""Design Studio chrome. Library components never depend on these rules."""


def build(x) -> str:
    c = x.c
    return f"""
StudioRoot {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {c.background}, stop:1 {c.surface_tertiary}); }}
BentoCard {{ background: {c.surface}; border: 1px solid {c.border_subtle}; border-radius: {x.r('xl')}; }}
BentoCard QLabel#bentoTitle {{ {x.font('heading-5')} }}
HeroCard {{ border: 1px solid {c.border_subtle}; border-radius: {x.r('xl')}; }}
PromoCard {{ border: 1px solid {c.brand_border}; border-radius: {x.r('xl')}; }}
QLabel#versionPill {{ color: {c.brand_text}; background: transparent; border: 1px solid {c.brand_border};
    border-radius: 11px; padding: 2px 10px; min-height: 16px; {x.font('caption')} }}
Button[pill="true"] {{ border-radius: 14px; }}
HeroCard Button[pill="true"] {{ border-radius: 20px; }}
HeroCard Button[feature="true"] {{ text-align: left; {x.font('body-medium')} padding: 2px 8px; min-height: 40px; color: {c.text_primary}; }}
QPushButton#searchPill {{ background: {c.surface}; border: 1px solid {c.border}; border-radius: 19px; min-height: 36px; padding: 0 16px;
    text-align: left; color: {c.text_tertiary}; {x.font('body-medium')} outline: none; }}
QPushButton#searchPill:hover {{ border-color: {c.primary}; }}
QPushButton#searchPill:focus {{ border: 2px solid {c.border_focus}; }}
QFrame[heroAccent="true"] {{ background: {c.primary}; border-radius: 1px; }}
QFrame[topbarDivider="true"] {{ background: {c.border}; }}
Sidebar[embedded="true"] {{ background: transparent; border: none; border-right: 1px solid {c.border_subtle}; }}
SwatchTile, GradientTile, ThemeTile, ScaleBar {{ background: transparent; }}
QListWidget#iconGrid::item {{ border-radius: {x.r('md')}; padding: 8px; }}
"""
