# Handoff Workflow — Rule 051

This runbook describes how to prepare a handoff for a new Cursor chat session using the automated handoff preparation script.

## Overview

When starting a new chat in Cursor, you need to provide baseline evidence per **Rule 051 (Cursor Insight & Handoff)**. The `prepare_handoff.py` script automates this process by:

1. Collecting git repository information
2. Detecting active PR (if applicable)
3. Generating formatted handoff content
4. Copying to clipboard (if available)
5. Saving to `share/handoff_latest.md` for reference

## Usage

### Method 1: Cursor Team Command (Recommended)

1. In Cursor, open the command palette (Cmd/Ctrl + Shift + P)
2. Type "Cursor: Run Team Command"
3. Select `handoff`
4. The handoff content will be copied to your clipboard
5. Open a new chat tab (Cmd/Ctrl + L, then click "New Chat")
6. Paste the handoff content (Cmd/Ctrl + V)

### Method 2: Makefile Target

```bash
make handoff.prepare
```

Then follow steps 4-6 above.

### Method 3: Direct Script Execution

```bash
python3 scripts/prepare_handoff.py
```

Then follow steps 4-6 above.

## What Gets Included

The handoff includes:

1. **Repository Information**
   - Git root directory
   - Current branch
   - Git status

2. **Hermetic Test Bundle** (commands to run)
   - `ruff format --check . && ruff check .`
   - `make book.smoke`
   - `make ci.exports.smoke`

3. **Active PR Information** (if on a PR branch)
   - PR number, title, branches
   - Commands to check PR status and required checks

4. **Next Steps**
   - Instructions for the new chat session

## Clipboard Support

The script attempts to copy to clipboard using:

- **macOS**: `pbcopy`
- **Linux**: `xclip` or `xsel` (if available)
- **Windows**: `clip`
- **Python**: `pyperclip` (if installed)

If clipboard copy fails, the content will be:
- Printed to stdout
- Saved to `share/handoff_latest.md`

## Installing Clipboard Support (Optional)

For better clipboard support on Linux, install one of:

```bash
# Ubuntu/Debian
sudo apt-get install xclip

# or
sudo apt-get install xsel

# Or install pyperclip (works across platforms)
pip install pyperclip
```

## Integration with Cursor

The handoff command is registered in `tools/cursor/team_commands.json`:

```json
{
  "name": "handoff",
  "desc": "Prepare Rule 051 handoff for new chat (copies to clipboard)",
  "shell": "python3 scripts/prepare_handoff.py"
}
```

This makes it available as a Cursor Team Command.

## Workflow Example

```bash
# 1. Prepare handoff
make handoff.prepare

# Output:
# 🔄 Preparing handoff content (Rule 051)...
# ✅ Handoff content copied to clipboard!
# 💾 Handoff also saved to: share/handoff_latest.md

# 2. In Cursor:
#    - Press Cmd/Ctrl + L
#    - Click "New Chat"
#    - Press Cmd/Ctrl + V to paste
#    - The new chat now has full context
```

## Troubleshooting

### Clipboard not working

If clipboard copy fails:
1. Check the printed output in terminal
2. Or read `share/handoff_latest.md`
3. Manually copy the content

### PR not detected

If you're on a PR branch but it's not detected:
- Ensure `gh` CLI is installed and authenticated
- Check that the branch name matches a PR head branch
- The script will still work without PR info

### Script errors

If the script fails:
- Ensure you're in the repository root
- Check that `git` and `gh` commands are available
- Verify Python 3 is installed

## Related Rules

- **Rule 051**: Cursor Insight & Handoff (AlwaysApply)
- **Rule 050**: OPS Contract v6.2.3
- **Rule 053**: Idempotent Baseline

## See Also

- `.cursor/rules/051-cursor-insight.mdc`
- `AGENTS.md` — Cursor Execution Profile section
- `scripts/prepare_handoff.py` — Source code





