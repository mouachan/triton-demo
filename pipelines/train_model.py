import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import argparse

def train_model_with_onnx(data_path="data", output_path="models"):
    print("🤖 Entraînement du modèle Random Forest + Export ONNX")
    print("=" * 60)
    
    # Créer le dossier de sortie pour les modèles
    os.makedirs(output_path, exist_ok=True)
    
    print("📂 Chargement des données d'entraînement...")
    
    # Charger les données d'entraînement et de test
    with open(os.path.join(data_path, 'X_train.pkl'), 'rb') as f:
        X_train = pickle.load(f)
    
    with open(os.path.join(data_path, 'y_train.pkl'), 'rb') as f:
        y_train = pickle.load(f)
    
    with open(os.path.join(data_path, 'X_test.pkl'), 'rb') as f:
        X_test = pickle.load(f)
    
    with open(os.path.join(data_path, 'y_test.pkl'), 'rb') as f:
        y_test = pickle.load(f)
    
    # Charger les métadonnées si disponibles, sinon utiliser les valeurs par défaut
    metadata = {}
    metadata_file = os.path.join(data_path, 'metadata.pkl')
    if os.path.exists(metadata_file):
        with open(metadata_file, 'rb') as f:
            metadata = pickle.load(f)
        feature_names = metadata['feature_names']
        target_names = metadata['target_names']
    else:
        # Valeurs par défaut pour le dataset Iris si métadonnées non disponibles
        feature_names = ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
        target_names = ['setosa', 'versicolor', 'virginica']
        print("⚠️  Métadonnées non trouvées - utilisation des valeurs par défaut Iris")
    
    print(f"📊 Données chargées: {X_train.shape[0]} échantillons d'entraînement")
    print(f"📊 Features: {feature_names}")
    print(f"🎯 Classes: {target_names}")
    
    # Configuration du modèle
    n_estimators = int(os.getenv('N_ESTIMATORS', 100))
    max_depth = int(os.getenv('MAX_DEPTH', 10))
    random_state = int(os.getenv('RANDOM_STATE', 42))
    
    print(f"🌳 Configuration: {n_estimators} arbres, profondeur max: {max_depth}")
    
    # Créer et entraîner le modèle
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=-1  # Utiliser tous les CPU disponibles
    )
    
    print("🔄 Entraînement en cours...")
    model.fit(X_train, y_train)
    
    # Évaluation du modèle
    print("📈 Évaluation du modèle...")
    train_accuracy = model.score(X_train, y_train)
    test_accuracy = model.score(X_test, y_test)
    
    # Prédictions pour le rapport détaillé
    y_pred = model.predict(X_test)
    
    print(f"✅ Accuracy d'entraînement: {train_accuracy:.4f}")
    print(f"✅ Accuracy de test: {test_accuracy:.4f}")
    
    # Rapport de classification
    print("\n📊 Rapport de classification:")
    print(classification_report(y_test, y_pred, target_names=target_names))
    
    # Importance des features
    feature_importance = dict(zip(feature_names, model.feature_importances_))
    print("\n🔍 Importance des features:")
    for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feature}: {importance:.4f}")
    
    # 1. Sauvegarder le modèle scikit-learn (format pickle)
    model_pkl_path = os.path.join(output_path, 'iris_model.pkl')
    with open(model_pkl_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"💾 Modèle scikit-learn sauvegardé: {model_pkl_path}")
    
    # 2. Exporter vers ONNX
    print("\n🔄 Export vers ONNX...")
    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType
        
        # Définir le type d'entrée ONNX
        initial_type = [('float_input', FloatTensorType([None, X_train.shape[1]]))]
        
        # Convertir le modèle vers ONNX
        onnx_model = convert_sklearn(
            model, 
            initial_types=initial_type,
            target_opset=11,  # Version ONNX compatible
            options={id(model): {'zipmap': False}}  # Sortie simplifiée
        )
        
        # Sauvegarder le modèle ONNX
        onnx_path = os.path.join(output_path, 'iris_model.onnx')
        with open(onnx_path, 'wb') as f:
            f.write(onnx_model.SerializeToString())
        
        print(f"✅ Modèle ONNX exporté: {onnx_path}")
        
        # Vérifier le modèle ONNX
        try:
            import onnx
            onnx_model_check = onnx.load(onnx_path)
            onnx.checker.check_model(onnx_model_check)
            print("✅ Modèle ONNX validé avec succès")
            
            # Tester l'inférence ONNX
            try:
                import onnxruntime as ort
                
                # Créer une session d'inférence
                ort_session = ort.InferenceSession(onnx_path)
                
                # Test avec quelques échantillons
                X_test_sample = X_test[:3].astype(np.float32)
                
                # Prédiction ONNX
                ort_inputs = {ort_session.get_inputs()[0].name: X_test_sample}
                ort_outputs = ort_session.run(None, ort_inputs)
                
                # Prédiction scikit-learn pour comparaison
                sklearn_pred = model.predict(X_test_sample)
                onnx_pred = ort_outputs[0]
                
                print(f"🔍 Test d'inférence:")
                print(f"  Scikit-learn: {sklearn_pred}")
                print(f"  ONNX: {onnx_pred}")
                
                # Vérifier la cohérence
                if np.array_equal(sklearn_pred, onnx_pred):
                    print("✅ Modèles scikit-learn et ONNX cohérents")
                else:
                    print("⚠️  Différence entre modèles scikit-learn et ONNX")
                    
            except ImportError:
                print("⚠️  ONNXRuntime non disponible - test d'inférence ignoré")
                
        except ImportError:
            print("⚠️  Package onnx non disponible - validation ignorée")
            
    except ImportError:
        print("⚠️  skl2onnx non disponible - export ONNX ignoré")
        print("💡 Pour activer ONNX: pip install skl2onnx onnx onnxruntime")
        onnx_path = None
    
    # 3. Sauvegarder les métadonnées du modèle
    model_metadata = {
        "model_type": "RandomForestClassifier",
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "train_accuracy": float(train_accuracy),
        "test_accuracy": float(test_accuracy),
        "feature_names": feature_names,
        "target_names": target_names,
        "feature_importance": feature_importance,
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, target_names=target_names, output_dict=True),
        "model_formats": {
            "pickle": "iris_model.pkl",
            "onnx": "iris_model.onnx" if onnx_path else None
        },
        "input_schema": {
            "type": "float32",
            "shape": [None, len(feature_names)],
            "features": feature_names
        },
        "output_schema": {
            "type": "int64",
            "classes": target_names
        }
    }
    
    model_metadata_path = os.path.join(output_path, 'model_metadata.pkl')
    with open(model_metadata_path, 'wb') as f:
        pickle.dump(model_metadata, f)
    
    # Sauvegarder également en JSON pour faciliter la lecture
    import json
    model_metadata_json_path = os.path.join(output_path, 'model_metadata.json')
    with open(model_metadata_json_path, 'w') as f:
        json.dump(model_metadata, f, indent=2)
    
    print(f"\n💾 Métadonnées sauvegardées:")
    print(f"  📄 {model_metadata_path}")
    print(f"  📄 {model_metadata_json_path}")
    
    print("\n🎉 Entraînement et export terminés avec succès!")
    
    # Résumé des fichiers créés
    print("\n📁 Fichiers créés:")
    print(f"  🤖 Modèle scikit-learn: iris_model.pkl")
    if onnx_path:
        print(f"  🔄 Modèle ONNX: iris_model.onnx")
    print(f"  📋 Métadonnées: model_metadata.pkl/.json")
    
    # Recommandation pour Model Registry
    print("\n🏛️ Pour Model Registry OpenShift AI:")
    if onnx_path:
        print("✅ Utilisez le fichier ONNX (format standard MLOps)")
        print("📂 Fichier principal: iris_model.onnx")
    else:
        print("📂 Fichier principal: iris_model.pkl")
    print("📋 Métadonnées: model_metadata.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entraînement du modèle Iris avec export ONNX")
    parser.add_argument("--data_path", type=str, default="data",
                       help="Chemin vers les données preprocessées")
    parser.add_argument("--output_path", type=str, default="models",
                       help="Chemin de sortie pour le modèle entraîné")
    
    args = parser.parse_args()
    train_model_with_onnx(args.data_path, args.output_path)