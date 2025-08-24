#!/bin/bash

# 🔒 Script de nettoyage des informations sensibles pour triton-demo
# Remplace toutes les informations sensibles par des placeholders

set -e

echo "🔒 Nettoyage des informations sensibles dans triton-demo..."
echo ""

# Fonction pour remplacer dans les fichiers
replace_in_files() {
    local search="$1"
    local replace="$2"
    local description="$3"
    
    echo "🔄 Remplacement de '$search' → '$replace' ($description)..."
    
    # Utiliser find pour trouver tous les fichiers (sauf .git et certains types)
    find . -type f \( -name "*.md" -o -name "*.py" -o -name "*.yaml" -o -name "*.yml" -o -name "*.sh" -o -name "*.pipeline" \) \
        -not -path "./.git/*" \
        -exec sed -i '' "s|$search|$replace|g" {} \;
    
    echo "✅ Remplacement terminé pour $description"
}

echo "📋 Remplacement des informations sensibles..."

# Cluster URLs
replace_in_files "CLUSTER_DOMAIN_PLACEHOLDER" "CLUSTER_DOMAIN_PLACEHOLDER" "Cluster domain"
replace_in_files "CLUSTER_NAME_PLACEHOLDER" "CLUSTER_NAME_PLACEHOLDER" "Cluster name"

# Model Registry URLs
replace_in_files "https://modelregistry-rest.apps.CLUSTER_DOMAIN_PLACEHOLDER" "https://modelregistry-rest.apps.CLUSTER_DOMAIN_PLACEHOLDER" "Model Registry URL"

# MySQL credentials
replace_in_files "MYSQL_PASSWORD_PLACEHOLDER" "MYSQL_PASSWORD_PLACEHOLDER" "MySQL password"
replace_in_files "MYSQL_USER_PLACEHOLDER" "MYSQL_USER_PLACEHOLDER" "MySQL user"

# MySQL endpoints
replace_in_files "MYSQL_ENDPOINT_PLACEHOLDER" "MYSQL_ENDPOINT_PLACEHOLDER" "MySQL endpoint"

# MinIO endpoints
replace_in_files "MINIO_ENDPOINT_PLACEHOLDER" "MINIO_ENDPOINT_PLACEHOLDER" "MinIO endpoint"

echo ""
echo "✅ Nettoyage terminé !"
echo ""
echo "📋 Prochaines étapes :"
echo "  1. Vérifier les changements : git diff"
echo "  2. Committer les changements : git add . && git commit -m '🔒 SECURITY: Replace sensitive data with placeholders'"
echo "  3. Pousser vers GitHub : git push"
echo ""
echo "🔒 Le repository est maintenant sécurisé !"
