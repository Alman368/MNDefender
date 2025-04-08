from flask import Flask, render_template, url_for
app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
