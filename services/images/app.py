from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from images'

@app.route('/healthz')
def health():
    return 'Healthy', 200

@app.route('/readyz')
def readyz():
    return 'Ready', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
