# Configuration Jupyter Lab optimisée pour Triton Demo
# Améliore les performances et l'expérience utilisateur

c = get_config()

# Configuration Elyra
c.ElyraApp.enable_pipeline_editing = True
c.ElyraApp.runtime_env = 'kubeflow_pipelines'

# Configuration des extensions
c.LabApp.collaborative = False
c.LabApp.news_url = None

# Optimisations de performance
c.ServerApp.max_buffer_size = 268435456  # 256MB
c.ServerApp.max_body_size = 268435456    # 256MB
c.ServerApp.rate_limit_window = 3        # Réduire la fenêtre de rate limiting

# Configuration des kernels
c.MappingKernelManager.default_kernel_name = 'python3'
c.KernelManager.autorestart = True

# Configuration des terminaux
c.ServerApp.terminals_enabled = True

# Configuration de sécurité (pour OpenShift)
c.ServerApp.disable_check_xsrf = True
c.ServerApp.allow_remote_access = True
c.ServerApp.allow_origin = '*'

# Logging optimisé
c.Application.log_level = 'INFO'
c.ServerApp.log_level = 'INFO'

# Configuration des data connections pour OpenShift AI
c.ElyraApp.data_connections = {
    'triton-data-connection': {
        'type': 's3',
        'endpoint': 'http://minio-api.minio.svc:9000',
        'access_key': 'minioadmin',
        'secret_key': 'minioadmin',
        'bucket': 'triton-data'
    }
}

print("✅ Configuration Jupyter Lab chargée - Triton Demo optimisé")