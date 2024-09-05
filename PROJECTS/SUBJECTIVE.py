import pandas as pd
import webbrowser
import urllib.parse
import time
import pyautogui
import logging
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import messagebox


def remove_trailing_zeros(number):
    """Remove trailing zeros from float values."""
    
    if isinstance(number, float) and number.is_integer():
        return int(number)
    return number

def send_whatsapp_message_via_url(phone_number, message, name, recipient, retries=3):
    """Send a WhatsApp message using web browser and pyautogui."""
    for attempt in range(retries):
        try:
            print(f"Drafting message for {name}'s {recipient} phone: {phone_number}")
            encoded_message = urllib.parse.quote(message)
            webbrowser.open(f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}")
            time.sleep(5)  # Allow WhatsApp Web to load and draft the message
            pyautogui.press("enter")  # Automatically press "Enter" to send the message
            time.sleep(1)  # Wait for the message to be sent
            pyautogui.hotkey("ctrl", "w")  # Close the current browser tab
            logging.info(f"Message sent and tab closed for {name}'s {recipient} phone successfully!")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {name}'s {recipient} phone. Error: {str(e)}")
            logging.error(f"Attempt {attempt + 1} failed for {name}'s {recipient} phone. Error: {str(e)}")

    return False

def create_message(name, tests, recipient_type):
    """Create a message string based on recipient type."""
    greeting = "*🗓 Greetings from Anees Defence Career Institute Pune (ADCI) 🗓*\n\n"
    if recipient_type == "student":
        message = (f"{greeting}Dear {name},\n\n"
                   f"🧾 Your Academic progress for the following tests is as below: 🧾\n\n")
    else:
        message = (f"{greeting}Dear Parent,\n\n"
                   f"🧾 The Academic progress detail of your ward {name} for the following tests is as below: 🧾\n\n")
    
    message += "📊 Subjective test details -\n"

    for test_date, subjects_marks in tests.items():
        message += f"📅 Date: {test_date}\n"
        for subject, marks in subjects_marks.items():
            message += f"Subject: {subject}, Marks: {marks}\n"
        message += "\n"

    message += ("Regards,\nTeam ADCI\n\n"
                f"📌 Note- \n"
                f"✏Do visit the Academy on a regular basis for your ward's progress.\n"
                f"✏Check the Official ADCI Parents-Students WhatsApp group daily for new informative updates from ADCI.")
    
    return message

def format_date(date_value):
    """Format date for display."""
    if pd.isna(date_value):
        return "N/A"
    if isinstance(date_value, pd.Timestamp):
        return date_value.strftime('%d-%m-%Y')
    return str(date_value)

def send_messages(file_path, status_label):
    """Read the file and send messages to the contacts."""
    try:
        # Load the file into a DataFrame
        df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()

        messages_sent = 0

        for _, row in df.iterrows():
            name = row['Name']
            student_phone_number = remove_trailing_zeros(row['Student Contact No.'])
            father_phone_number = remove_trailing_zeros(row["Father/Guardian Contact No."])
            mother_phone_number = remove_trailing_zeros(row["Mother/Guardian Contact No."])

            # Group tests by date
            tests = {}
            for i in range(1, 11):  # Adjust range based on the maximum number of test dates
                test_date_col = f'Subjective date{i}'
                subjects_col = f'Subject{i}'
                marks_col = f'Subjective Marks{i}'

                if test_date_col in df.columns and subjects_col in df.columns and marks_col in df.columns:
                    test_date = format_date(row[test_date_col])
                    subject = row[subjects_col]
                    marks = remove_trailing_zeros(row[marks_col])
                    if pd.isna(marks):
                        marks = "Absent"
                    if test_date not in tests:
                        tests[test_date] = {}
                    tests[test_date][subject] = marks

            phone_numbers = {
                "student": f"+91{student_phone_number}" if pd.notna(student_phone_number) else None,
                "father": f"+91{father_phone_number}" if pd.notna(father_phone_number) else None,
                "mother": f"+91{mother_phone_number}" if pd.notna(mother_phone_number) else None
            }

            student_message = create_message(name, tests, "student")
            parent_message = create_message(name, tests, "parent")

            # Attempt to send messages
            for recipient, phone_number in phone_numbers.items():
                if phone_number:  # Only proceed if the phone number is not None
                    message = student_message if recipient == "student" else parent_message
                    if send_whatsapp_message_via_url(phone_number, message, name, recipient):
                        messages_sent += 1
                else:
                    print(f"Skipping message for {name}'s {recipient} - No phone number provided")
                    logging.info(f"Skipped message for {name}'s {recipient} - No phone number provided")

            

        status_label.config(text=f"Messages sent successfully! Total sent: {messages_sent}" if messages_sent > 0 else "No messages to send.")

    except Exception as e:
        print(f"Error reading file or sending messages: {str(e)}")
        logging.error(f"Error reading file or sending messages: {str(e)}")
        status_label.config(text=f"Error: {str(e)}")

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("WhatsApp Message Sender")
        self.geometry("600x400")
        self.configure(bg="#2c3e50")

        self.label = tk.Label(self, text="Drag and drop a CSV or XLSX file here", width=60, height=10, bg="#ecf0f1", fg="#2c3e50", relief="groove", bd=2)
        self.label.pack(padx=10, pady=20)
        self.label.bind("<Configure>", self.rounded_label)

        self.file_path = None
        self.label.drop_target_register(DND_FILES)
        self.label.dnd_bind('<<Drop>>', self.on_drop)

        self.send_button = tk.Button(self, text="Send Messages", command=self.on_send, bg="#3498db", fg="white", font=("Helvetica", 14), relief="raised", bd=3)
        self.send_button.pack(padx=10, pady=10)
        self.send_button.bind("<Configure>", self.rounded_button)

        self.status_label = tk.Label(self, text="", bg="#2c3e50", fg="white", font=("Helvetica", 10))
        self.status_label.pack(pady=5)

    def rounded_label(self, event):
        self.label.config(highlightthickness=3, highlightbackground="#3498db")
        self.label.update_idletasks()

    def rounded_button(self, event):

        self.send_button.config(highlightthickness=3, highlightbackground="#3498db")
        self.send_button.update_idletasks()

    def on_drop(self, event):
        self.file_path = event.data.strip("{}")
        self.label.config(text=f"File selected: {self.file_path}")

    def on_send(self):
        if self.file_path:
            self.status_label.config(text="Processing...")
            self.update()
            send_messages(self.file_path, self.status_label)
        else:
            messagebox.showwarning("No file selected", "Please drag and drop a CSV or XLSX file first")

if __name__ == '__main__':
    app = App()
    app.mainloop()