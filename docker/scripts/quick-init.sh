#!/bin/bash
# Script d'initialisation rapide pour l'image Triton Demo
# Tous les packages sont pré-installés, seulement la configuration dynamique

set -e

echo "🚀 Initialisation rapide Triton Demo Notebook..."
echo "📦 Packages pré-installés, configuration en cours..."

# Variables d'environnement
NAMESPACE=${KUBERNETES_NAMESPACE:-"triton-demo"}
CLUSTER_DOMAIN=${CLUSTER_DOMAIN:-"apps.cluster-v2mx6.v2mx6.sandbox1062.opentlc.com"}

# Fonction de configuration Elyra rapide
configure_elyra_runtime() {
    echo "⚡ Configuration rapide du runtime Elyra..."
    
    # Répertoires déjà créés dans l'image
    METADATA_DIR="/opt/app-root/src/.local/share/jupyter/metadata"
    
    # Configuration runtime Data Science Pipelines
    cat > "${METADATA_DIR}/runtimes/data_science_pipelines.json" << EOF
{
  "display_name": "Data Science Pipelines (Triton Demo)",
  "metadata": {
    "api_endpoint": "https://ds-pipeline-${NAMESPACE}-pipelines-${NAMESPACE}.${CLUSTER_DOMAIN}",
    "api_username": "",
    "api_password": "",
    "cos_endpoint": "http://minio-api.minio.svc:9000",
    "cos_username": "minioadmin",
    "cos_password": "minioadmin",
    "cos_bucket": "triton-data",
    "cos_directory": "",
    "tags": ["kubeflow", "pipelines", "triton", "optimized"],
    "engine": "Argo",
    "auth_type": "KUBERNETES_SERVICE_ACCOUNT_TOKEN",
    "runtime_type": "KUBEFLOW_PIPELINES",
    "api_version": "v1",
    "user_namespace": "${NAMESPACE}",
    "engine_namespace": "${NAMESPACE}",
    "cos_secure": false,
    "disable_ssl_verification": false,
    "cos_auth_type": "USER_CREDENTIALS"
  },
  "schema_name": "kfp",
  "name": "data_science_pipelines"
}
EOF
    
    echo "✅ Runtime Elyra configuré en < 1 seconde"
}

# Fonction de vérification des packages
verify_packages() {
    echo "🔍 Vérification rapide des packages..."
    
    python3 -c "
import sys
packages = [
    'numpy', 'pandas', 'sklearn', 'matplotlib', 'seaborn',
    'tensorflow', 'boto3', 'minio', 'tritonclient', 'kfp', 'elyra'
]
failed = []
for pkg in packages:
    try:
        __import__(pkg)
    except ImportError:
        failed.append(pkg)

if failed:
    print(f'❌ Packages manquants: {failed}')
    sys.exit(1)
else:
    print(f'✅ Tous les {len(packages)} packages critiques sont disponibles')
"
}

# Fonction de configuration Git (si le repo est fourni)
setup_git_repo() {
    if [ -n "${GIT_REPO}" ] && [ -n "${GIT_PATH}" ]; then
        echo "📂 Clonage du repository Git..."
        
        cd /opt/app-root/src
        if [ ! -d ".git" ]; then
            git clone "${GIT_REPO}" temp_repo
            if [ -n "${GIT_PATH}" ] && [ -d "temp_repo/${GIT_PATH}" ]; then
                cp -r temp_repo/${GIT_PATH}/* .
                rm -rf temp_repo
                echo "✅ Repository cloné et configuré"
            else
                echo "⚠️ Chemin ${GIT_PATH} non trouvé dans le repository"
            fi
        else
            echo "✅ Repository déjà configuré"
        fi
    fi
}

# Exécution des étapes d'initialisation
echo "🎯 Étapes d'initialisation (< 10 secondes):"

# 1. Vérification des packages (< 1 seconde)
verify_packages

# 2. Configuration Elyra (< 1 seconde)
configure_elyra_runtime

# 3. Configuration Git (< 5 secondes)
setup_git_repo

# 4. Affichage des informations système
echo ""
echo "📊 Informations système:"
echo "   🐍 Python: $(python3 --version)"
echo "   📦 Pip: $(pip --version | cut -d' ' -f1-2)"
echo "   🔐 Namespace: ${NAMESPACE}"
echo "   🌐 Cluster: ${CLUSTER_DOMAIN}"
echo "   📁 Workdir: $(pwd)"

# Vérification de l'authentification Kubernetes si disponible
if [ -f "/var/run/secrets/kubernetes.io/serviceaccount/token" ]; then
    echo "   🔑 Service Account: ✅ Disponible"
else
    echo "   🔑 Service Account: ⚠️ Non monté"
fi

echo ""
echo "🎉 Initialisation terminée en quelques secondes!"
echo "🚀 Démarrage de Jupyter Lab..."

# Démarrage de Jupyter avec la configuration optimisée
exec start-notebook.sh "$@"