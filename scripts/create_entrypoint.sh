#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DESKTOP_PATH="${DESKTOP_PATH:-${PROJECT_ROOT}/scripts/neo-robot.desktop}"

cat > "${DESKTOP_PATH}" <<EOF
[Desktop Entry]
Type=Application
Name=NEO Robot
Comment=Learn Python by controlling a robot arm
Exec=${PROJECT_ROOT}/scripts/neo-robot-launcher.sh
Terminal=true
Categories=Education;
Keywords=robot;python;education;stem;
EOF

cat > "${PROJECT_ROOT}/scripts/neo-robot-launcher.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if command -v neo-robot >/dev/null 2>&1; then
  exec neo-robot "$@"
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"
exec env PYTHONPATH="${PROJECT_ROOT}/src" "${PYTHON_BIN}" -m neo_robot "$@"
EOF

chmod +x "${PROJECT_ROOT}/scripts/neo-robot-launcher.sh"
echo "Wrote ${DESKTOP_PATH}"
