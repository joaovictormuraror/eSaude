from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'esaude_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Mock database - in production, use a real database
users_db = {}
plans_db = {
    'ambulatorial': {
        'name': 'Plano de Saúde de Atendimento Ambulatorial',
        'price': 290,
        'description': 'Plano com cobertura apenas ambulatorial, ideal para quem busca economia e não precisa de internações.'
    },
    'hospitalar_sem_obst': {
        'name': 'Plano de Saúde Hospitalar – Sem Cobertura Obstétrica',
        'price': 350,
        'description': 'Plano hospitalar cobre internações, exames e cirurgias, mas exclui cuidados com gravidez e parto.'
    },
    'hospitalar_com_obst': {
        'name': 'Plano de Saúde Hospitalar – Com Cobertura Obstétrica',
        'price': 500,
        'description': 'Plano hospitalar com obstetrícia cobre internações, exames, cirurgias e cuidados completos com gestação e parto.'
    },
    'odontologico': {
        'name': 'Plano de Saúde Odontológico',
        'price': 250,
        'description': 'Cobertura completa para tratamentos odontológicos e cuidados bucais.'
    },
    'referencial': {
        'name': 'Plano de Saúde Referencial',
        'price': 700,
        'description': 'Plano premium com cobertura completa e acesso aos melhores profissionais.'
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        plan_number = request.form['plan_number']
        phone = request.form['phone']
        password = request.form['password']
        
        # Simple authentication check
        if email in users_db and users_db[email]['password'] == password:
            session['user'] = email
            session['user_data'] = users_db[email]
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.')
    
    return render_template('login.html')

@app.route('/plans')
def plans():
    return render_template('plans.html', plans=plans_db)

@app.route('/plan_details/<plan_id>')
def plan_details(plan_id):
    if plan_id not in plans_db:
        return redirect(url_for('plans'))
    
    plan = plans_db[plan_id]
    return render_template('plan_details.html', plan=plan, plan_id=plan_id)

@app.route('/register/personal', methods=['GET', 'POST'])
def register_personal():
    if request.method == 'POST':
        session['personal_info'] = {
            'name': request.form['name'],
            'email': request.form['email'],
            'birth_date': request.form['birth_date'],
            'address': request.form['address'],
            'cpf': request.form['cpf'],
            'gender': request.form['gender']
        }
        return redirect(url_for('register_health'))
    
    return render_template('register_personal.html')

@app.route('/register/health', methods=['GET', 'POST'])
def register_health():
    if 'personal_info' not in session:
        return redirect(url_for('register_personal'))
    
    if request.method == 'POST':
        session['health_info'] = {
            'blood_type': request.form['blood_type'],
            'surgeries': request.form['surgeries'],
            'addictions': request.form['addictions'],
            'medications': request.form['medications'],
            'family_cases': request.form['family_cases'],
            'allergies': request.form['allergies']
        }
        return redirect(url_for('register_general'))
    
    return render_template('register_health.html')

@app.route('/register/general', methods=['GET', 'POST'])
def register_general():
    if 'health_info' not in session:
        return redirect(url_for('register_health'))
    
    if request.method == 'POST':
        session['general_info'] = {
            'occupation': request.form['occupation'],
            'income': request.form['income'],
            'children': request.form['children'],
            'marital_status': request.form['marital_status'],
            'spouse_name': request.form['spouse_name']
        }
        return redirect(url_for('register_documents'))
    
    return render_template('register_general.html')

@app.route('/register/documents', methods=['GET', 'POST'])
def register_documents():
    if 'general_info' not in session:
        return redirect(url_for('register_general'))
    
    if request.method == 'POST':
        # Handle file uploads
        uploaded_files = {}
        for file_type in ['id_front', 'id_back', 'address_proof', 'income_proof', 'birth_certificate']:
            if file_type in request.files:
                file = request.files[file_type]
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    uploaded_files[file_type] = filename
        
        session['documents'] = uploaded_files
        return redirect(url_for('register_dependents'))
    
    return render_template('register_documents.html')

@app.route('/register/dependents', methods=['GET', 'POST'])
def register_dependents():
    if 'documents' not in session:
        return redirect(url_for('register_documents'))
    
    if request.method == 'POST':
        # Handle dependent documents
        dependent_files = {}
        for file_type in ['dep_id_front', 'dep_id_back', 'dep_address_proof', 'dep_income_proof', 'dep_birth_certificate']:
            if file_type in request.files:
                file = request.files[file_type]
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    dependent_files[file_type] = filename
        
        # Save all user data
        email = session['personal_info']['email']
        users_db[email] = {
            'password': 'temp123',  # In production, hash this
            'personal_info': session['personal_info'],
            'health_info': session['health_info'],
            'general_info': session['general_info'],
            'documents': session['documents'],
            'dependent_documents': dependent_files
        }
        
        # Clear session data
        for key in ['personal_info', 'health_info', 'general_info', 'documents']:
            session.pop(key, None)
        
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('login'))
    
    return render_template('register_dependents.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_data = session.get('user_data', {})
    return render_template('dashboard.html', user_data=user_data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
