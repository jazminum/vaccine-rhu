import serial
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GSMModem:
    def __init__(self, port='COM3', baudrate=115200, timeout=5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(1)
            logging.info(f"Connected to GSM Modem on {self.port}")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to GSM Modem: {e}")
            return False

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            logging.info("Disconnected from GSM Modem")

    def send_command(self, cmd, wait_time=1):
        if not self.ser or not self.ser.is_open:
            return None
        
        self.ser.write((cmd + '\r').encode())
        time.sleep(wait_time)
        response = self.ser.read_all().decode()
        return response

    def send_sms(self, phone_number, message):
        try:
            if not self.ser or not self.ser.is_open:
                if not self.connect():
                    return False

            logging.info(f"Sending SMS to {phone_number}...")
            
            # Set text mode
            self.send_command('AT+CMGF=1')
            
            # Set recipient
            self.ser.write(f'AT+CMGS="{phone_number}"\r'.encode())
            time.sleep(1)
            
            # Send message
            self.ser.write(f'{message}\x1A'.encode()) # \x1A is Ctrl+Z
            time.sleep(3)
            
            response = self.ser.read_all().decode()
            if 'OK' in response or '+CMGS:' in response:
                logging.info(f"SMS sent successfully to {phone_number}")
                return True
            else:
                logging.error(f"Failed to send SMS: {response}")
                return False

        except Exception as e:
            logging.error(f"Error in send_sms: {e}")
            return False

if __name__ == "__main__":
    # Test block
    modem = GSMModem(port='COM3') # Update with actual port
    if modem.connect():
        # Example: modem.send_sms("09123456789", "Test from iTegno W3800")
        modem.disconnect()
