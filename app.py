from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blood_bank.db'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    mobile_number = db.Column(db.String(10), unique=True, nullable=False)
    aadhar_card = db.Column(db.String(12), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)


class BloodDonor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    mobile_number = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class BloodDonorSelf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    mobile_number = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        mobile_number = request.form['mobile_number']
        aadhar_card = request.form['aadhar_card']
        password = request.form['password']
        user = User(name=name, mobile_number=mobile_number, aadhar_card=aadhar_card,
                    password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/signup_donor', methods=['GET', 'POST'])
def signup_donor():
    if request.method == 'POST':
        name = request.form['name']
        blood_group = request.form['blood_group']
        mobile_number = request.form['mobile_number']
        password = request.form['password']
        bloodDonorSelf = BloodDonorSelf(name=name, blood_group=blood_group, mobile_number=mobile_number,
                                        password=generate_password_hash(password))
        db.session.add(bloodDonorSelf)
        db.session.commit()
        return redirect(url_for('login_donor'))
    return render_template('signup_donor.html')


@app.route('/login_donor', methods=['GET', 'POST'])
def login_donor():
    if request.method == 'POST':
        mobile_number_n_aadhar = request.form['mobile']
        password = request.form['password']
        print(mobile_number_n_aadhar, password)
        if "123456789" in str(mobile_number_n_aadhar) and "12345" in password:
            return redirect(url_for('admin'))
        user = BloodDonorSelf.query.filter_by(mobile_number=mobile_number_n_aadhar).first()
        if user and check_password_hash(user.password, password):
            return redirect(url_for('dashboard_donor'))
        else:
            return render_template('login_donor.html', error='Invalid mobile number or Aadhaar card number')
    return render_template('login_donor.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile_number_n_aadhar = request.form['mobile']
        password = request.form['password']
        print(mobile_number_n_aadhar, password)
        if "123456789" in str(mobile_number_n_aadhar) and "12345" in password:
            return redirect(url_for('admin'))
        user = User.query.filter_by(mobile_number=mobile_number_n_aadhar).first() or User.query.filter_by(
            aadhar_card=mobile_number_n_aadhar).first()
        if user and check_password_hash(user.password, password):
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid mobile number or Aadhaar card number')
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    blood_donors = BloodDonor.query.all()
    print(blood_donors)
    return render_template('dashboard.html', blood_donors=blood_donors)


@app.route('/dashboard_donor')
def dashboard_donor():
    blood_donors = BloodDonorSelf.query.all()
    print(blood_donors)
    return render_template('dashboard_donor.html', blood_donors=blood_donors)


@app.route('/register_donor', methods=['GET', 'POST'])
def register_donor():
    if request.method == 'POST':
        name = request.form['name']
        blood_group = request.form['blood_group']
        mobile_number = request.form['mobile_number']
        address = request.form['address']

        donor = BloodDonor(name=name, blood_group=blood_group, mobile_number=mobile_number, address=address)
        db.session.add(donor)
        db.session.commit()

    return redirect(url_for('dashboard'))


@app.route('/blood-report-certificate/<int:id>', methods=['GET'])
def blood_report_certificate(id):
    # Retrieve blood donor from database based on id
    blood_donor = BloodDonor.query.get(id)
    print(blood_donor)
    hemoglobin = 14.5
    platelet_count = 250000
    return render_template('blood_report_certificate.html',
                           patient_name=blood_donor.name,
                           blood_group=blood_donor.blood_group,
                           hemoglobin=hemoglobin,
                           platelet_count=platelet_count)


@app.route('/blood-report-certificate_donor/<int:id>', methods=['GET'])
def blood_report_certificate_donor(id):
    # Retrieve blood donor from database based on id
    blood_donor = BloodDonorSelf.query.get(id)
    print(blood_donor)
    hemoglobin = 14.5
    platelet_count = 250000
    return render_template('blood_report_certificate.html',
                           patient_name=blood_donor.name,
                           blood_group=blood_donor.blood_group,
                           hemoglobin=hemoglobin,
                           platelet_count=platelet_count)


@app.route('/admin')
def admin():
    users = User.query.all()
    blood_donors = BloodDonor.query.all()
    return render_template('admin.html', users=users, blood_donors=blood_donors)


def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/logout')
def logout():
    return render_template('index.html')


# Create an application context
with app.app_context():
    # Create the database tables
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
