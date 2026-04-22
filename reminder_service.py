import mysql.connector
import datetime
import time
import logging
from sms_handler import GSMModem

# Database configuration (matching app.py)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',
    'database': 'vaccine_db'
}

# Modem configuration
MODEM_PORT = 'COM3'  # Change this to your actual modem port (e.g., COM4, COM5)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='reminder_service.log',
    filemode='a'
)

# Add a console handler to also print to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def get_db_connection():
    return mysql.connector.connect(**db_config)

def check_and_send_reminders():
    logging.info("Checking for upcoming appointments...")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        today = datetime.date.today()
        three_days_later = today + datetime.timedelta(days=3)
        
        modem = GSMModem(port=MODEM_PORT)
        
        # 1. Check for appointments in 3 days
        cursor.execute("""
            SELECT s.id, s.label, s.date, s.time, p.name, p.phone 
            FROM schedules s
            JOIN patients p ON s.patient_id = p.id
            WHERE s.date = %s AND s.status = 'Pending' AND s.sent_reminder_3d = FALSE
        """, (three_days_later,))
        
        reminders_3d = cursor.fetchall()
        for r in reminders_3d:
            message = f"Reminder: Hello {r['name']}, you have a {r['label']} appointment on {r['date']} at {r['time']}. Please be ready."
            if modem.send_sms(r['phone'], message):
                cursor.execute("UPDATE schedules SET sent_reminder_3d = TRUE WHERE id = %s", (r['id'],))
                conn.commit()
                logging.info(f"3-day reminder sent to {r['name']} ({r['phone']})")

        # 2. Check for appointments today
        cursor.execute("""
            SELECT s.id, s.label, s.date, s.time, p.name, p.phone 
            FROM schedules s
            JOIN patients p ON s.patient_id = p.id
            WHERE s.date = %s AND s.status = 'Pending' AND s.sent_reminder_today = FALSE
        """, (today,))
        
        reminders_today = cursor.fetchall()
        for r in reminders_today:
            message = f"Urgent Reminder: Hello {r['name']}, your {r['label']} appointment is TODAY at {r['time']}. See you at the clinic."
            if modem.send_sms(r['phone'], message):
                cursor.execute("UPDATE schedules SET sent_reminder_today = TRUE WHERE id = %s", (r['id'],))
                conn.commit()
                logging.info(f"Same-day reminder sent to {r['name']} ({r['phone']})")

        cursor.close()
        conn.close()
        modem.disconnect()

    except Exception as e:
        logging.error(f"Error in reminder service: {e}")
        if conn:
            conn.close()

def main():
    logging.info("Starting Vaccine Reminder Service...")
    while True:
        try:
            check_and_send_reminders()
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
        
        # Check every 1 minute (60 seconds) for testing
        logging.info("Sleeping for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    main()
