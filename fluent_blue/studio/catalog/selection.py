from . import Entry

G = "Selection"
ENTRIES = [
    Entry("Select", G, '''
from fluent_blue import Select, Stack

demo = Stack([
    Select(["Design", "Engineering", "Marketing"], placeholder="Choose a team"),
    Select([("Weekly", 7), ("Monthly", 30)], value=30),
    Select(["Disabled"], disabled=True),
], direction="horizontal")
''', ["Prefer it over radio buttons when there are more than five options."]),
    Entry("MultiSelect", G, '''
from fluent_blue import MultiSelect

demo = MultiSelect(["Python", "Rust", "Go", "TypeScript"], values=["Python", "Rust"], placeholder="Languages")
''', ["The label collapses to a count, so the control keeps its width."]),
    Entry("ComboBox", G, '''
from fluent_blue import ComboBox

demo = ComboBox(["Amsterdam", "Berlin", "Copenhagen", "Dublin", "Hanoi"], placeholder="Type a city…")
''', ["Use when free text is valid or the list is long enough to need search."]),
    Entry("Checkbox", G, '''
from fluent_blue import Checkbox, Stack

demo = Stack([
    Checkbox("Email me product updates", checked=True),
    Checkbox("Partly selected", indeterminate=True),
    Checkbox("Unchecked"),
    Checkbox("Disabled", disabled=True),
])
''', ["Use for independent choices that are applied together, such as in a form."]),
    Entry("RadioButton", G, '''
from fluent_blue import RadioButton, Stack

demo = Stack([RadioButton("Standalone", checked=True), RadioButton("Disabled", disabled=True)])
''', ["Most of the time RadioGroup is what you want."]),
    Entry("RadioGroup", G, '''
from fluent_blue import RadioGroup

demo = RadioGroup([("Comfortable", "comfortable"), ("Compact", "compact"), ("Spacious", "spacious")],
                  value="compact", orientation="horizontal")
''', ["Show all options at once when comparison matters and there are few."]),
    Entry("Switch", G, '''
from fluent_blue import Stack, Switch

demo = Stack([Switch("Enable sync", checked=True), Switch("Dark sidebar"), Switch("Disabled", disabled=True)])
''', ["A switch takes effect immediately; use a Checkbox if a Save button follows."]),
    Entry("SegmentedControl", G, '''
from fluent_blue import SegmentedControl

demo = SegmentedControl(["Day", "Week", "Month", "Year"], value="Week")
''', ["Ideal for switching views of the same content; keep to about five options."]),
    Entry("Slider", G, '''
from fluent_blue import Slider, Stack

demo = Stack([Slider(40), Slider(70, disabled=True)], spacing=3)
''', ["Use when the approximate value matters; use NumberInput for exact values."]),
    Entry("SpinBox", G, '''
from fluent_blue import SpinBox

demo = SpinBox(16, minimum=8, maximum=72, suffix=" px")
''', ["Add a suffix so that the unit is never ambiguous."]),
]
