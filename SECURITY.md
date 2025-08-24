# 🔒 Guide de Sécurité - Triton Demo

Ce document décrit les bonnes pratiques de sécurité pour le repository `triton-demo`.

## 🚨 Informations sensibles remplacées

Toutes les informations sensibles ont été remplacées par des placeholders :

### 🔑 Credentials
- **MySQL User** : `mlmduser` → `MYSQL_USER_PLACEHOLDER`
- **MySQL Password** : `TheBlurstOfTimes` → `MYSQL_PASSWORD_PLACEHOLDER`

### 🌐 URLs et Endpoints
- **Cluster Domain** : `cluster-v2mx6.v2mx6.sandbox1062.opentlc.com` → `CLUSTER_DOMAIN_PLACEHOLDER`
- **Cluster Name** : `cluster-v2mx6` → `CLUSTER_NAME_PLACEHOLDER`
- **Model Registry URL** : `https://modelregistry-rest.apps.cluster-v2mx6.v2mx6.sandbox1062.opentlc.com` → `https://modelregistry-rest.apps.CLUSTER_DOMAIN_PLACEHOLDER`
- **MySQL Endpoint** : `mysql.db-ai.svc.cluster.local:3306` → `MYSQL_ENDPOINT_PLACEHOLDER`
- **MinIO Endpoint** : `minio.db-ai.svc.cluster.local:9000` → `MINIO_ENDPOINT_PLACEHOLDER`

## 📋 Fichiers modifiés

Les fichiers suivants ont été nettoyés :
- `README.md` - Documentation principale
- `pipelines/iris.pipeline` - Pipeline Tekton
- `pipelines/evaluate_register_model.py` - Script Python
- `docker/scripts/quick-init.sh` - Script d'initialisation

## 🛡️ Bonnes pratiques

### 1. Configuration
- ✅ Utilisez `config.env.example` comme modèle
- ✅ Créez `config.env` avec vos vraies valeurs
- ✅ Ne committez JAMAIS `config.env`

### 2. Déploiement
- ✅ Utilisez des secrets Kubernetes pour les credentials
- ✅ Utilisez des ConfigMaps pour les endpoints
- ✅ Vérifiez que les placeholders sont remplacés

### 3. Vérification
```bash
# Vérifier qu'il n'y a plus d'informations sensibles
grep -r "cluster-v2mx6" .
grep -r "TheBlurstOfTimes" .
grep -r "mlmduser" .
```

## 🔧 Utilisation des placeholders

### Dans les scripts Python
```python
import os

model_registry_url = os.getenv('MODEL_REGISTRY_URL', 'https://modelregistry-rest.apps.CLUSTER_DOMAIN_PLACEHOLDER')
mysql_user = os.getenv('MYSQL_USER', 'MYSQL_USER_PLACEHOLDER')
```

### Dans les pipelines Tekton
```yaml
env_vars:
  - env_var: "MODEL_REGISTRY_URL"
    value: "https://modelregistry-rest.apps.CLUSTER_DOMAIN_PLACEHOLDER"
```

### Dans les scripts Shell
```bash
CLUSTER_DOMAIN=${CLUSTER_DOMAIN:-"apps.CLUSTER_DOMAIN_PLACEHOLDER"}
```

## 📚 Ressources

- [OpenShift AI Documentation](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai_self-managed)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [GitHub Security Best Practices](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/creating-a-repository-on-github/about-repository-visibility)

## 🆘 Support

Pour toute question de sécurité, contactez l'équipe DevOps ou créez une issue avec le label `security`.
