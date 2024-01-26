# Imports:
from flask import Flask, render_template

# Flask constructor:
app = Flask(__name__)
app.secret_key = 'lvc4s'

# Home route:
@app.route('/')
def home():
    return render_template('index.html')

# Overall execution:
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
