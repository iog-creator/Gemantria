#!/bin/bash
# Auto-activate Gemantria virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating Gemantria virtual environment..."
    source .venv/bin/activate
    echo "Virtual environment active: $VIRTUAL_ENV"
else
    echo "Virtual environment already active: $VIRTUAL_ENV"
fi
