import pandas as pd
import webbrowser
import urllib.parse
import time
import pyautogui
import logging
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import messagebox

logging.basicConfig(filename='message_log.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

def remove_trailing_zeros(number):
    if isinstance(number, float) and number.is_integer():
        return int(number)
    return number

def send_whatsapp_message_via_url(phone_number, message, name, recipient, retries=3):
    for attempt in range(retries):
        
        try:
            print(f"Drafting message for {name}'s {recipient} phone: {phone_number}")
            
            encoded_message = urllib.parse.quote(message)
            webbrowser.open(f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}")
            time.sleep(5)  # Give enough time for WhatsApp Web to load and draft the message
            pyautogui.press("enter")  # Automatically press "Enter" to send the message
            time.sleep(1)  # Wait for the message to be sent
            pyautogui.hotkey("ctrl", "w")  # Close the current browser tab
            print(f"Message sent and tab closed for {name}'s {recipient} phone successfully!")
            logging.info(f"Message sent and tab closed for {name}'s {recipient} phone successfully!")
            return True
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {str(e)}")
            logging.error(f"Attempt {attempt+1} failed: {str(e)}")
           
    print(f"Failed to send message and close tab for {name}'s {recipient} phone after {retries} attempts.")
    logging.error(f"Failed to send message and close tab for {name}'s {recipient} phone after {retries} attempts.")
    return False

def create_combined_message(name, roll_no, exams, recipient_type):
    greeting = "*🗓 Greetings from Anees Defence Career Institute Pune (ADCI) 🗓*\n\n"
    if recipient_type == "student":
        message = (f"{greeting}Dear {name},\n\n"
                   f"🧾 Your Academic progress for the following exams is as below: 🧾\n\n")
    else:
        message = (f"{greeting}Dear Parent,\n\n"
                   f"🧾 The Academic progress detail of your ward {name} for the following exams is as below: 🧾\n\n")

    message += f"📝 Roll No: {roll_no}\n\n"

    for exam, marks in exams.items():
        if marks == "Absent":
            message += f"📊 {exam} Exam details -\nTotal Marks - Absent\n\n"
        else:
            total = "300" if "MATHS" in exam else "600"
            message += f"📊 {exam} Exam details -\nTotal Marks - {marks}/{total}\n\n"

    message += ("Regards,\nTeam ADCI\n\n"
                f"📌 Note- NDA DAILY MATHS/GAT- OBJECTIVE TESTS \n"
                f"✏PARENTS Do visit the Academy on a regular basis for your ward's progress.\n"
                f"✏Check the Official ADCI Parents-Students WhatsApp group daily for new informative updates from ADCI.")
    
    return message

def format_date(date_value):
    if pd.isna(date_value):
        return "N/A"
    if isinstance(date_value, pd.Timestamp):
        
        return date_value.strftime('%d-%m-%Y')
    return str(date_value)


def send_messages(file_path, status_label):
    try:
        df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
        
        messages_sent = 0


        for _, row in df.iterrows():
            name = row['Name']
            student_phone_number = remove_trailing_zeros(row['Student Contact No.'])
            father_phone_number = remove_trailing_zeros(row['Father/Guardian Contact No.'])
            mother_phone_number = remove_trailing_zeros(row['Mother/Guardian Contact No.'])
            roll_no = row['Roll No']
            
            exams = {format_date(row[f'Exam{i}']): remove_trailing_zeros(row[f'Total Marks{i}']) if not pd.isna(row[f'Total Marks{i}']) else "Absent" 
                     for i in range(1, (len(df.columns) - 4) // 2 + 1) 
                     if f'Exam{i}' in df.columns and f'Total Marks{i}' in df.columns}
            
            student_message = create_combined_message(name, roll_no, exams, "student")
            parent_message = create_combined_message(name, roll_no, exams, "parent")

            if pd.notna(student_phone_number) and str(student_phone_number).strip():
                full_student_phone_number = f"+91{student_phone_number}"
                if send_whatsapp_message_via_url(full_student_phone_number, student_message, name, "student"):
                    messages_sent += 1
            else:
                print(f"Skipping student message for {name} due to missing phone number")
                logging.info(f"Skipping student message for {name} due to missing phone number")
                

            if pd.notna(father_phone_number) and str(father_phone_number).strip():
                full_father_phone_number = f"+91{father_phone_number}"
                if send_whatsapp_message_via_url(full_father_phone_number, parent_message, name, "father"):
                    messages_sent += 1
            else:
                print(f"Skipping father message for {name} due to missing phone number")
                logging.info(f"Skipping father message for {name} due to missing phone number")

            if pd.notna(mother_phone_number) and str(mother_phone_number).strip():
                full_mother_phone_number = f"+91{mother_phone_number}"
                if send_whatsapp_message_via_url(full_mother_phone_number, parent_message, name, "mother"):
                    messages_sent += 1
            else:
                print(f"Skipping mother message for {name} due to missing phone number")
                logging.info(f"Skipping mother message for {name} due to missing phone number")

          
        status_label.config(text=f"Messages sent successfully! Total sent: {messages_sent}" if messages_sent > 0 else "No messages to send.")

    except Exception as e:
        print(f"Error reading file or sending messages: {str(e)}")
        logging.error(f"Error reading file or sending messages: {str(e)}")
        status_label.config(text=f"Error: {str(e)}")
class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("WhatsApp Message Sender - GAT and MATHS")
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
