#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
#  RavenDB Semantic Search — Demo Startup Script
#  Run this from the root of the repo before recording.
# ─────────────────────────────────────────────────────────────────

set -e
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
DEMO_DIR="$REPO_DIR/04-demo"

echo ""
echo "  ██████╗  █████╗ ██╗   ██╗███████╗███╗   ██╗██████╗ ██████╗ "
echo "  ██╔══██╗██╔══██╗██║   ██║██╔════╝████╗  ██║██╔══██╗██╔══██╗"
echo "  ██████╔╝███████║██║   ██║█████╗  ██╔██╗ ██║██║  ██║██████╔╝"
echo "  ██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  ██║╚██╗██║██║  ██║██╔══██╗"
echo "  ██║  ██║██║  ██║ ╚████╔╝ ███████╗██║ ╚████║██████╔╝██████╔╝"
echo "  ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝╚═════╝ ╚═════╝ "
echo ""
echo "  Semantic Search Demo"
echo "  ─────────────────────────────────────────────────────────"
echo ""

# ── 1. Check Python ────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "  ✗  Python 3 not found. Install from https://python.org"
  exit 1
fi
PYTHON_VER=$(python3 --version 2>&1)
echo "  ✓  $PYTHON_VER"

# ── 2. Check / start RavenDB ───────────────────────────────────
if curl -s http://127.0.0.1:8080/databases 2>/dev/null | grep -q "Databases\|Results"; then
  echo "  ✓  RavenDB is running at http://127.0.0.1:8080"
else
  echo ""
  echo "  ! RavenDB is not running."
  echo ""
  echo "  Start it with:"
  echo "    ./Server/Raven.Server   (Mac/Linux)"
  echo "    Server\\Raven.Server.exe  (Windows)"
  echo ""
  echo "  First time? Use Setup.Mode=None in settings.json:"
  echo "    { \"ServerUrl\": \"http://127.0.0.1:8080\", \"Setup.Mode\": \"None\" }"
  echo ""
  read -p "  Press Enter once RavenDB is running, or Ctrl+C to exit..."
  echo ""
fi

# ── 3. Install dependencies ────────────────────────────────────
echo ""
echo "  Installing Python dependencies..."
pip install -q -r "$DEMO_DIR/requirements.txt"
echo "  ✓  Dependencies ready"

# ── 4. Create .env if missing ─────────────────────────────────
ENV_FILE="$DEMO_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
  echo "  Creating .env file..."
  cat > "$ENV_FILE" << 'ENV'
RAVENDB_URL=http://127.0.0.1:8080
RAVENDB_DATABASE=ProductsDemo
RAVENDB_CERT_PATH=
ENV
  echo "  ✓  .env created"
fi

# ── 5. Check if database is seeded ────────────────────────────
DOC_COUNT=$(curl -s "http://127.0.0.1:8080/databases/ProductsDemo/stats" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('CountOfDocuments',0))" 2>/dev/null || echo "0")

if [ "$DOC_COUNT" -ge 50 ] 2>/dev/null; then
  echo "  ✓  Database seeded ($DOC_COUNT products)"
else
  echo ""
  echo "  Seeding database (generates embeddings — takes ~30s first time)..."
  cd "$DEMO_DIR" && python3 seed.py
fi

# ── 6. Launch the demo ────────────────────────────────────────
echo ""
echo "  ─────────────────────────────────────────────────────────"
echo "  Everything is ready. Launching search demo..."
echo "  ─────────────────────────────────────────────────────────"
echo ""
cd "$DEMO_DIR" && python3 search.py
