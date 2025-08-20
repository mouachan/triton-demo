# 🌸 Triton Demo - Classification Iris

Ce projet démontre l'utilisation de NVIDIA Triton Inference Server pour déployer et servir un modèle de classification Iris dans un environnement OpenShift AI.

## 📋 Prérequis

- OpenShift AI (RHODS) 2.22+
- ArgoCD configuré
- Model Registry opérationnel
- MinIO/S3 accessible
- MySQL pour le Model Registry

## 🚀 Déploiement

### 1. Déploiement via GitOps

Le projet est configuré pour être déployé automatiquement via ArgoCD :

```bash
# Vérifier que ArgoCD est synchronisé
oc get applications -n openshift-gitops

# Forcer la synchronisation si nécessaire
oc patch application openshift-ai-complete -n openshift-gitops --type='merge' -p='{"spec":{"syncPolicy":{"automated":{"prune":true,"selfHeal":true}}}}'
```

### 2. Composants déployés

- **MySQL Database** : `mysql.db-ai.svc.cluster.local:3306`
- **Model Registry** : `modelregistry` dans le namespace `rhoai-model-registries`
- **MinIO Storage** : `minio.db-ai.svc.cluster.local:9000`
- **Jupyter Workbench** : `triton-workbench` dans le namespace `triton-demo`
- **Triton Inference Server** : Pour servir les modèles

## 📊 Utilisation du Notebook

### 1. Accès au Workbench

1. Connectez-vous à OpenShift AI Dashboard
2. Allez dans le projet `triton-demo`
3. Lancez le workbench `triton-workbench`
4. Ouvrez le notebook `demos/triton-example/notebooks/iris_classification_notebook.ipynb`

### 2. Configuration automatique

Le workbench est configuré avec :
- **Image** : `s2i-generic-data-science-notebook:2025.1`
- **Variables d'environnement** :
  - `MODEL_REGISTRY_URL` : URL du Model Registry
  - `AWS_S3_ENDPOINT` : Endpoint MinIO
  - `AWS_S3_BUCKET` : Bucket pour les modèles
  - `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` : Credentials S3

### 3. Test local

Vous pouvez tester le notebook localement :

```bash
cd demos/triton-example
python3 test_notebook.py
```

## 🔧 Configuration

### Variables d'environnement

Le workbench utilise les variables suivantes :

```yaml
# Model Registry
MODEL_REGISTRY_URL: "https://modelregistry-rest.apps.cluster-v2mx6.v2mx6.sandbox1062.opentlc.com"
MODEL_REGISTRY_DATABASE_URL: "mysql://mlmduser:TheBlurstOfTimes@mysql.db-ai.svc.cluster.local:3306/model_registry"

# S3/MinIO
AWS_ACCESS_KEY_ID: "accesskey"
AWS_SECRET_ACCESS_KEY: "secretkey"
AWS_S3_ENDPOINT: "minio.db-ai.svc.cluster.local:9000"
AWS_S3_BUCKET: "model-registry"
AWS_S3_FORCE_PATH_STYLE: "true"
```

### Secrets

Le workbench utilise le secret `triton-demo-s3-connection` pour les credentials S3.

## 📁 Structure du projet

```
demos/triton-example/
├── notebooks/
│   └── iris_classification_notebook.ipynb  # Notebook principal
├── pipelines/
│   ├── model_registry.py                   # Script pour Model Registry
│   ├── model_training.py                   # Script d'entraînement
│   └── ...
├── models/                                 # Modèles entraînés
├── data/                                   # Données
├── test_notebook.py                        # Script de test local
└── README.md                               # Ce fichier
```

## 🎯 Fonctionnalités

### 1. Entraînement du modèle
- Chargement du dataset Iris
- Entraînement Random Forest
- Évaluation des performances
- Sauvegarde du modèle

### 2. Conversion ONNX
- Conversion du modèle scikit-learn vers ONNX
- Validation du modèle ONNX
- Test d'inférence

### 3. Model Registry
- Enregistrement du modèle
- Upload vers S3/MinIO
- Métadonnées complètes

### 4. Triton Inference
- Déploiement sur Triton
- Test d'inférence via API REST
- Monitoring des performances

## 🔍 Dépannage

### Problèmes courants

1. **Workbench ne démarre pas**
   - Vérifiez les ressources CPU/Memory
   - Vérifiez l'image Docker
   - Vérifiez les secrets S3

2. **Erreur de connexion S3**
   - Vérifiez les credentials dans le secret
   - Vérifiez l'endpoint MinIO
   - Vérifiez la connectivité réseau

3. **Erreur Model Registry**
   - Vérifiez l'URL du Model Registry
   - Vérifiez la base de données MySQL
   - Vérifiez les permissions

### Logs utiles

```bash
# Logs du workbench
oc logs -f deployment/triton-workbench -n triton-demo

# Logs du Model Registry
oc logs -f deployment/modelregistry -n rhoai-model-registries

# Logs MySQL
oc logs -f deployment/mysql -n db-ai
```

## 📈 Monitoring

### Métriques importantes

- **Accuracy du modèle** : > 0.90
- **Latence d'inférence** : < 100ms
- **Disponibilité** : > 99.9%

### Dashboards

- **OpenShift AI Dashboard** : Vue d'ensemble
- **ArgoCD** : État du déploiement GitOps
- **Grafana** : Métriques détaillées

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature
3. Committez vos changements
4. Poussez vers la branche
5. Créez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🔗 Liens utiles

- [OpenShift AI Documentation](https://access.redhat.com/documentation/en-us/red_hat_openshift_ai_self-managed)
- [NVIDIA Triton Documentation](https://github.com/triton-inference-server/server)
- [Model Registry Documentation](https://model-registry.readthedocs.io/)
- [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/)
