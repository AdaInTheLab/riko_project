from flask import Flask, render_template
from modules.core import load_personas
from modules.chat import chat_bp
from modules.media import media_bp
from modules.forge import forge_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(chat_bp)
app.register_blueprint(media_bp)
app.register_blueprint(forge_bp)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    load_personas()
    print("Lab Terminal entry point synchronized. Routes registered.")
    app.run(debug=True, port=8081)
