# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2022-2026 IMA LLC

import os
import os.path
import json

DEBUG = False
ADDIN_NAME = os.path.basename(os.path.dirname(__file__))
COMPANY_NAME = "IMA LLC"


design_workspace = "FusionSolidEnvironment"
tools_tab_id = "ToolsTab"
my_tab_name = "Power Tools"

my_panel_id = f"PT_{my_tab_name}"
my_panel_name = "Power Tools"
my_panel_after = ""

# ---------------------------------------------------------------------------
# Drawing workspace — target for commands that run inside a 2D drawing doc.
# FusionDocTab is a built-in Drawing-workspace tab, so we never create or
# delete it; we only add/remove our own PowerTools panel on it.
# ---------------------------------------------------------------------------
drawing_workspace = "FusionDocumentationEnvironment"
drawing_tab_id = "FusionDocTab"
drawing_panel_id = "PT_DrawingPowerTools"
drawing_panel_name = "Power Tools"
drawing_panel_after = ""

# ---------------------------------------------------------------------------
# Shared cache / settings paths
# ---------------------------------------------------------------------------

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
SETTINGS_FILE = os.path.join(CACHE_DIR, "settings.json")


def load_settings() -> dict:
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_settings(settings: dict) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


# ---------------------------------------------------------------------------
# Shared PowerTools Settings dropdown in the QAT file menu
# ---------------------------------------------------------------------------

PT_SETTINGS_DROPDOWN_ID = "PTSettings"
PT_SETTINGS_DROPDOWN_NAME = "PowerTools Settings"


