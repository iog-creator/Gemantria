#!/usr/bin/env bash
# Filter Cursor IDE integration noise from stderr
# Suppresses "dump_bash_state: command not found" errors that confuse orchestrators

# Execute command and filter stderr
"$@" 2> >(grep -v "dump_bash_state: command not found" >&2)

