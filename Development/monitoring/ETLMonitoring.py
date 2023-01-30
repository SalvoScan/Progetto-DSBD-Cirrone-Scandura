from flask import Flask, request
import os

app = Flask(__name__)

content = {}

@app.route("/setDati", methods=['POST'])
def getTiming():
    global content
    content = request.json
    return ""

@app.route("/getDati", methods=['GET'])
def dati():
    global content
    return content

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8500))
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=port)