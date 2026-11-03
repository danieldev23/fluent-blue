"""Derive API documentation from component source, so the docs cannot drift from the code."""
from __future__ import annotations

import inspect
import re
from dataclasses import dataclass

from ..compatibility.qt import SignalTypes

_SECTION = re.compile(r"^\s*(Args|Attributes|Signals|Returns|Raises):\s*$")
_ITEM = re.compile(r"^\s*(\w+)(\([^)]*\))?:\s*(.*)$")


@dataclass
class Prop:
    name: str
    default: str
    description: str


@dataclass
class SignalDoc:
    name: str
    args: str
    description: str


_COMMON_DOCS = {
    "parent": "Parent widget.", "tooltip": "Tooltip text.", "disabled": "Start disabled.",
    "checkable": "Toggle between checked and unchecked on each click.",
}
# For helper classes whose docstrings do not list arguments.
_CLASS_DOCS = {
    "Command": {"id": "Value reported by command_triggered.", "title": "Main text.", "subtitle": "Secondary text.", "icon": "Icon name.",
                "keywords": "Extra search terms.", "action": "Callable run when the command is chosen."},
    "DataTableModel": {"columns": "Column objects or plain keys.", "rows": "A list of dicts.", "page_size": "Rows per page, or None for all."},
    "FloatingTooltip": {"text": "Tooltip text."},
    "SyntaxHighlighter": {"document": "The QTextDocument to highlight.", "language": "python, json, sql or text."},
    "TimePopup": {"minute_step": "Minute granularity."},
    "TitleBar": {"window": "The window this bar moves and controls.", "title": "Title text.", "icon_name": "Icon name shown before the title.",
                 "show_minimize": "Show the minimize button.", "show_maximize": "Show the maximize button.", "show_close": "Show the close button."},
    "ToastCard": {"title": "Bold first line.", "message": "Body text.", "variant": "info, success, warning or error; None hides the icon.",
                  "kind": "toast, notification or snackbar; sets the styling.", "duration": "Milliseconds before dismissal; 0 keeps it open.",
                  "action_text": "Action label.", "on_action": "Callable run when the action is used.", "closable": "Show a dismiss button."},
}


def clean_markup(text: str) -> str:
    """Reduce reStructuredText roles and literals to plain text."""
    text = re.sub(r":\w+:`~?([^`]+)`", lambda m: m.group(1).rsplit(".", 1)[-1], text)
    return text.replace("``", "")


def _sections(doc: str) -> dict[str, list[tuple[str, str, str]]]:
    sections: dict[str, list[tuple[str, str, str]]] = {}
    current = None
    for line in inspect.cleandoc(doc or "").splitlines():
        heading = _SECTION.match(line)
        if heading:
            current = sections.setdefault(heading.group(1), [])
            continue
        if current is None or not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        item = _ITEM.match(line)
        if item and indent <= 4:
            current.append((item.group(1), (item.group(2) or "").strip("()"), item.group(3)))
        elif current:
            name, args, text = current[-1]
            current[-1] = (name, args, f"{text} {line.strip()}")
    return sections


def _api_target(cls):
    """Static helpers such as ``Toast.show`` document their arguments on the method."""
    return cls.show if inspect.isfunction(inspect.getattr_static(cls, "show", None)) or isinstance(inspect.getattr_static(cls, "show", None), staticmethod) and not hasattr(cls, "metaObject") else cls.__init__


def properties(cls) -> list[Prop]:
    """Constructor parameters merged with their ``Args:`` documentation, through the MRO."""
    target = _api_target(cls)
    docs: dict[str, str] = {}
    for klass in reversed(cls.__mro__):
        if klass.__module__.startswith("fluent_blue"):
            sections = _sections(klass.__doc__)
            docs.update({n: d for n, _a, d in sections.get("Attributes", [])})
            docs.update({n: d for n, _a, d in sections.get("Args", [])})
    docs.update({n: d for n, _a, d in _sections(target.__doc__).get("Args", [])})
    result, seen = [], set()
    for klass in cls.__mro__:
        if not klass.__module__.startswith("fluent_blue"):
            continue
        if klass is not cls and klass.__name__.startswith("_"):
            continue  # Private bases take arguments that their public subclass already fills in.
        init = target if klass is cls else klass.__dict__.get("__init__")
        if init is None:
            continue
        has_var_kw = False
        for name, parameter in inspect.signature(init).parameters.items():
            if name == "self":
                continue
            if parameter.kind == parameter.VAR_KEYWORD:
                has_var_kw = True
                continue
            if parameter.kind == parameter.VAR_POSITIONAL or name in seen:
                continue
            seen.add(name)
            default = "required" if parameter.default is parameter.empty else repr(parameter.default)
            text = docs.get(name) or _CLASS_DOCS.get(cls.__name__, {}).get(name) or _COMMON_DOCS.get(name, "")
            result.append(Prop(name, default, clean_markup(text)))
        if not has_var_kw or target is not cls.__init__:
            break
    return result


def signals(cls) -> list[SignalDoc]:
    """Signals declared by Fluent Blue classes, with text from ``Signals:`` sections."""
    docs: dict[str, tuple[str, str]] = {}
    for klass in reversed(cls.__mro__):
        if klass.__module__.startswith("fluent_blue"):
            docs.update({n: (a, d) for n, a, d in _sections(klass.__doc__).get("Signals", [])})
    found = {}
    for klass in cls.__mro__:
        if not klass.__module__.startswith("fluent_blue"):
            continue
        for name, value in vars(klass).items():
            if isinstance(value, SignalTypes) and not name.startswith("_"):
                found.setdefault(name, None)
    return [SignalDoc(n, docs.get(n, ("", ""))[0], docs.get(n, ("", ""))[1]) for n in found]


def inherited_signals_note(cls) -> str:
    """Text of an ``Inherits ...`` line in the ``Signals:`` section, if any."""
    match = re.search(r"Inherits ([^\n]+(?:\n\s+[^\n:]+)*)", inspect.cleandoc(cls.__doc__ or ""))
    return " ".join(match.group(0).split()) if match else ""


def summary(cls) -> str:
    """First paragraph of the class docstring."""
    text = inspect.cleandoc(cls.__doc__ or "").split("\n\n")[0].replace("\n", " ")
    return clean_markup(text)


def declared_signal_names(widget) -> list[str]:
    """Signal attribute names declared by Fluent Blue classes for this instance."""
    names = []
    for klass in type(widget).__mro__:
        if klass.__module__.startswith("fluent_blue"):
            names += [n for n, v in vars(klass).items() if isinstance(v, SignalTypes) and not n.startswith("_")]
    return names
