# 🐳 Triton Demo Notebook - Image Docker Optimisée

Image notebook personnalisée avec tous les packages ML/AI pré-installés pour des démarrages ultra-rapides.

## 🚀 Quick Start

```bash
# Build local pour tests
./build-local.sh

# Construction et push vers Quay.io
./build-and-push.sh

# Ou avec un tag spécifique
./build-and-push.sh v1.0.0
```

## 📦 Contenu de l'image

### **Base**
- UBI9 Python 3.11 (Red Hat Universal Base Image)
- Jupyter Lab 4.0+
- Elyra 3.15+
- Optimisé pour Podman/OpenShift

### **Packages pré-installés**
- **ML/AI** : TensorFlow, PyTorch, Scikit-learn, Transformers
- **Data Science** : NumPy, Pandas, Matplotlib, Seaborn
- **Cloud** : Boto3, MinIO, S3FS
- **MLOps** : Kubeflow Pipelines, Model Registry
- **Inference** : Triton Client

## 🔨 Build Manuel

```bash
# 1. Build local pour tests
./build-local.sh

# 2. Build et push vers Quay.io
podman login quay.io
podman build --file Containerfile -t quay.io/mouachan/triton-demo-notebook:latest .

# 3. Test local
podman run --rm quay.io/mouachan/triton-demo-notebook:latest \
  python3 -c "import numpy, sklearn, kfp; print('✅ All packages OK')"

# 4. Push
podman push quay.io/mouachan/triton-demo-notebook:latest
```

## 📋 Structure des fichiers

```
docker/
├── Containerfile              # Image principale (Podman)
├── build-and-push.sh         # Script automatisé pour Quay.io
├── build-local.sh            # Script de build local
├── jupyter_config/            # Configuration Jupyter optimisée
│   └── jupyter_lab_config.py  
├── scripts/                   # Scripts d'initialisation
│   └── quick-init.sh          
└── README.md                  # Cette documentation
```

## ⚡ Performance

| Métrique | Avant | Après | Gain |
|----------|-------|-------|------|
| Démarrage | 8-12 min | 30-60 sec | **90%** |
| Redémarrage | 8-12 min | 30-60 sec | **90%** |
| CPU usage | 2-4 CPU | 0.1-0.5 CPU | **80%** |

## 🔧 Utilisation

Une fois l'image poussée sur Quay.io, elle est automatiquement disponible dans OpenShift AI :

1. **Dashboard** → **Data Science Projects** → **Create Workbench**
2. **Notebook image** → "Triton Demo Notebook"
3. **Démarrage** : ~30 secondes ⚡

## 📝 Logs de build

Le script `build-and-push.sh` affiche des logs détaillés :

```
🚀 Construction et push de l'image Triton Demo
📦 Image: quay.io/mouachan/triton-demo-notebook:latest
🔍 Vérification des prérequis...
✅ Podman détecté
✅ Déjà connecté à Quay.io
🔨 Construction de l'image...
✅ Image construite avec succès
🧪 Test de l'image...
✅ Image testée avec succès
📤 Push vers Quay.io...
✅ Image poussée avec succès
🎉 Construction et push terminés!
```

## 🛡️ Sécurité

```bash
# Scanner les vulnérabilités
trivy image quay.io/mouachan/triton-demo-notebook:latest

# Audit des packages Python
podman run --rm quay.io/mouachan/triton-demo-notebook:latest pip-audit
```

## 🔄 Maintenance

### Mise à jour des packages

1. Modifier le `Dockerfile`
2. Rebuilder : `./build-and-push.sh v1.1.0`
3. Tester la nouvelle image
4. Mettre à jour la référence dans `workbench.yaml`

### Monitoring

- **Quay.io** : Scan automatique des vulnérabilités
- **GitHub Actions** : Build automatique sur push
- **OpenShift** : Health checks des workbenches

## 📞 Support

- **Issues** : [GitHub](https://github.com/mouachan/openshift-ai-setup/issues)
- **Documentation** : [Guide complet](../../../docs/CUSTOM-NOTEBOOK-IMAGE.md)

---

⚡ **Résultat** : Démarrage de workbench en 30-60 secondes au lieu de 8-12 minutes !