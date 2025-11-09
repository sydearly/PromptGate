from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'PromptGate Flask environment is live!'

if __name__ == '__main__':
    app.run(debug=True)
