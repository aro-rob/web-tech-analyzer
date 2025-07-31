from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_website():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Check if we can find the CLI script
        cli_path = None
        possible_paths = [
            'src/cli.py',
            'cli.py', 
            'src/wappalyzer.py',
            'wappalyzer.py'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                cli_path = path
                break
        
        if not cli_path:
            return jsonify({'error': 'CLI script not found'}), 500
        
        # Run the webappanalyzer CLI
        result = subprocess.run(
            ['python', cli_path, url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return jsonify({'error': f'CLI error: {result.stderr}'}), 500
        
        # Try to parse as JSON, fallback to raw output
        try:
            analysis = json.loads(result.stdout)
        except:
            # If not JSON, return raw output
            analysis = {'raw_output': result.stdout, 'url': url}
        
        return jsonify(analysis)
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Analysis timeout'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'})

@app.route('/debug', methods=['GET'])
def debug_files():
    # Debug endpoint to see what files exist
    files = []
    for root, dirs, filenames in os.walk('.'):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return jsonify({'files': files[:50]})  # Limit to first 50 files

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
