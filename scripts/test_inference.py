#!/usr/bin/env python3
"""
Script de test d'inférence pour le modèle Iris Triton
Teste le modèle déployé via KServe avec Triton Inference Server
"""

import requests
import json
import numpy as np
import argparse
import sys
from typing import Dict, List, Any

# Configuration par défaut
DEFAULT_MODEL_NAME = "iris_classifier"
DEFAULT_MODEL_VERSION = "1"

# Données de test Iris (features: sepal_length, sepal_width, petal_length, petal_width)
SAMPLE_DATA = {
    "setosa": [5.1, 3.5, 1.4, 0.2],
    "versicolor": [6.2, 2.9, 4.3, 1.3],
    "virginica": [6.3, 3.3, 6.0, 2.5]
}

# Mapping des classes
CLASS_NAMES = ["setosa", "versicolor", "virginica"]

def prepare_triton_request(input_data: List[List[float]], 
                          model_name: str = DEFAULT_MODEL_NAME) -> Dict[str, Any]:
    """
    Prépare la requête au format Triton Inference Server v2 protocol
    """
    return {
        "inputs": [
            {
                "name": "input_features",
                "shape": [len(input_data), 4],
                "datatype": "FP32",
                "data": [item for sublist in input_data for item in sublist]
            }
        ],
        "outputs": [
            {
                "name": "predictions"
            },
            {
                "name": "probabilities"
            }
        ]
    }

def send_inference_request(url: str, data: Dict[str, Any], 
                          timeout: int = 30) -> requests.Response:
    """
    Envoie une requête d'inférence au serveur Triton
    """
    headers = {
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(url, 
                               headers=headers, 
                               data=json.dumps(data), 
                               timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la requête: {e}")
        sys.exit(1)

def parse_triton_response(response: requests.Response) -> Dict[str, Any]:
    """
    Parse la réponse du serveur Triton
    """
    try:
        result = response.json()
        
        # Extraire les prédictions
        predictions_output = None
        probabilities_output = None
        
        for output in result.get("outputs", []):
            if output["name"] == "predictions":
                predictions_output = output
            elif output["name"] == "probabilities":
                probabilities_output = output
        
        if not predictions_output:
            raise ValueError("Sortie 'predictions' non trouvée dans la réponse")
        
        predictions = predictions_output["data"]
        probabilities = probabilities_output["data"] if probabilities_output else None
        
        return {
            "predictions": predictions,
            "probabilities": probabilities,
            "shape": predictions_output["shape"]
        }
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"❌ Erreur lors du parsing de la réponse: {e}")
        print(f"Réponse brute: {response.text}")
        sys.exit(1)

def format_results(parsed_response: Dict[str, Any], 
                  input_samples: List[str]) -> None:
    """
    Formate et affiche les résultats
    """
    predictions = parsed_response["predictions"]
    probabilities = parsed_response["probabilities"]
    
    print("\n🔍 RÉSULTATS D'INFÉRENCE")
    print("=" * 50)
    
    for i, sample_name in enumerate(input_samples):
        pred_class_idx = int(predictions[i])
        pred_class_name = CLASS_NAMES[pred_class_idx]
        
        print(f"\n📊 Échantillon: {sample_name}")
        print(f"   Prédiction: {pred_class_name} (classe {pred_class_idx})")
        
        if probabilities:
            # Afficher les probabilités pour chaque classe
            print("   Probabilités:")
            start_idx = i * 3
            for j, class_name in enumerate(CLASS_NAMES):
                prob = probabilities[start_idx + j]
                print(f"     - {class_name}: {prob:.4f} ({prob*100:.2f}%)")

def test_health_check(base_url: str) -> bool:
    """
    Teste si le serveur Triton est accessible
    """
    health_url = f"{base_url}/v2/health/ready"
    
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print("✅ Serveur Triton accessible")
            return True
        else:
            print(f"⚠️  Serveur Triton non prêt (status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Impossible de contacter le serveur: {e}")
        return False

def test_model_metadata(base_url: str, model_name: str, model_version: str) -> bool:
    """
    Récupère les métadonnées du modèle
    """
    metadata_url = f"{base_url}/v2/models/{model_name}/versions/{model_version}"
    
    try:
        response = requests.get(metadata_url, timeout=10)
        if response.status_code == 200:
            metadata = response.json()
            print(f"✅ Modèle {model_name} v{model_version} disponible")
            print(f"   Platform: {metadata.get('platform', 'N/A')}")
            print(f"   Inputs: {len(metadata.get('inputs', []))}")
            print(f"   Outputs: {len(metadata.get('outputs', []))}")
            return True
        else:
            print(f"❌ Modèle non trouvé (status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur métadonnées: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test d'inférence pour le modèle Iris Triton")
    parser.add_argument("--url", "-u", 
                       default="http://iris-classifier-triton-rhods-notebooks.apps.your-cluster.com",
                       help="URL de base du service d'inférence")
    parser.add_argument("--model-name", "-m", 
                       default=DEFAULT_MODEL_NAME,
                       help="Nom du modèle")
    parser.add_argument("--model-version", "-v", 
                       default=DEFAULT_MODEL_VERSION,
                       help="Version du modèle")
    parser.add_argument("--samples", "-s", 
                       nargs="+",
                       default=["setosa", "versicolor", "virginica"],
                       choices=list(SAMPLE_DATA.keys()),
                       help="Échantillons à tester")
    parser.add_argument("--custom-data", 
                       help="Données personnalisées au format JSON: [[5.1,3.5,1.4,0.2]]")
    
    args = parser.parse_args()
    
    print("🚀 DÉMARRAGE DU TEST D'INFÉRENCE TRITON")
    print("=" * 50)
    print(f"URL: {args.url}")
    print(f"Modèle: {args.model_name} v{args.model_version}")
    
    # Test de santé du serveur
    if not test_health_check(args.url):
        sys.exit(1)
    
    # Test des métadonnées du modèle
    if not test_model_metadata(args.url, args.model_name, args.model_version):
        sys.exit(1)
    
    # Préparer les données d'entrée
    if args.custom_data:
        try:
            input_data = json.loads(args.custom_data)
            sample_names = [f"custom_{i}" for i in range(len(input_data))]
        except json.JSONDecodeError:
            print("❌ Format JSON invalide pour --custom-data")
            sys.exit(1)
    else:
        input_data = [SAMPLE_DATA[sample] for sample in args.samples]
        sample_names = args.samples
    
    print(f"\n📋 Test avec {len(input_data)} échantillon(s)")
    
    # Préparer la requête Triton
    triton_request = prepare_triton_request(input_data, args.model_name)
    
    # URL d'inférence
    inference_url = f"{args.url}/v2/models/{args.model_name}/versions/{args.model_version}/infer"
    
    print(f"\n🔄 Envoi de la requête d'inférence...")
    print(f"URL: {inference_url}")
    
    # Envoyer la requête
    response = send_inference_request(inference_url, triton_request)
    
    # Parser et afficher les résultats
    parsed_response = parse_triton_response(response)
    format_results(parsed_response, sample_names)
    
    print(f"\n✅ Test d'inférence terminé avec succès!")
    print(f"Status: {response.status_code}")
    print(f"Temps de réponse: {response.elapsed.total_seconds():.3f}s")

if __name__ == "__main__":
    main()
