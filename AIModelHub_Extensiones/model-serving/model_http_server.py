"""
Simple HTTP Server for ML Model Files
Exposes ML models through HTTP endpoints with basic authentication.
"""
import os
import hashlib
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import base64

# ============ CONFIGURATION ============
SERVER_HOST = '0.0.0.0'  # Listen on all interfaces
SERVER_PORT = 8080

# Directory where models are stored
MODEL_BASE_PATH = '/home/edmundo/AIModelHub/AIModelHub_Extensiones/model-server/models'

# Simple authentication (API Key)
API_KEY = 'ml-model-key-2024'  # Change to a secure value

# Available models - register your models here
AVAILABLE_MODELS = {
    'iris-classifier-v1': {
        'path': 'iris_classifier.pkl',
        'metadata_path': 'iris_classifier_metadata.json',
        'content_type': 'application/octet-stream',
        'description': 'Iris Random Forest Classifier',
        'version': '1.0',
        'size_bytes': None  # Will be calculated automatically
    },
    # Example for your LGBM model (when you want to add it):
    # 'lgbm-classifier-1': {
    #     'path': 'path/to/LGBM_Classifier_1.pkl',
    #     'metadata_path': 'path/to/lgbm_metadata.json',  # Create similar metadata
    #     'content_type': 'application/octet-stream',
    #     'description': 'LGBM Classifier Model v1',
    #     'version': '1.0'
    # }
}

