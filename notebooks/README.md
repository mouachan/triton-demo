# Notebooks Triton Demo

## 📚 Notebook disponible

### 🌸 `iris_classification.ipynb`
**Description** : Notebook complet pour la classification Iris avec Triton Inference Server

**Fonctionnalités** :
- Configuration de l'environnement OpenShift AI
- Chargement et préparation des données Iris
- Entraînement d'un modèle Random Forest
- Sauvegarde du modèle au format TensorFlow SavedModel
- Déploiement avec Triton Inference Server
- Tests d'inférence et évaluation des performances

**Utilisation** :
1. Ouvrir le notebook dans Jupyter Lab
2. Exécuter les cellules dans l'ordre
3. Vérifier la configuration de l'environnement
4. Lancer l'entraînement et le déploiement

**Dépendances** :
- OpenShift AI 2.22
- Triton Inference Server
- Model Registry (MinIO S3)
- Pipelines Elyra

## 🗂️ Structure

```
notebooks/
└── iris_classification.ipynb    # Notebook principal
```

## 📝 Notes

- Ce notebook est configuré pour fonctionner dans l'environnement `triton-demo`
- Il utilise l'image `s2i-generic-data-science-notebook:2025.1`
- Les modèles sont sauvegardés au format TensorFlow SavedModel
- L'inférence se fait via Triton avec le runtime `nvidia-triton-runtime`
