#!/usr/bin/env bash
# filter_stderr.sh — Filter Cursor IDE integration noise from stderr
#
# Usage in bash scripts:
#   exec 2> >(grep -v "dump_bash_state: command not found" >&2 || true)
#
# Or filter a specific command:
#   command 2> >(grep -v "dump_bash_state: command not found" >&2 || true)

# Filter function for use in scripts
filter_cursor_noise() {
    grep -v "dump_bash_state: command not found" || true
}
