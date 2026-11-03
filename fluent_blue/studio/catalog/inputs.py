from . import Entry

G = "Inputs"
ENTRIES = [
    Entry("Input", G, '''
from fluent_blue import Grid, Input

demo = Grid(columns=2, gap=2)
demo.add(Input(placeholder="Your name", prefix_icon="user"))
demo.add(Input("Read-only value", read_only=True))
demo.add(Input("Looks good", validation="success", suffix_icon="check"))
demo.add(Input("Not valid", validation="error"))
demo.add(Input(placeholder="Small", size="small"))
demo.add(Input(placeholder="Large", size="large"))
demo.add(Input("Disabled", disabled=True))
demo.add(Input(placeholder="https://", prefix_icon="link", clearable=True))
''', ["Wrap in FormField to add a label and messages.", "Placeholders are hints; they never replace a label."]),
    Entry("PasswordInput", G, '''
from fluent_blue import PasswordInput

demo = PasswordInput("correct horse battery")
''', ["Let people reveal what they typed; it reduces errors.", "Never pre-fill a real password."]),
    Entry("SearchInput", G, '''
from fluent_blue import SearchInput

demo = SearchInput(placeholder="Search projects…", debounce_ms=250)
''', ["Connect to search_changed rather than textChanged, to avoid a query on each keystroke."]),
    Entry("NumberInput", G, '''
from fluent_blue import NumberInput

demo = NumberInput(12.5, minimum=0, maximum=100, step=0.5, decimals=1)
''', ["Set realistic bounds; the value is clamped on commit.", "Up and Down arrow keys step the value."]),
    Entry("TextArea", G, '''
from fluent_blue import TextArea

demo = TextArea(placeholder="Describe the issue…", max_length=280, rows=3)
''', ["Size it for the expected answer length; the box height is a hint to the user."]),
    Entry("ClearableInput", G, '''
from fluent_blue import ClearableInput

demo = ClearableInput("Clear me", placeholder="Type something")
''', ["Useful for filters and any value people often replace entirely."]),
    Entry("InputGroup", G, '''
from fluent_blue import Button, Input, InputGroup, Stack

demo = Stack([
    InputGroup(Input("my-project"), prefix="https://", suffix=".example.com"),
    InputGroup(Input(placeholder="Amount"), prefix="$"),
], spacing=2)
''', ["Use addons for units and fixed affixes, so they are not typed by mistake."]),
    Entry("FormField", G, '''
from fluent_blue import FormField, Input, Stack

def check_email(value):
    return None if "@" in value else "Enter a valid email address."

email = FormField("Work email", Input(placeholder="name@company.com"), required=True,
                  helper="Used for sign-in only.", validator=check_email)
email.validate()
name = FormField("Display name", Input("Ada Lovelace"), helper="Shown to your team.")
demo = Stack([email, name], spacing=4)
''', ["Validate when the field loses focus, not on each keystroke.", "Say how to fix the problem, not just that one exists."]),
]
