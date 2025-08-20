import os
import pickle
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import argparse

def preprocess_data(output_path="data"):
    print("🔄 Chargement des données Iris...")
    
    # Charger les données Iris
    iris = load_iris()
    X, y = iris.data, iris.target
    
    print(f"📊 Dataset: {X.shape[0]} échantillons, {X.shape[1]} features")
    print(f"📊 Classes: {iris.target_names}")
    
    # S'assurer que les noms sont des listes Python (pas des numpy arrays)
    feature_names = list(iris.feature_names) if hasattr(iris.feature_names, '__iter__') else iris.feature_names
    target_names = list(iris.target_names) if hasattr(iris.target_names, '__iter__') else iris.target_names
    
    print("🔄 Division train/test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=42,
        stratify=y
    )
    
    print("🔄 Normalisation des features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Créer le dossier de sortie
    os.makedirs(output_path, exist_ok=True)
    
    print(f"💾 Sauvegarde des données dans {output_path}...")
    
    # Sauvegarder les données d'entraînement
    with open(os.path.join(output_path, 'X_train.pkl'), 'wb') as f:
        pickle.dump(X_train_scaled, f)
    
    with open(os.path.join(output_path, 'X_test.pkl'), 'wb') as f:
        pickle.dump(X_test_scaled, f)
    
    with open(os.path.join(output_path, 'y_train.pkl'), 'wb') as f:
        pickle.dump(y_train, f)
    
    with open(os.path.join(output_path, 'y_test.pkl'), 'wb') as f:
        pickle.dump(y_test, f)
    
    # Sauvegarder le scaler
    with open(os.path.join(output_path, 'scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)
    
    # Préparer les métadonnées - CORRECTION ICI
    metadata = {
        "feature_names": feature_names,  # Pas de .tolist() car c'est déjà une liste
        "target_names": target_names,    # Pas de .tolist() car c'est déjà une liste
        "n_features": X.shape[1],
        "n_classes": len(np.unique(y)),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "feature_stats": {
            "mean": X_train_scaled.mean(axis=0).tolist(),
            "std": X_train_scaled.std(axis=0).tolist()
        }
    }
    
    # Sauvegarder les métadonnées
    with open(os.path.join(output_path, 'metadata.pkl'), 'wb') as f:
        pickle.dump(metadata, f)
    
    print("✅ Preprocessing terminé avec succès!")
    print(f"📊 Données d'entraînement: {X_train_scaled.shape}")
    print(f"📊 Données de test: {X_test_scaled.shape}")
    print(f"🎯 Classes: {len(np.unique(y))}")
    print(f"📋 Features: {feature_names}")
    print(f"📋 Classes: {target_names}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Préprocessing des données Iris")
    parser.add_argument("--output_path", type=str, default="data",
                       help="Chemin de sortie pour les données preprocessées")
    
    args = parser.parse_args()
    preprocess_data(args.output_path)