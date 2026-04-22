from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session
import mysql.connector
from werkzeug.security import check_password_hash
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'your_secret_key_here' # In a real app, use a secure random key

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',
    'database': 'vaccine_db'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Route to serve images
@app.route('/image/<path:filename>')
def serve_image(filename):
    return send_from_directory('image', filename)

@app.route('/')
def index():
    return render_template('get-started-page.html')

@app.route('/login-page.html')
def login_page():
    return render_template('login-page.html')

@app.route('/registration.html')
def registration_page():
    return render_template('registration.html')

@app.route('/monitoring-checklist.html')
def monitoring_page():
    return render_template('monitoring-checklist.html')

@app.route('/records.html')
def records_page():
    return render_template('records.html')

@app.route('/reminder-settings.html')
def reminder_settings_page():
    return render_template('reminder-settings.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/register_patient', methods=['POST'])
def register_patient():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert patient
        cursor.execute("""
            INSERT INTO patients (name, birthday, phone, address, bite_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['name'], data['birthday'], data['phone'], data['address'], data['biteDate']))
        
        patient_id = cursor.lastrowid
        
        # Insert schedules
        for dose in data['fullSchedule']:
            cursor.execute("""
                INSERT INTO schedules (patient_id, label, date, time, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (patient_id, dose['label'], dose['date'], dose['time'], dose.get('status', 'Pending')))
            
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': 'Patient registered successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/patients', methods=['GET'])
def get_patients():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM patients")
        patients = cursor.fetchall()
        
        for patient in patients:
            cursor.execute("SELECT * FROM schedules WHERE patient_id = %s", (patient['id'],))
            # Convert date/time objects to strings for JSON
            schedules = cursor.fetchall()
            for s in schedules:
                s['date'] = s['date'].strftime('%Y-%m-%d')
                s['time'] = str(s['time'])
            patient['fullSchedule'] = schedules
            patient['birthday'] = patient['birthday'].strftime('%Y-%m-%d')
            patient['bite_date'] = patient['bite_date'].strftime('%Y-%m-%d')
            
        cursor.close()
        conn.close()
        return jsonify(patients)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/update_dose_status', methods=['POST'])
def update_dose_status():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE schedules SET status = %s WHERE id = %s
        """, (data['status'], data['doseId']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/complete_treatment', methods=['POST'])
def complete_treatment():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patients SET completed = TRUE WHERE id = %s
        """, (data['patientId'],))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete_patient', methods=['POST'])
def delete_patient():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Due to ON DELETE CASCADE on schedules, deleting the patient will also delete their schedules
        cursor.execute("DELETE FROM patients WHERE id = %s", (data['patientId'],))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
