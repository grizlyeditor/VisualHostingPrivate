from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get('code', '')
    
    try:
        # Create temp file
        with open('temp.py', 'w') as f:
            f.write(code)
        
        # Execute the code
        result = subprocess.run(
            ['python', 'temp.py'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Clean up
        os.remove('temp.py')
        
        if result.returncode == 0:
            return jsonify({'success': True, 'output': result.stdout})
        return jsonify({'success': False, 'output': result.stderr})
    
    except Exception as e:
        return jsonify({'success': False, 'output': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
