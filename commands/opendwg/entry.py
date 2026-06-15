# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2022-2026 IMA LLC
"""Open DWG — pick a .dwg file from disk and open it in the active
drawing via the Fusion text command:

    FusionDoc.ExecuteAcadCommand _.open "<path>"

The file dialog and the text command are both run from the command's
``destroy`` callback, which fires after the command lifecycle is fully
torn down. Calling either ``ui.createFileDialog().showOpen()`` or
``app.executeTextCommand`` from ``command_created`` or
``command_execute`` crashed Fusion (reentrancy into the command engine).
Likewise, ``args.command.doExecute(True)`` to skip the command panel
crashed Fusion immediately after returning. The destroy-deferred
pattern is the same one ``assigndrawingnumber`` uses to safely show its
post-execute messagebox.
"""

from __future__ import annotations

import os
import traceback

import adsk.core

from ... import config
from ...lib import fusionAddInUtils as futil


app = adsk.core.Application.get()
ui = app.userInterface

CMD_NAME = "Open DWG"
CMD_ID = "PTND-openDwg"
CMD_Description = (
    "Browse for a .dwg file on this computer and open it in the active "
    "drawing using FusionDoc.ExecuteAcadCommand _.open."
)
IS_PROMOTED = True

WORKSPACE_ID = config.drawing_workspace
TAB_ID = config.drawing_tab_id
PANEL_ID = config.drawing_panel_id
PANEL_NAME = config.drawing_panel_name
PANEL_AFTER = config.drawing_panel_after

ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "")

local_handlers: list = []


# ---------------------------------------------------------------------------
# Add-in lifecycle
# ---------------------------------------------------------------------------


def start():
    cmd_def = ui.commandDefinitions.addButtonDefinition(
        CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER
    )
    futil.add_handler(cmd_def.commandCreated, command_created)

    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    if workspace is None:
        futil.log(f"[{CMD_NAME}] Workspace {WORKSPACE_ID} not found at start()")
        return

    toolbar_tab = workspace.toolbarTabs.itemById(TAB_ID)
    if toolbar_tab is None:
        futil.log(
            f"[{CMD_NAME}] Tab '{TAB_ID}' not found on '{WORKSPACE_ID}' — "
            f"skipping UI registration."
        )
        return

    panel = toolbar_tab.toolbarPanels.itemById(PANEL_ID)
    if panel is None:
        panel = toolbar_tab.toolbarPanels.add(PANEL_ID, PANEL_NAME, PANEL_AFTER, False)

    control = panel.controls.addCommand(cmd_def)
    control.isPromoted = IS_PROMOTED

    futil.log(f"{CMD_NAME} command started")


def stop():
    try:
        workspace = ui.workspaces.itemById(WORKSPACE_ID)
        if not workspace:
            return

        toolbar_tab = workspace.toolbarTabs.itemById(TAB_ID)
        panel = toolbar_tab.toolbarPanels.itemById(PANEL_ID) if toolbar_tab else None
        command_control = panel.controls.itemById(CMD_ID) if panel else None
        command_definition = ui.commandDefinitions.itemById(CMD_ID)

        if command_control:
            command_control.deleteMe()
        if command_definition:
            command_definition.deleteMe()
        # Delete our panel when it's empty, but never touch FusionDocTab — it
        # is a native Fusion tab and belongs to the Drawing workspace.
        if panel and panel.controls.count == 0:
            panel.deleteMe()

        futil.log(f"{CMD_NAME} command stopped")
    except Exception as exc:
        futil.log(f"Error stopping {CMD_NAME}: {exc}")


# ---------------------------------------------------------------------------
# Command lifecycle — work runs in destroy, after the command is gone
# ---------------------------------------------------------------------------


def command_created(args: adsk.core.CommandCreatedEventArgs):
    """Set up the command. We add a brief instructional text-box input so
    the user understands what clicking OK will do, then wire execute (no-
    op) and destroy (does the real work) handlers.
    """
    futil.log(f"{CMD_NAME}: command_created — entered")
    try:
        cmd = args.command
        cmd.okButtonText = "Browse..."

        inputs = cmd.commandInputs
        info = inputs.addTextBoxCommandInput(
            "od_info",
            "",
            "Click <b>Browse...</b> to choose a <b>.dwg</b> file to open "
            "in the active drawing.",
            3, True,
        )
        info.isFullWidth = True

        futil.add_handler(cmd.execute, command_execute, local_handlers=local_handlers)
        futil.add_handler(cmd.destroy, command_destroy, local_handlers=local_handlers)
        futil.log(f"{CMD_NAME}: command_created — handlers registered")
    except Exception:
        futil.log(
            f"{CMD_NAME}: command_created raised:\n{traceback.format_exc()}",
            adsk.core.LogLevels.ErrorLogLevel,
        )


def command_execute(args: adsk.core.CommandEventArgs):
    """Intentionally empty. The real work runs in command_destroy, where
    modal UI and executeTextCommand are safe to call.
    """
    futil.log(f"{CMD_NAME}: command_execute — no-op (work deferred to destroy)")


def command_destroy(args: adsk.core.CommandEventArgs):
    """Fires after the command panel has closed and the command lifecycle
    is fully unwound. This is the safe context for modal UI and reentrant
    text commands — the same place assigndrawingnumber shows its
    deferred messagebox.
    """
    global local_handlers
    futil.log(f"{CMD_NAME}: command_destroy — entered")
    try:
        futil.log(f"{CMD_NAME}: creating file dialog (deferred)")
        dialog = ui.createFileDialog()
        dialog.title = "Select a DWG file to open"
        dialog.filter = "AutoCAD Drawing (*.dwg);;All Files (*.*)"
        dialog.isMultiSelectEnabled = False

        futil.log(f"{CMD_NAME}: about to call showOpen() (deferred)")
        result = dialog.showOpen()
        futil.log(f"{CMD_NAME}: showOpen() returned {result}")

        if result != adsk.core.DialogResults.DialogOK:
            futil.log(f"{CMD_NAME}: user cancelled file dialog")
            return

        path = dialog.filename
        futil.log(f"{CMD_NAME}: user selected path: {path!r}")

        # Escape embedded double quotes so the text command's quoted
        # argument stays intact even on unusual paths.
        safe_path = path.replace('"', r'\"')
        text_command = f'FusionDoc.ExecuteAcadCommand _.open "{safe_path}"'

        futil.log(
            f"{CMD_NAME}: about to executeTextCommand: {text_command!r}"
        )
        try:
            returned = app.executeTextCommand(text_command)
            futil.log(
                f"{CMD_NAME}: executeTextCommand returned: {returned!r}"
            )
        except Exception:
            futil.log(
                f"{CMD_NAME}: executeTextCommand raised:\n"
                f"{traceback.format_exc()}",
                adsk.core.LogLevels.ErrorLogLevel,
            )
    except Exception:
        futil.log(
            f"{CMD_NAME}: command_destroy raised:\n{traceback.format_exc()}",
            adsk.core.LogLevels.ErrorLogLevel,
        )
    finally:
        # Drop handler refs so they can be GC'd between invocations.
        local_handlers = []
