#!/usr/bin/env bash

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Run this script with: source _uv_active.sh"
    echo "Direct execution cannot activate the virtual environment in your current shell."
    exit 1
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/riot_database_3_14_2/bin/activate"
