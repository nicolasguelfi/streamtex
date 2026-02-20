#!/usr/bin/env bash

# StreamTeX Test Projects Launcher
# Paramétrable pour lancer les 3 projets en parallèle
# Usage: ./run-test-projects.sh [OPTIONS]
# Options:
#   --help           Affiche cette aide
#   --all            Lance les 3 projets (défaut)
#   --collection     Lance que le hub collection (port 8501)
#   --intro          Lance que le projet intro (port 8502)
#   --advanced       Lance que le projet advanced (port 8503)
#   --ports P1,P2,P3 Ports personnalisés (défaut: 8501,8502,8503)
#   --no-intro       Lance collection et advanced
#   --no-advanced    Lance collection et intro
#   --no-collection  Lance intro et advanced
#   --kill           Tue tous les processus Streamlit lancés
#   --watch          Lance et regarde les logs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COLLECTION_PROJECT="$SCRIPT_DIR/tests/test_collection"
INTRO_PROJECT="$SCRIPT_DIR/tests/test_project_intro"
ADVANCED_PROJECT="$SCRIPT_DIR/tests/test_project_advanced"

# Ports par défaut
COLLECTION_PORT=8501
INTRO_PORT=8502
ADVANCED_PORT=8503

# Flags pour les projets à lancer
LAUNCH_COLLECTION=true
LAUNCH_INTRO=true
LAUNCH_ADVANCED=true

WATCH_MODE=false

# Parse les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            cat << 'EOF'
StreamTeX Test Projects Launcher

USAGE:
  ./run-test-projects.sh [OPTIONS]

OPTIONS:
  --all              Lance les 3 projets (défaut)
  --collection       Lance que le hub collection (port 8501)
  --intro            Lance que le projet intro (port 8502)
  --advanced         Lance que le projet advanced (port 8503)

  --no-intro         Lance collection et advanced
  --no-advanced      Lance collection et intro
  --no-collection    Lance intro et advanced

  --ports P1,P2,P3   Ports personnalisés (défaut: 8501,8502,8503)
  --kill             Tue tous les processus Streamlit lancés
  --watch            Lance et regarde les logs (Ctrl+C pour quitter)
  --help             Affiche cette aide

EXAMPLES:
  # Lance tout (défaut)
  ./run-test-projects.sh

  # Lance que le projet intro
  ./run-test-projects.sh --intro

  # Lance collection et advanced sur ports 9001, 9003
  ./run-test-projects.sh --no-intro --ports 9001,_,9003

  # Tue tous les Streamlit
  ./run-test-projects.sh --kill

  # Lance avec watch des logs
  ./run-test-projects.sh --watch

URLs:
  Collection: http://localhost:8501
  Intro:      http://localhost:8502
  Advanced:   http://localhost:8503
EOF
            exit 0
            ;;
        --all)
            LAUNCH_COLLECTION=true
            LAUNCH_INTRO=true
            LAUNCH_ADVANCED=true
            shift
            ;;
        --collection)
            LAUNCH_COLLECTION=true
            LAUNCH_INTRO=false
            LAUNCH_ADVANCED=false
            shift
            ;;
        --intro)
            LAUNCH_COLLECTION=false
            LAUNCH_INTRO=true
            LAUNCH_ADVANCED=false
            shift
            ;;
        --advanced)
            LAUNCH_COLLECTION=false
            LAUNCH_INTRO=false
            LAUNCH_ADVANCED=true
            shift
            ;;
        --no-intro)
            LAUNCH_INTRO=false
            shift
            ;;
        --no-advanced)
            LAUNCH_ADVANCED=false
            shift
            ;;
        --no-collection)
            LAUNCH_COLLECTION=false
            shift
            ;;
        --ports)
            IFS=',' read -r COLLECTION_PORT INTRO_PORT ADVANCED_PORT <<< "$2"
            # Remplacer '_' par le port par défaut
            [ "$COLLECTION_PORT" = "_" ] && COLLECTION_PORT=8501
            [ "$INTRO_PORT" = "_" ] && INTRO_PORT=8502
            [ "$ADVANCED_PORT" = "_" ] && ADVANCED_PORT=8503
            shift 2
            ;;
        --kill)
            echo "🛑 Arrêt de tous les processus Streamlit..."
            pkill -f "streamlit run" || true
            sleep 1
            echo "✓ Fait"
            exit 0
            ;;
        --watch)
            WATCH_MODE=true
            shift
            ;;
        *)
            echo "❌ Option inconnue: $1"
            echo "Utilisez --help pour voir les options disponibles"
            exit 1
            ;;
    esac
done

# Vérifier que les projets existent
check_project() {
    local project_path=$1
    local project_name=$2
    if [ ! -d "$project_path" ]; then
        echo "❌ Le projet $project_name n'existe pas: $project_path"
        exit 1
    fi
    if [ ! -f "$project_path/book.py" ]; then
        echo "❌ book.py introuvable dans $project_name"
        exit 1
    fi
}

[ "$LAUNCH_COLLECTION" = true ] && check_project "$COLLECTION_PROJECT" "collection"
[ "$LAUNCH_INTRO" = true ] && check_project "$INTRO_PROJECT" "intro"
[ "$LAUNCH_ADVANCED" = true ] && check_project "$ADVANCED_PROJECT" "advanced"

# Logs
LOG_DIR="/tmp/streamtex-tests"
mkdir -p "$LOG_DIR"
COLLECTION_LOG="$LOG_DIR/collection.log"
INTRO_LOG="$LOG_DIR/intro.log"
ADVANCED_LOG="$LOG_DIR/advanced.log"

