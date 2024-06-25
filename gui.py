import tkinter as tk
from tkinter import ttk, scrolledtext
import serial
import serial.tools.list_ports
import sv_ttk
from time import sleep
import threading

class SerialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Super Serial")
        self.root.geometry("790x450")
        self.root.resizable(False, False)

        self.ser = None
        self.reader_window = None

        sv_ttk.set_theme("dark")
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TEntry", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12))

        self.main_frame = ttk.Frame(root, padding="20 20 20 20")
        self.main_frame.pack(fill="both", expand=True)

        self.create_widgets()

    def create_widgets(self):
        port_label = ttk.Label(self.main_frame, text="Port série :")
        port_label.grid(row=0, column=0, padx=10, pady=10, sticky="W")

        self.port_combobox = ttk.Combobox(self.main_frame, values=self.list_serial_ports(), state="readonly")
        self.port_combobox.grid(row=0, column=1, padx=10, pady=10)

        self.bitrate_label = ttk.Label(self.main_frame, text="Bitrate :")
        self.bitrate_label.grid(row=1, column=0, padx=10, pady=10, sticky="W")

        self.bitrate_combobox = ttk.Combobox(self.main_frame, values=[75, 110, 300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200], state="readonly")
        self.bitrate_combobox.set("9600")
        self.bitrate_combobox.grid(row=1, column=1, padx=10, pady=10)

        connect_button = ttk.Button(self.main_frame, text="Connecter", command=self.connect_to_port)
        connect_button.grid(row=0, column=2, padx=10, pady=10)

        disconnect_button = ttk.Button(self.main_frame, text="Déconnecter", command=self.disconnect_from_port)
        disconnect_button.grid(row=0, column=3, padx=10, pady=10)

        self.status_label = ttk.Label(self.main_frame, text="Déconnecté", foreground="red")
        self.status_label.grid(row=2, columnspan=4, pady=10)

        self.loginOneAccess_button = ttk.Button(self.main_frame, text="Login", command=self.routeur_login)
        self.loginOneAccess_button.grid(row=1, column=3, padx=10, pady=10)

        open_reader_button = ttk.Button(self.main_frame, text="Open serial reader", command=self.open_reader_window)
        open_reader_button.grid(row=1, column=4, padx=10, pady=10)

        command_label = ttk.Label(self.main_frame, text="Commande :")
        command_label.grid(row=3, column=0, padx=10, pady=10, sticky="W")

        self.command_entry = ttk.Entry(self.main_frame, width=40)
        self.command_entry.grid(row=3, column=1, padx=10, pady=10, columnspan=2)

        send_button = ttk.Button(self.main_frame, text="Envoyer", command=self.send_command)
        send_button.grid(row=3, column=3, padx=10, pady=10)

        self.response_text = scrolledtext.ScrolledText(self.main_frame, width=60, height=10, wrap=tk.WORD)
        self.response_text.grid(row=4, columnspan=4, padx=10, pady=10)

        clear_button = ttk.Button(self.main_frame, text="Clear result", command=self.clear_text)
        clear_button.grid(row=5, column=3)

        quit_button = ttk.Button(self.main_frame, text="Quitter", command=self.quit_application)
        quit_button.grid(row=5, columnspan=4, pady=10)
        
    def list_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect_to_port(self):
        selected_port = self.port_combobox.get()
        selected_bitrate = self.bitrate_combobox.get()
        if selected_port and selected_bitrate:
            try:
                self.ser = serial.Serial(selected_port, int(selected_bitrate), timeout=1)
                self.status_label.config(text=f"Connecté à {selected_port} à {selected_bitrate} bps", foreground="green")
            except Exception as e:
                self.status_label.config(text=f"Erreur: {e}", foreground="red")

    def disconnect_from_port(self):
        if self.ser and self.ser.is_open:
            self.ser.write("exit".encode('utf-8'))
            self.ser.close()
            self.status_label.config(text="Déconnecté", foreground="red")

    def send_command(self):
        if self.ser and self.ser.is_open:
            command = self.command_entry.get()
            command_to_send = command + "\r"
            self.ser.write(command_to_send.encode('utf-8'))
            sleep(1)  # Short delay to allow response to be received
            response = self.ser.read(self.ser.inWaiting()).decode()
            self.response_text.insert(tk.END, f"{response}\n")

    def quit_application(self):
        self.disconnect_from_port()
        self.root.quit()
    
    def routeur_login(self):
        username = "\r" #YOUR USERNAME
        password = "\r" #YOUR PASSWORD
        commande = "configure terminal\r"
        quit = "exit\r"
        sleep(1)
        self.ser.write(username.encode('utf-8'))
        self.ser.write(username.encode('utf-8'))
        sleep(3)
        self.ser.write(username.encode('utf-8'))
        sleep(2)
        response = self.ser.read(self.ser.inWaiting()).decode('utf-8')
        print(response)
        self.ser.write(password.encode('utf-8'))
        sleep(2)
        self.ser.write(commande.encode('utf-8'))
        sleep(2)
        response1 = self.ser.read(self.ser.inWaiting()).decode('utf-8')
        if 'ENTER' in response1.upper():
            self.ser.write(quit.encode('utf-8'))
        
    def clear_text(self):
        self.response_text.delete('1.0', tk.END)

    def open_reader_window(self):
        if self.ser and self.ser.is_open:
            self.reader_window = tk.Toplevel(self.root)
            self.reader_window.title("Serial Reader")
            self.reader_window.geometry("600x400")
            self.reader_text = scrolledtext.ScrolledText(self.reader_window, width=70, height=20, wrap=tk.WORD, state='disabled')
            self.reader_text.pack(fill="both", expand=True)
            self.read_serial_data()

    def read_serial_data(self):
        if self.ser and self.ser.is_open:
            threading.Thread(target=self._read_serial_data_thread).start()

    def _read_serial_data_thread(self):
        while self.ser and self.ser.is_open:
            data = self.ser.read(self.ser.inWaiting()).decode('utf-8')
            if data:
                self.reader_text.config(state='normal')
                self.reader_text.insert(tk.END, data)
                self.reader_text.config(state='disabled')
                self.reader_text.see(tk.END)
            sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialApp(root)
    root.mainloop()