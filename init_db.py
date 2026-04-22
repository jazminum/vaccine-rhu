import mysql.connector
from werkzeug.security import generate_password_hash

def init_db():
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="vaccine_db"
        )
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Table 'users' created or already exists.")

        # Create patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                birthday DATE NOT NULL,
                phone VARCHAR(20) NOT NULL,
                address TEXT NOT NULL,
                bite_date DATE NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Table 'patients' created or already exists.")

        # Create schedules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                label VARCHAR(100) NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                status ENUM('Pending', 'Done', 'Missed') DEFAULT 'Pending',
                sent_reminder_3d BOOLEAN DEFAULT FALSE,
                sent_reminder_today BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
        """)
        print("Table 'schedules' created or already exists.")

        # Check if default admin exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if cursor.fetchone() is None:
            hashed_password = generate_password_hash("admin123")
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ("admin", hashed_password))
            conn.commit()
            print("Default user 'admin' created with password 'admin123'.")
        else:
            print("Default user 'admin' already exists.")

        cursor.close()
        conn.close()
        print("Database initialization completed successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    init_db()
