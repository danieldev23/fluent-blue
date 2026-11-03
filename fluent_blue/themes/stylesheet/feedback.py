"""Alerts, toasts, dialogs, overlays, drawers."""


def build(x) -> str:
    c = x.c
    out = f"""
Alert {{ border-radius: {x.r('md')}; border: 1px solid {c.border}; }}
Alert QLabel {{ background: transparent; border: none; }}
Alert QLabel#alertTitle {{ {x.font('heading-5')} }}
Alert QLabel#alertMessage {{ {x.font('body-medium')} color: {c.text_secondary}; }}
Alert[dense="true"] QLabel#alertMessage {{ {x.font('body-small')} }}
ToastCard {{ background: {c.surface_elevated}; border: 1px solid {c.border}; border-radius: {x.r('lg')}; }}
ToastCard QLabel {{ background: transparent; border: none; }}
ToastCard QLabel#toastTitle {{ {x.font('heading-5')} }}
ToastCard QLabel#toastMessage {{ {x.font('body-medium')} color: {c.text_secondary}; }}
ToastCard[kind="snackbar"] {{ background: {c.gray_900}; border-color: {c.gray_700}; }}
ToastCard[kind="snackbar"] QLabel#toastMessage {{ color: {c.gray_0}; }}
ToastCard[kind="snackbar"] Button[variant="text"] {{ color: {c.primary_300}; }}
ToastCard[kind="snackbar"] Button[variant="text"]:hover {{ color: {c.primary_200}; }}
QFrame#modalPanel, Drawer {{ background: {c.surface_elevated}; border: 1px solid {c.border_subtle}; }}
QFrame#modalPanel {{ border-radius: {x.r('xl')}; }}
QFrame#modalPanel QLabel#modalTitle, Drawer QLabel#modalTitle {{ {x.font('heading-3')} }}
QFrame#modalFooter {{ background: transparent; border-top: 1px solid {c.border_subtle}; }}
ModalScrim, DrawerScrim {{ background: {c.surface_overlay}; }}
LoadingOverlay QLabel {{ color: {c.text_secondary}; background: transparent; {x.font('body-medium')} }}
ScrollArea {{ background: transparent; border: none; }}
"""
    for name in ("success", "warning", "error", "info"):
        out += f'Alert[variant="{name}"] {{ background: {c[name + "-subtle"]}; border-color: {c[name + "-border"]}; }}\n'
    return out
