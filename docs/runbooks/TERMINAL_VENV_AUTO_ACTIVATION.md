# Terminal Venv Auto-Activation

## Problem

The terminal shows duplicate `(.venv)` indicators (yellow) because the venv gets activated multiple times. You have to relaunch the terminal to get a clean state.

## Solution

### Option 1: Auto-Activation Script (Recommended)

Run the setup script to configure automatic venv activation:

```bash
cd /home/mccoy/Projects/Gemantria.v2
./scripts/setup_terminal_auto_venv.sh
```

This will:
- Add auto-activation to your `~/.bashrc` or `~/.zshrc`
- Auto-activate the venv when you `cd` into the project directory
- Prevent duplicate activations (no more yellow duplicates)

After running, restart your terminal or run:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### Option 2: direnv (Alternative)

If you use `direnv`, the `.envrc` file will auto-activate the venv:

```bash
# Install direnv first
# Then:
cd /home/mccoy/Projects/Gemantria.v2
direnv allow
```

### Quick Fix for Current Session

If you have duplicate venv indicators right now:

```bash
./scripts/fix_venv_prompt.sh
```

This will:
- Deactivate all venv instances
- Clean up the prompt
- Reactivate the venv properly (once)

## How It Works

The `auto_activate_venv.sh` script:
1. Checks if you're in the Gemantria project directory
2. Only activates if venv is NOT already active
3. Prevents duplicate activations that cause the yellow indicator issue

## Verification

After setup, verify it works:

```bash
# Open a new terminal
cd /home/mccoy/Projects/Gemantria.v2
# You should see: (.venv) in your prompt (only once, not multiple times)
echo $VIRTUAL_ENV
# Should show: /home/mccoy/Projects/Gemantria.v2/.venv
```

