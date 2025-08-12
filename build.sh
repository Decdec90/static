#!/usr/bin/env bash
set -euo pipefail

# If given an argument, use it; otherwise try to detect from git remote; fallback to "/"
if [[ $# -gt 0 ]]; then
	BASEPATH="$1"
else
	if git remote get-url origin >/dev/null 2>&1; then
		repo=$(basename -s .git "$(git remote get-url origin)")
		BASEPATH="/${repo}/"
	else
		BASEPATH="/"
	fi
fi

python3 src/main.py "$BASEPATH"
echo "✅ Build finished with basepath: $BASEPATH"

