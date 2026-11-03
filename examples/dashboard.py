"""A dashboard: navigation bar, statistic cards, a timeline and a live log."""
from __future__ import annotations

from fluent_blue import (
    Avatar,
    Card,
    Grid,
    IconButton,
    LogViewer,
    NavigationBar,
    ScrollArea,
    SearchInput,
    Stack,
    StatisticCard,
    Text,
    ThemeManager,
    Timeline,
)
from fluent_blue.compatibility.qt import QApplication, QVBoxLayout, QWidget


def build() -> QWidget:
    window = QWidget()
    window.setWindowTitle("Dashboard")
    column = QVBoxLayout(window)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(0)

    bar = NavigationBar("Acme Console")
    bar.add_center(SearchInput(size="small"))
    theme = IconButton("moon", tooltip="Toggle theme")
    theme.clicked.connect(ThemeManager.toggle)
    bar.add_end(theme)
    bar.add_end(Avatar("Ada Lovelace", status="online"))
    column.addWidget(bar)

    content = Stack(spacing=4, padding=6)
    content.add(Text("Overview", style="heading-1"))
    stats = Grid(min_column_width=220)
    stats.add(StatisticCard("Revenue", "$48.2k", delta="+12.4%", trend="up", caption="vs last month", icon="chart-line",
                            spark=[3, 4, 3.6, 5, 4.8, 6, 7.2]))
    stats.add(StatisticCard("Active users", "2,840", delta="+3.1%", trend="up", caption="vs last week", icon="users",
                            spark=[6, 5.8, 6.2, 6, 6.4, 6.6, 6.5]))
    stats.add(StatisticCard("Error rate", "0.42%", delta="-0.08%", trend="down", caption="vs yesterday", icon="alert-triangle",
                            positive_is_up=False, spark=[5, 4.6, 4.8, 3.9, 3.2, 3.4, 2.9]))
    content.add(stats)

    lower = Grid(columns=2)
    activity = Card(title="Activity")
    activity.add(Timeline([
        {"title": "Build passed", "description": "All tests are green.", "time": "09:42", "variant": "success"},
        {"title": "Deploy started", "description": "Rolling out to production.", "time": "09:44"},
        {"title": "Latency warning", "description": "p95 rose above 400 ms.", "time": "09:51", "variant": "warning"},
    ]))
    lower.add(activity)
    log = LogViewer()
    for level, message in (("info", "Connected to database"), ("warning", "Slow query: 1840 ms"), ("error", "Cache write failed")):
        log.log(message, level)
    log.setMinimumHeight(220)
    lower.add(log)
    content.add(lower, 1)
    column.addWidget(ScrollArea(content), 1)
    window.resize(1100, 720)
    return window


def main() -> int:
    app = QApplication.instance() or QApplication([])
    ThemeManager.set_theme("light")
    window = build()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
