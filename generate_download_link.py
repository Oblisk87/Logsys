
from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/download/<filename>')
def download_file(filename):
    directory = os.path.abspath(os.path.dirname(__file__))
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(port=5000)
