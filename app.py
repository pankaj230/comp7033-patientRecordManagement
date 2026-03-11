from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    # Process registration logic here
    return "Registration successful!"


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']
    return f"Logged in as {role} with email {email}"

@app.route('/patient_dashboard')
def patient_dashboard():
    return render_template('roleSpecificDashboard/patient_dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)
