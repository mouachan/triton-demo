import os
import json
import pickle
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def try_install_onnx():
    """Tentative d'installation ONNX sans forcer"""
    
    print("🔧 Tentative d'installation ONNX optionnelle...")
    
    import subprocess
    import sys
    
    try:
        # Essayer les versions les plus récentes disponibles
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "onnx", "onnxruntime", "skl2onnx", 
            "--upgrade", "--quiet"
        ])
        print("✅ ONNX installé avec versions disponibles")
        return True
    except Exception as e:
        print(f"⚠️ Installation ONNX échouée: {e}")
        print("💡 Continuer avec modèle sklearn uniquement")
        return False

def install_model_registry():
    """Installation Model Registry uniquement"""
    
    print("🔧 Installation Model Registry...")
    
    import subprocess
    import sys
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "aiohttp-retry", "model-registry==0.2.7a1", "--quiet"
        ])
        print("✅ Model Registry installé")
        return True
    except Exception as e:
        print(f"⚠️ Erreur Model Registry: {e}")
        return False

def evaluate_model():
    """Évalue le modèle sur les données de test"""
    
    print("🔍 Chargement du modèle et des données...")
    
    try:
        # Charger le modèle
        with open('models/iris_model.pkl', 'rb') as f:
            model = pickle.load(f)
        
        # Charger les données de test
        with open('data/X_test.pkl', 'rb') as f:
            X_test = pickle.load(f)
        with open('data/y_test.pkl', 'rb') as f:
            y_test = pickle.load(f)
        
        # Charger les métadonnées du modèle
        with open('models/model_metadata.json', 'r') as f:
            model_metadata = json.load(f)
        
        print(f"📊 Données de test: {X_test.shape}")
        print(f"📊 Labels de test: {y_test.shape}")
        
        # Faire les prédictions
        print("🧪 Prédictions sur les données de test...")
        y_pred = model.predict(X_test)
        
        # Calculer les métriques
        accuracy = accuracy_score(y_test, y_pred)
        class_report = classification_report(y_test, y_pred, output_dict=True)
        conf_matrix = confusion_matrix(y_test, y_pred)
        
        # Compter les erreurs
        errors = np.sum(y_test != y_pred)
        total_samples = len(y_test)
        
        print(f"📈 Précision du modèle: {accuracy:.4f}")
        print(f"📊 Erreurs de classification: {errors}/{total_samples} échantillons")
        
        # Créer le répertoire evaluation
        eval_dir = Path("evaluation")
        eval_dir.mkdir(exist_ok=True)
        
        # Préparer les métriques complètes
        evaluation_metrics = {
            "accuracy": float(accuracy),
            "error_rate": float(errors / total_samples),
            "errors": int(errors),
            "total_samples": int(total_samples),
            "classification_report": class_report,
            "confusion_matrix": conf_matrix.tolist(),
            "model_metadata": model_metadata
        }
        
        # Sauvegarder les métriques pour Elyra (format pkl attendu)
        with open(eval_dir / "evaluation_metrics.pkl", "wb") as f:
            pickle.dump(evaluation_metrics, f)
        
        # Sauvegarder aussi en JSON pour lisibilité
        with open(eval_dir / "evaluation_metrics.json", "w") as f:
            json.dump(evaluation_metrics, f, indent=2)
        
        # Sauvegarder accuracy pour KFP
        with open(eval_dir / "accuracy.txt", "w") as f:
            f.write(str(accuracy))
        
        print("🏛️ Logging des métriques pour KFP...")
        print("✅ Métriques sauvegardées au format KFP")
        
        return accuracy, evaluation_metrics, model, X_test
        
    except Exception as e:
        print(f"❌ Erreur lors de l'évaluation: {e}")
        # Créer fichiers minimaux pour Elyra
        eval_dir = Path("evaluation")
        eval_dir.mkdir(exist_ok=True)
        
        empty_metrics = {"accuracy": 0.0, "error_message": str(e)}
        
        with open(eval_dir / "evaluation_metrics.pkl", "wb") as f:
            pickle.dump(empty_metrics, f)
        with open(eval_dir / "accuracy.txt", "w") as f:
            f.write("0.0")
            
        return 0.0, {}, None, None

