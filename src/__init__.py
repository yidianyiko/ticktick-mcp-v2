# SPDX-License-Identifier: MIT
"""Top-level package initializer for ticktick-mcp-v2.

This file ensures that the `src` directory (i.e. this package's root) is on
`sys.path` so that modules can continue to import their siblings using absolute
imports such as ``import auth`` or ``import tools`` even when the package is
executed with ``python -m src.<module>``.

Background
----------
Running a module inside this directory via ``uv run ticktick-mcp`` executes the
``src`` package but **does not** automatically add the directory itself to
``sys.path``.  Consequently, top-level imports like ``import auth`` or
``import tools`` would fail because the interpreter searches the entries in
``sys.path`` for a top-level ``auth`` module.

By explicitly inserting the package directory into ``sys.path`` we guarantee
that these absolute imports resolve correctly regardless of the invocation
method (module execution, unit tests, interactive sessions, etc.).
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

# Absolute path to the directory that contains this file (the ``src`` package).
_pkg_dir = _Path(__file__).resolve().parent

# Prepend the directory to ``sys.path`` if it is not already present.
if str(_pkg_dir) not in _sys.path:
    _sys.path.insert(0, str(_pkg_dir))

# Clean up internal names so they are not exposed when using ``from src import *``
# (though wildcard imports are discouraged).
del _sys, _Path, _pkg_dir
