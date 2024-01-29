# Imports:
from flask import Flask, render_template

from routes.kml_compiler_route import kml_compiler_bp

# Flask constructor:
app = Flask(__name__)
app.secret_key = 'lvc4s'

app.register_blueprint(kml_compiler_bp)

# Home route:
@app.route('/')
def home():
    return render_template('index.html')

# Home route:
@app.route('/error')
def error():
    return render_template('error.html')

# Overall execution:
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
