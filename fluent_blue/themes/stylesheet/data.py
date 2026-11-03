"""DataTable and advanced data widgets."""


def build(x) -> str:
    c = x.c
    return f"""
DataTable {{ background: {c.surface}; border: 1px solid {c.border_subtle}; border-radius: {x.r('lg')}; }}
DataTable QFrame#toolbar {{ background: transparent; border-bottom: 1px solid {c.border_subtle}; }}
DataTable QFrame#footer {{ background: transparent; border-top: 1px solid {c.border_subtle}; }}
CodeEditor {{ {x.font('monospace')} {x.mono()} padding: 0; }}
LogViewer, RichTextEditor, ImageViewer {{ background: {c.surface}; border: 1px solid {c.border}; border-radius: {x.r('md')}; }}
LogViewer QPlainTextEdit {{ border: none; border-top: 1px solid {c.border_subtle}; background: transparent; padding: 6px 8px; {x.font('monospace')} {x.mono()} }}
RichTextEditor RichTextArea {{ border: none; border-top: 1px solid {c.border_subtle}; border-radius: 0; background: transparent; }}
RichTextEditor RichTextArea:focus {{ border: none; border-top: 1px solid {c.border_focus}; padding: 6px 8px; }}
TreeView, FileTree {{ background: {c.surface}; border: 1px solid {c.border_subtle}; border-radius: {x.r('md')}; padding: 4px; }}
TreeView:focus, FileTree:focus {{ border-color: {c.border_focus}; }}
ImageViewer QGraphicsView {{ border: none; border-top: 1px solid {c.border_subtle}; background: {c.surface_tertiary}; }}
PickerPopup {{ background: {c.surface_elevated}; border: 1px solid {c.border}; border-radius: {x.r('lg')}; }}
TimePopup QListWidget {{ background: transparent; {x.font('body-medium')} }}
"""
