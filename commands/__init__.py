# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2022-2026 IMA LLC

from .assigndrawingnumber import entry as assigndrawingnumber
from .assignpartnumbers import entry as assignpartnumbers
from .autosave import entry as autosave
from .changeactivecolor import entry as changeactivecolor
from .datatoggle import entry as datatoggle
from .defaultfolders import entry as defaultfolders
from .dochistory import entry as dochistory
from .docinfo import entry as docinfo
from .docopen import entry as docopen
from .favorites import entry as favorites

# from .opendwg import entry as opendwg # Not ready for use
from .versiondiff import entry as versiondiff
from .versionmerge import entry as versionmerge

from ..lib import fusionAddInUtils as futil

# Fusion will automatically call the start() and stop() functions.
commands = [
    assigndrawingnumber,
    assignpartnumbers,
    autosave,
    changeactivecolor,
    datatoggle,
    defaultfolders,
    dochistory,
    docinfo,
    docopen,
    favorites,
    # opendwg,
    versiondiff,
    versionmerge,
]


# Assumes you defined a "start" function in each of your modules.
# The start function will be run when the add-in is started.
def start():
    for command in commands:
        try:
            command.start()
        except Exception:
            futil.handle_error(command.__name__)


# Assumes you defined a "stop" function in each of your modules.
# The stop function will be run when the add-in is stopped.
def stop():
    for command in commands:
        try:
            command.stop()
        except Exception:
            futil.handle_error(command.__name__)
