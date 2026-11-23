#!/usr/bin/env bash

# ============================================================
#   ████████╗███████╗██████╗ ███╗   ███╗██╗   ██╗██╗  ██╗
#   ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║   ██║╚██╗██╔╝
#      ██║   █████╗  ██████╔╝██╔████╔██║██║   ██║ ╚███╔╝
#      ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║ ██╔██╗
#      ██║   ███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██╔╝ ██╗
#      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝
#
#   Smart Setup & Runner  •  Skip if Already Installed
# ============================================================

set -euo pipefail

# ---------- Colors ----------
R="\033[0m"; B="\033[1m"; D="\033[2m"
RED="\033[0;31m"; GRN="\033[0;32m"; YEL="\033[0;33m"
BLU="\033[0;34m"; MAG="\033[0;35m"; CYN="\033[0;36m"; WHT="\033[0;37m"
BG_G="\033[42m"

# ---------- Helpers ----------
ok()    { echo -e "  ${GRN}${B}✔${R} ${GRN}$1${R}"; }
skip()  { echo -e "  ${MAG}${B}↷${R} ${MAG}$1${R}"; }
warn()  { echo -e "  ${YEL}${B}⚠${R} ${YEL}$1${R}"; }
fail()  { echo -e "  ${RED}${B}✘${R} ${RED}$1${R}"; }
info()  { echo -e "  ${CYN}${B}ℹ${R} ${WHT}$1${R}"; }
step()  {
    echo -e "\n${BLU}${B}▶ $1${R}"
    echo -e "${D}────────────────────────────────────────────────────${R}"
}

# ---------- Banner ----------
banner() {
    clear
    echo -e "${CYN}${B}"
    cat <<'EOF'
  ╔══════════════════════════════════════════════════╗
  ║                                                  ║
  ║        🚀  TERMUX AUTO SETUP & RUNNER  🚀        ║
  ║                                                  ║
  ║     Python • Modules • Execute app.py            ║
  ║                                                  ║
  ╚══════════════════════════════════════════════════╝
EOF
    echo -e "${R}"
}

banner

# ---------- Script Directory (এখানেই app.py আছে) ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
info "Working directory: $SCRIPT_DIR"

# ---------- [1/4] Storage Permission ----------
step "[1/4] Storage Permission"

if [ -d "$HOME/storage" ]; then
    skip "Storage already configured — skipping"
else
    info "Requesting storage permission..."
    termux-setup-storage
    sleep 2
    ok "Storage permission granted"
fi

# ---------- [2/4] Python Check / Install ----------
step "[2/4] Python Environment"

if command -v python >/dev/null 2>&1; then
    skip "Python already installed — $(python --version 2>&1)"
else
    info "Installing Python & Git..."
    pkg update -y >/dev/null 2>&1
    pkg install -y python git >/dev/null 2>&1
    ok "Python installed — $(python --version 2>&1)"
fi

# Ensure Git is present
if ! command -v git >/dev/null 2>&1; then
    info "Installing Git..."
    pkg install -y git >/dev/null 2>&1
    ok "Git installed"
else
    skip "Git already installed"
fi

# Upgrade pip silently
python -m pip install --upgrade pip >/dev/null 2>&1 || true
ok "pip is up to date"

# ---------- [3/4] Python Modules ----------
step "[3/4] Python Modules"

MODULES=(
    "httpx"
    "aiohttp"
    "requests"
    "pycryptodome"
    "protobuf>=6.30.0"
    "protobuf-decoder"
    "google-play-scraper"
)

declare -A IMPORT_NAME=(
    ["httpx"]="httpx"
    ["aiohttp"]="aiohttp"
    ["requests"]="requests"
    ["pycryptodome"]="Crypto"
    ["protobuf>=6.30.0"]="google.protobuf"
    ["protobuf-decoder"]="protobuf_decoder"
    ["google-play-scraper"]="google_play_scraper"
)

for pkg in "${MODULES[@]}"; do
    imp="${IMPORT_NAME[$pkg]}"
    if python -c "import $imp" >/dev/null 2>&1; then
        skip "$pkg already installed"
    else
        info "Installing $pkg ..."
        if python -m pip install "$pkg" >/dev/null 2>&1; then
            ok "$pkg installed"
        else
            warn "$pkg failed to install (continuing)"
        fi
    fi
done

# ---------- [4/4] Run app.py (একই ফোল্ডারে) ----------
step "[4/4] Executing app.py"

cd "$SCRIPT_DIR"

if [ ! -f "app.py" ]; then
    fail "app.py not found in '$SCRIPT_DIR'"
    exit 1
fi

echo -e "\n${BG_G}${B}${WHT}  ▶  STARTING app.py  ${R}\n"
echo -e "${CYN}${B}════════════════════════════════════════════════════${R}\n"

python app.py

echo -e "\n${CYN}${B}════════════════════════════════════════════════════${R}"
echo -e "${GRN}${B}  ✔  Execution finished successfully${R}\n"