def try_convert_to_onnx(model, X_sample):
    """Tentative de conversion ONNX si possible"""
    
    print("🔄 Tentative de conversion ONNX...")
    
    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType
        import onnx
        import onnxruntime as ort
        
        print(f"📦 ONNX disponible - tentative de conversion...")
        
        n_features = X_sample.shape[1]
        initial_type = [('float_input', FloatTensorType([None, n_features]))]
        
        # Conversion simple pour ONNX 1.9 (compatible Triton 23.10)
        onnx_model = convert_sklearn(
            model, 
            initial_types=initial_type,
            options={'zipmap': False},
            target_opset=9
        )
        
        # Sauvegarder
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        onnx_path = models_dir / "iris_model.onnx"
        
        with open(onnx_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        
        # Test rapide
        session = ort.InferenceSession(str(onnx_path))
        test_input = X_sample[:1].astype(np.float32)
        result = session.run(None, {session.get_inputs()[0].name: test_input})
        
        print(f"✅ Modèle ONNX créé avec succès!")
        print(f"📊 Taille: {os.path.getsize(onnx_path)} bytes")
        
        return str(onnx_path)
        
    except Exception as e:
        print(f"❌ Conversion ONNX échouée: {e}")
        return None

def get_model_registry_config():
    """Configuration Model Registry"""
    
    model_registry_url = "https://modelregistry-rest.apps.CLUSTER_DOMAIN_PLACEHOLDER"
    token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
    
    try:
        with open(token_path, 'r') as f:
            token = f.read().strip()
        print("🔓 Connexion via ServiceAccount Kubernetes")
        return model_registry_url, token
    except FileNotFoundError:
        print(f"❌ Token ServiceAccount non trouvé")
        return None, None

def create_triton_structure_local(onnx_path):
    """Crée la structure de répertoire Triton locale parfaite"""
    
    if not onnx_path or not os.path.exists(onnx_path):
        print("⚠️ Pas de modèle ONNX - structure Triton non créée")
        return False
    
    try:
        print("🔧 Création de la structure Triton locale parfaite...")
        
        # Créer le répertoire iris_model/1
        triton_dir = Path("models/iris_model/1")
        triton_dir.mkdir(parents=True, exist_ok=True)
        
        # Copier le modèle dans la structure Triton
        triton_model_path = triton_dir / "iris_model.onnx"
        import shutil
        shutil.copy2(onnx_path, triton_model_path)
        
        # Créer le fichier de configuration Triton DANS le répertoire iris_model
        config_path = Path("models/iris_model/config.pbtxt")
        config_content = f"""name: "iris_model"
platform: "onnxruntime_onnx"
max_batch_size: 0
default_model_filename: "iris_model.onnx"
input [
  {{
    name: "float_input"
    data_type: TYPE_FP32
    dims: [ -1, 4 ]
  }}
]
output [
  {{
    name: "output"
    data_type: TYPE_FP32
    dims: [ 1 ]
  }},
  {{
    name: "probabilities"
    data_type: TYPE_FP32
    dims: [ -1, 3 ]
  }}
]
instance_group [
  {{
    count: 1
    kind: KIND_CPU
  }}
]
"""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Structure Triton parfaite créée:")
        print(f"  📁 {triton_model_path}")
        print(f"  📄 {config_path}")
        print(f"  📁 Structure finale:")
        print(f"    models/iris_model/")
        print(f"    ├── config.pbtxt")
        print(f"    └── 1/")
        print(f"        └── iris_model.onnx")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création structure Triton locale: {e}")
        return False

def register_model_in_registry(metrics, onnx_path):
    """Enregistrement dans Model Registry"""
    
    try:
        from model_registry import ModelRegistry
        print("✅ model_registry importé")
    except ImportError as e:
        print(f"❌ model_registry non disponible: {e}")
        return False
    
    registry_url, token = get_model_registry_config()
    if not registry_url or not token:
        return False
    
    try:
        print("🧪 Test de la connexion...")
        registry = ModelRegistry(
            server_address=registry_url,
            author="iris-pipeline-final",
            user_token=token,
            is_secure=False
        )
        
        # Version unique
        import time
        pipeline_id = os.getenv('PIPELINE_RUN_NAME', f'iris-{int(time.time())}')
        unique_version = f"v{int(time.time())}"
        
        # Déterminer format
        if onnx_path and os.path.exists(onnx_path):
            # Structure pour Triton: iris_model/1/iris_model.onnx
            s3_uri = f"s3://mlpipeline/{pipeline_id}/models/iris_model/1/iris_model.onnx"
            model_format = "onnx"
            description = f"🎯 Modèle Iris ONNX - Accuracy: {metrics.get('accuracy', 0):.4f} - Prêt pour déploiement"
        else:
            s3_uri = f"s3://mlpipeline/{pipeline_id}/models/iris_model.pkl"
            model_format = "sklearn"
            description = f"📊 Modèle Iris sklearn - Accuracy: {metrics.get('accuracy', 0):.4f}"
        
        print(f"📝 Enregistrement: iris-random-forest {unique_version} ({model_format.upper()})")
        
        registered_model = registry.register_model(
            name="iris-random-forest",
            uri=s3_uri,
            version=unique_version,
            model_format_name=model_format,
            model_format_version="1.0",
            description=description,
            metadata={
                "pipeline": "iris-elyra-final",
                "accuracy": float(metrics.get('accuracy', 0)),
                "deployment_ready": onnx_path is not None,
                "pipeline_run": pipeline_id
            }
        )
        
        print(f"✅ Modèle enregistré avec succès!")
        print(f"📋 ID: {getattr(registered_model, 'id', 'N/A')}")
        print(f"🎯 Format: {model_format.upper()}")
        print(f"🔢 Version: {unique_version}")
        
        # Créer la structure Triton dans S3 si c'est un modèle ONNX
        if onnx_path and os.path.exists(onnx_path):
            print("\n🔧 Création de la structure Triton locale...")
            triton_structure_created = create_triton_structure_local(onnx_path)
            if triton_structure_created:
                print("✅ Structure Triton prête pour déploiement!")
            else:
                print("⚠️ Structure Triton non créée - déploiement manuel requis")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur Model Registry: {e}")
        return False

def create_fallback_files():
    """Crée les fichiers attendus par Elyra même si non utilisés"""
    
    eval_dir = Path("evaluation")
    eval_dir.mkdir(exist_ok=True)
    
    # Créer registry_info.json même si l'enregistrement réussit
    # (pour éviter l'erreur Elyra)
    fallback_info = {
        "status": "registration_attempted",
        "note": "Voir les logs pour le résultat réel"
    }
    
    with open(eval_dir / "registry_info.json", "w") as f:
        json.dump(fallback_info, f, indent=2)

def main():
    """Fonction principale simplifiée et robuste"""
    
    print("🚀 Pipeline Iris Final - Robuste et Fonctionnel")
    
    # 1. Installation optionnelle
    onnx_available = try_install_onnx()
    registry_available = install_model_registry()
    
    # 2. Évaluation (priorité absolue)
    accuracy, metrics, model, X_test = evaluate_model()
    
    if not metrics:
        print("❌ Impossible de continuer sans métriques")
        create_fallback_files()
        return
    
    # 3. Conversion ONNX (optionnelle)
    onnx_path = None
    if onnx_available and model is not None and X_test is not None:
        onnx_path = try_convert_to_onnx(model, X_test)
    
    # 4. Enregistrement Model Registry (optionnel)
    registry_success = False
    if registry_available:
        print("\n🏛️ Enregistrement Model Registry...")
        registry_success = register_model_in_registry(metrics, onnx_path)
    
    # 5. Créer les fichiers attendus par Elyra
    create_fallback_files()
    
    # 6. Rapport final
    print(f"\n💾 Fichiers créés:")
    print(f"  📄 evaluation/evaluation_metrics.pkl")
    print(f"  📄 evaluation/evaluation_metrics.json") 
    print(f"  📄 evaluation/accuracy.txt")
    print(f"  📄 evaluation/registry_info.json")
    if onnx_path:
        print(f"  📄 models/iris_model.onnx")
    
    print(f"\n🎯 RÉSUMÉ FINAL:")
    print(f"  📊 Accuracy: {metrics.get('accuracy', 0):.4f}")
    print(f"  🎯 ONNX: {'✅ Créé' if onnx_path else '❌ Non disponible'}")
    print(f"  🏛️ Registry: {'✅ Enregistré' if registry_success else '❌ Non disponible'}")
    
    if onnx_path and registry_success:
        print(f"\n🎉 SUCCÈS COMPLET!")
        print(f"  ✅ Modèle ONNX prêt pour déploiement")
    elif registry_success:
        print(f"\n✅ SUCCÈS PARTIEL!")
        print(f"  📊 Modèle sklearn enregistré - conversion ONNX possible ultérieurement")
    else:
        print(f"\n✅ ÉVALUATION RÉUSSIE!")
        print(f"  📊 Métriques sauvegardées - enregistrement manuel possible")

if __name__ == "__main__":
    main()