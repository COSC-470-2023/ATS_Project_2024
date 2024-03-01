from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/configuration')
def configuration():
    return render_template('configuration.html')

if __name__ == '__main__':
    app.run(debug=True)