# ============ HTTP SERVER ============
class ModelHTTPHandler(BaseHTTPRequestHandler):
    
    def _set_headers(self, status=200, content_type='application/json'):
        """Set HTTP headers with CORS"""
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key')
        self.end_headers()
    
    def _authenticate(self):
        """Check authentication via API Key"""
        # Check X-API-Key header
        api_key = self.headers.get('X-API-Key')
        if api_key == API_KEY:
            return True
        
        # Check Authorization: Bearer token
        auth_header = self.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if token == API_KEY:
                return True
        
        return False
    
    def _get_file_info(self, file_path):
        """Get file information"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'exists': True
        }
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self._set_headers(204)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Endpoint: GET /health
        if path == '/health':
            self._set_headers()
            response = {
                'status': 'healthy',
                'service': 'ML Model HTTP Server',
                'available_models': len(AVAILABLE_MODELS)
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Endpoint: GET /models - List available models
        if path == '/models':
            self._set_headers()
            models_info = {}
            for model_id, model_config in AVAILABLE_MODELS.items():
                full_path = os.path.join(MODEL_BASE_PATH, model_config['path'])
                file_info = self._get_file_info(full_path)
                models_info[model_id] = {
                    'id': model_id,
                    'description': model_config['description'],
                    'version': model_config['version'],
                    'content_type': model_config['content_type'],
                    'available': file_info is not None,
                    'size_bytes': file_info['size'] if file_info else None,
                    'download_url': f'http://localhost:{SERVER_PORT}/download/{model_id}'
                }
            
            response = {
                'models': models_info,
                'total': len(models_info)
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            return
        
        # Endpoint: GET /download/{model_id} - Download model
        if path.startswith('/download/'):
            # Verify authentication
            if not self._authenticate():
                self._set_headers(401)
                self.wfile.write(json.dumps({
                    'error': 'Unauthorized',
                    'message': 'Valid API Key required in X-API-Key header or Authorization Bearer token'
                }).encode())
                return
            
            # Get model_id
            model_id = path.split('/download/')[1].split('?')[0]
            
            if model_id not in AVAILABLE_MODELS:
                self._set_headers(404)
                self.wfile.write(json.dumps({
                    'error': 'Not Found',
                    'message': f'Model "{model_id}" not found'
                }).encode())
                return
            
            model_config = AVAILABLE_MODELS[model_id]
            full_path = os.path.join(MODEL_BASE_PATH, model_config['path'])
            
            if not os.path.exists(full_path):
                self._set_headers(404)
                self.wfile.write(json.dumps({
                    'error': 'File Not Found',
                    'message': f'Model file does not exist: {model_config["path"]}'
                }).encode())
                return
            
            # Read and send file
            try:
                with open(full_path, 'rb') as f:
                    file_data = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', model_config['content_type'])
                self.send_header('Content-Length', str(len(file_data)))
                self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(full_path)}"')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(file_data)
                
                print(f"✓ Downloaded: {model_id} ({len(file_data)} bytes)")
                
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({
                    'error': 'Internal Server Error',
                    'message': str(e)
                }).encode())
            return
        
        # Endpoint: GET /metadata/{model_id} - Get model metadata
        if path.startswith('/metadata/'):
            model_id = path.split('/metadata/')[1]
            
            if model_id not in AVAILABLE_MODELS:
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': 'Model not found'}).encode())
                return
            
            model_config = AVAILABLE_MODELS[model_id]
            full_path = os.path.join(MODEL_BASE_PATH, model_config['path'])
            file_info = self._get_file_info(full_path)
            
            # Load metadata JSON if present
            model_metadata = None
            if 'metadata_path' in model_config:
                metadata_file = os.path.join(MODEL_BASE_PATH, model_config['metadata_path'])
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r') as f:
                            model_metadata = json.load(f)
                    except Exception as e:
                        print(f"Warning: Could not load metadata file: {e}")
            
            metadata = {
                'id': model_id,
                'description': model_config['description'],
                'version': model_config['version'],
                'content_type': model_config['content_type'],
                'path': model_config['path'],
                'exists': file_info is not None,
                'size_bytes': file_info['size'] if file_info else None,
                'endpoints': {
                    'download': f'http://localhost:{SERVER_PORT}/download/{model_id}',
                    'metadata': f'http://localhost:{SERVER_PORT}/metadata/{model_id}'
                }
            }
            
            # Add model metadata if available
            if model_metadata:
                metadata['model_metadata'] = model_metadata
            
            self._set_headers()
            self.wfile.write(json.dumps(metadata, indent=2).encode())
            return
        
        # Default - 404
        self._set_headers(404)
        self.wfile.write(json.dumps({
            'error': 'Not Found',
            'available_endpoints': [
                'GET /health',
                'GET /models',
                'GET /download/{model_id}',
                'GET /metadata/{model_id}'
            ]
        }).encode())
    
    def log_message(self, format, *args):
        """Override for custom logging"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Start the HTTP server"""
    print("=" * 60)
    print("  ML Model HTTP Server")
    print("=" * 60)
    print(f"  Host: {SERVER_HOST}")
    print(f"  Port: {SERVER_PORT}")
    print(f"  Models Base Path: {MODEL_BASE_PATH}")
    print(f"  API Key: {API_KEY[:8]}...")
    print("=" * 60)
    
    # Verificar modelos
    print("\nChecking models...")
    for model_id, config in AVAILABLE_MODELS.items():
        full_path = os.path.join(MODEL_BASE_PATH, config['path'])
        exists = os.path.exists(full_path)
        status = "✓" if exists else "✗"
        size = os.path.getsize(full_path) if exists else 0
        print(f"  {status} {model_id}: {config['description']}")
        print(f"     Path: {config['path']}")
        print(f"     Size: {size:,} bytes" if exists else f"     Size: FILE NOT FOUND")
        print(f"     URL: http://localhost:{SERVER_PORT}/download/{model_id}")
    
    print("\n" + "=" * 60)
    print("  Server starting...")
    print("=" * 60)
    print(f"\n  Access at: http://localhost:{SERVER_PORT}/models")
    print(f"  Health check: http://localhost:{SERVER_PORT}/health")
    print("\n  Press Ctrl+C to stop\n")
    
    server = HTTPServer((SERVER_HOST, SERVER_PORT), ModelHTTPHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()
        print("Server stopped.")


if __name__ == '__main__':
    main()