# Fonction pour afficher les PID
print_pids() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "StreamTeX Test Projects Running"
    echo "═══════════════════════════════════════════════════════════"
    [ "$LAUNCH_COLLECTION" = true ] && echo "📦 Collection: http://localhost:$COLLECTION_PORT (PID: $(pgrep -f "streamtex_collection" | head -1 || echo '—'))"
    [ "$LAUNCH_INTRO" = true ] && echo "📚 Intro:      http://localhost:$INTRO_PORT (PID: $(pgrep -f "streamtex_intro" | head -1 || echo '—'))"
    [ "$LAUNCH_ADVANCED" = true ] && echo "🚀 Advanced:   http://localhost:$ADVANCED_PORT (PID: $(pgrep -f "streamtex_advanced" | head -1 || echo '—'))"
    echo ""
    echo "Logs: $LOG_DIR"
    [ "$WATCH_MODE" = false ] && echo "Utilisez --kill pour arrêter tous les processus"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
}

# Libère un port en tuant les processus serveur qui l'occupent
# Note: -sTCP:LISTEN filtre uniquement les serveurs, pas les clients (navigateurs, etc.)
free_port() {
    local port=$1
    local pids
    pids=$(lsof -ti :"$port" -sTCP:LISTEN 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "   ⚠️  Port $port occupé (PIDs: $pids) — arrêt des processus..."
        echo "$pids" | xargs kill 2>/dev/null || true
        sleep 2
    fi
}

# Lance un projet
launch_project() {
    local project_path=$1
    local project_name=$2
    local port=$3
    local log_file=$4

    echo "🚀 Lancement $project_name (port $port)..."
    free_port "$port"

    cd "$SCRIPT_DIR"
    nohup uv run streamlit run "$project_path/book.py" \
        --server.port "$port" \
        --logger.level=warning \
        > "$log_file" 2>&1 &

    local pid=$!
    sleep 2

    if ps -p $pid > /dev/null 2>&1; then
        echo "   ✓ $project_name lancé (PID: $pid)"
    else
        echo "   ❌ Erreur au lancement de $project_name"
        echo "   Logs: $log_file"
        tail -20 "$log_file"
        return 1
    fi
}

# Tue tous les processus liés
cleanup() {
    echo ""
    echo "🛑 Arrêt des projets..."
    pkill -f "streamtex_collection\|streamtex_intro\|streamtex_advanced" || true
    pkill -f "streamlit run.*test_collection\|streamlit run.*test_project_intro\|streamlit run.*test_project_advanced" || true
    sleep 1
    echo "✓ Tous les projets ont été arrêtés"
}

# Configuration de cleanup au CTRL+C
trap cleanup INT

# Lance les projets
echo "StreamTeX Test Projects Launcher"
echo "=================================="
echo ""

if [ "$LAUNCH_COLLECTION" = true ]; then
    launch_project "$COLLECTION_PROJECT" "Collection" "$COLLECTION_PORT" "$COLLECTION_LOG"
fi

if [ "$LAUNCH_INTRO" = true ]; then
    launch_project "$INTRO_PROJECT" "Intro" "$INTRO_PORT" "$INTRO_LOG"
fi

if [ "$LAUNCH_ADVANCED" = true ]; then
    launch_project "$ADVANCED_PROJECT" "Advanced" "$ADVANCED_PORT" "$ADVANCED_LOG"
fi

print_pids

# Attendre si en watch mode
if [ "$WATCH_MODE" = true ]; then
    echo "📊 Mode watch activé. Appuyez sur Ctrl+C pour quitter."
    echo ""

    while true; do
        sleep 5
        # Vérifier que les processus tournent toujours
        if [ "$LAUNCH_COLLECTION" = true ] && ! pgrep -f "streamlit run.*test_collection" > /dev/null 2>&1; then
            echo "⚠️  Collection est arrêté. Redémarrage..."
            launch_project "$COLLECTION_PROJECT" "Collection" "$COLLECTION_PORT" "$COLLECTION_LOG"
        fi
        if [ "$LAUNCH_INTRO" = true ] && ! pgrep -f "streamlit run.*test_project_intro" > /dev/null 2>&1; then
            echo "⚠️  Intro est arrêté. Redémarrage..."
            launch_project "$INTRO_PROJECT" "Intro" "$INTRO_PORT" "$INTRO_LOG"
        fi
        if [ "$LAUNCH_ADVANCED" = true ] && ! pgrep -f "streamlit run.*test_project_advanced" > /dev/null 2>&1; then
            echo "⚠️  Advanced est arrêté. Redémarrage..."
            launch_project "$ADVANCED_PROJECT" "Advanced" "$ADVANCED_PORT" "$ADVANCED_LOG"
        fi
    done
else
    # Attendre un peu puis montrer les URLs
    sleep 2
    echo "✨ Tous les projets sont lancés!"
    echo ""
    echo "Ouvrez dans votre navigateur:"
    [ "$LAUNCH_COLLECTION" = true ] && echo "  • Collection: http://localhost:$COLLECTION_PORT"
    [ "$LAUNCH_INTRO" = true ] && echo "  • Intro:      http://localhost:$INTRO_PORT"
    [ "$LAUNCH_ADVANCED" = true ] && echo "  • Advanced:   http://localhost:$ADVANCED_PORT"
    echo ""
    echo "Utilisez './run-test-projects.sh --kill' pour arrêter tous les projets"
    echo ""
fi
