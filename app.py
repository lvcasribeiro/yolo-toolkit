# Imports:
from flask import Flask

from routes.main_route import main_bp
from routes.kml_compiler_route import kml_compiler_bp
from routes.metadata_extractor_route import metadata_extractor_bp
from routes.dataset_splitter_route import dataset_splitter_bp

# Flask constructor:
app = Flask(__name__)
app.secret_key = 'lvc4s'

app.register_blueprint(main_bp)
app.register_blueprint(kml_compiler_bp)
app.register_blueprint(metadata_extractor_bp)
app.register_blueprint(dataset_splitter_bp)

# Overall execution:
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
