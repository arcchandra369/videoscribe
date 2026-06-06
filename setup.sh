#!/usr/bin/env bash
set -e

echo ""
echo "  ██╗   ██╗██╗██████╗ ███████╗ ██████╗ ███████╗ ██████╗██████╗ ██╗██████╗ ███████╗"
echo "  ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗██╔════╝██╔════╝██╔══██╗██║██╔══██╗██╔════╝"
echo "  ██║   ██║██║██║  ██║█████╗  ██║   ██║███████╗██║     ██████╔╝██║██████╔╝█████╗  "
echo "  ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║╚════██║██║     ██╔══██╗██║██╔══██╗██╔══╝  "
echo "   ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝███████║╚██████╗██║  ██║██║██████╔╝███████╗"
echo "    ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝"
echo ""
echo "  VideoScribe Setup"
echo "  ─────────────────────────────────────────────────"
echo ""

# ── 1. Check Python version ──────────────────────────────
echo "→ Checking Python version..."
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; }; then
    echo "✗ Python 3.8+ is required. You have Python $PYTHON_VERSION."
    echo "  Download Python from https://www.python.org/downloads/"
    exit 1
fi
echo "✓ Python $PYTHON_VERSION detected"

# ── 2. Check ffmpeg ──────────────────────────────────────
echo "→ Checking ffmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "✗ ffmpeg is not installed."
    echo ""
    echo "  Install instructions:"
    echo "  ┌─ macOS ──────────────────────────────────────────┐"
    echo "  │  brew install ffmpeg                              │"
    echo "  └──────────────────────────────────────────────────┘"
    echo "  ┌─ Linux (Debian/Ubuntu) ───────────────────────────┐"
    echo "  │  sudo apt update && sudo apt install ffmpeg        │"
    echo "  └──────────────────────────────────────────────────┘"
    echo "  ┌─ Linux (RHEL/CentOS) ─────────────────────────────┐"
    echo "  │  sudo yum install ffmpeg                           │"
    echo "  └──────────────────────────────────────────────────┘"
    echo "  ┌─ Windows ─────────────────────────────────────────┐"
    echo "  │  Download from https://ffmpeg.org/download.html   │"
    echo "  │  Add to PATH after installing                      │"
    echo "  └──────────────────────────────────────────────────┘"
    exit 1
fi
echo "✓ ffmpeg is installed"

# ── 3. Check ClamAV ─────────────────────────────────────
echo "→ Checking ClamAV..."
if ! command -v clamscan &> /dev/null; then
    echo "⚠  ClamAV is not installed. Virus scanning will be disabled."
    echo ""
    echo "  Install ClamAV (recommended):"
    echo "  ┌─ macOS ──────────────────────────────────────────┐"
    echo "  │  brew install clamav                              │"
    echo "  └──────────────────────────────────────────────────┘"
    echo "  ┌─ Linux (Debian/Ubuntu) ───────────────────────────┐"
    echo "  │  sudo apt install clamav clamav-daemon             │"
    echo "  └──────────────────────────────────────────────────┘"
    echo "  ┌─ Linux (RHEL/CentOS) ─────────────────────────────┐"
    echo "  │  sudo yum install clamav                           │"
    echo "  └──────────────────────────────────────────────────┘"
    echo "  ┌─ Windows ─────────────────────────────────────────┐"
    echo "  │  https://www.clamav.net/downloads                  │"
    echo "  └──────────────────────────────────────────────────┘"
    echo ""
    echo "  You can continue without ClamAV by setting CLAMAV_ENABLED=false in .env"
else
    echo "✓ ClamAV is installed"
fi

# ── 4. Install Python dependencies ──────────────────────
echo "→ Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✓ Dependencies installed"

# ── 5. Update ClamAV virus definitions ──────────────────
if command -v freshclam &> /dev/null; then
    echo "→ Updating ClamAV virus definitions..."
    freshclam 2>/dev/null || echo "⚠  Could not update ClamAV definitions (may need sudo or ClamAV config). Continuing..."
fi

# ── 6. Create directories ────────────────────────────────
echo "→ Creating project directories..."
mkdir -p downloads quarantine transcripts
echo "✓ Directories created: downloads/, quarantine/, transcripts/"

# ── 7. Copy .env.example to .env if not exists ──────────
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env from .env.example"
    echo "  ⚠  Don't forget to add your ANTHROPIC_API_KEY to .env"
else
    echo "✓ .env already exists"
fi

echo ""
echo "  ─────────────────────────────────────────────────"
echo "  ✓ Setup complete!"
echo ""
echo "  Next steps:"
echo "  1. Edit .env and add your ANTHROPIC_API_KEY"
echo "     Get one at: https://console.anthropic.com/"
echo ""
echo "  2. Run the CLI:"
echo "     python3 main.py"
echo ""
echo "  3. Or launch the web UI:"
echo "     python3 app.py"
echo "     Then open: http://localhost:5000"
echo "  ─────────────────────────────────────────────────"
echo ""
