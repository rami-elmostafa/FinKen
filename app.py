from flask import Flask, render_template
import os

app = Flask(__name__, static_folder='frontend')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/CreateNewUser')
def create_new_user():
    # Change this to whatever the new user creation page is once it is created
    return render_template('CreateNewUser.html')

@app.route("/ForgotPassword")
def forgot_password():
    # Change this to whatever the new forgot password page is once it is created
    return render_template('ForgotPassword.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
