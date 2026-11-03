#!/usr/bin/env bash
cd "$(dirname "$0")"
PYTHONPATH=. .venv-pyqt/bin/python -m fluent_blue.studio.app
