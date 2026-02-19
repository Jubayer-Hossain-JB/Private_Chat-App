import customtkinter as ctk
import qrcode
import multiprocessing
from PIL import Image
import webbrowser
import web
import soket
import socket
from ctypes import windll
import os
from shutil import rmtree

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)


class Window(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QR Code Generator")
        self.geometry("400x520")
        self.iconbitmap(os.path.join(os.path.dirname(os.path.realpath(__file__)),'icon.ico'))
        self.overrideredirect(True)
        self.config(bg='#5b5b5b') 
        self.attributes('-transparentcolor', '#5b5b5b')

        # Initialize drag functionality variables
        self._drag_start_x = 0
        self._drag_start_y = 0

        # Main frame to hold all widgets
        self.main_frame = ctk.CTkFrame(self, border_width=8, border_color="#4d4949", corner_radius=40, bg_color="#5b5b5b")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tframe = ctk.CTkFrame(self.main_frame, fg_color="#4d4949", height=25, width= 320, corner_radius=20)
        tframe.place(relx=0.5,y=0, anchor='n')
        ctk.CTkFrame(tframe,fg_color="#4d4949", width=320, height=10,corner_radius=0).place(x=0,y=0)

        # Image display label
        self.image_label = ctk.CTkLabel(self.main_frame, text="QR Code will appear here", 
                                        width=300, height=300, fg_color="white", corner_radius=10)
        self.image_label.pack(pady=30)
        ctk.CTkLabel(self.main_frame, text="The backend engine is running. Now scan the above QRcode or Click the button below or go to the hyper link below.", wraplength=350, compound="left").place(y=375, relx= 0.5, anchor='s')
        # Text display label
        self.open_page = ctk.CTkButton(
            master=self,
            text="Open Website",
            command=self.open_browser,
            width=200,
            height=40,
            corner_radius=8,
            font=("Arial", 14),
            
        )
        self.open_page.place(y=410, relx= 0.5, anchor='center')

        # Custom close button
        self.close_button = ctk.CTkButton(self.main_frame, text="✕", width=60, height=40, 
                                          fg_color="#6b0000", font=("Arial", 21),
                                          command=self.close ,hover_color="#2f0909")
        self.close_button.pack(pady=20,side='bottom')
        self.update_display(f'http://{IPAddr}:8080')
        
        # Bind drag events 
        self.bind_tree(self.main_frame, "<Button-1>", self.start_drag)
        self.bind_tree(self.main_frame, "<B1-Motion>", self.on_drag)
        self.close_button.bind("<Button-1>", lambda e: self.close())  # Prevent drag when clicking button
        # self.main_frame.bind("<Button-1>", self.start_drag)
        # self.main_frame.bind("<B1-Motion>", self.on_drag)

    def close(self):
        self.destroy()
        message_server_p.terminate()
        web_server_p.terminate()
        message_server_p.join()
        web_server_p.join()
        mng.shutdown()
        dir = os.path.join(os.getenv('APPDATA'), "Private_Chat_App", "uploads")
        rmtree(dir)
        os.makedirs(dir)
    def bind_tree(self, widget, event, callback):
        widget.bind(event, callback)
        for child in widget.winfo_children():
            self.bind_tree(child, event, callback)
    
    def start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def on_drag(self, event):
        x = self.winfo_x() + (event.x - self._drag_start_x)
        y = self.winfo_y() + (event.y - self._drag_start_y)
        self.geometry(f"+{x}+{y}")

    def update_display(self, text):
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr.clear()
        del qr
        pil_image = Image.new("RGB", (300, 300), "white")
        pil_image.paste(img.resize((300, 300)), (0, 0))

        # Convert to CTkImage
        ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(300, 300))
        self.image_label.configure(image=ctk_image, text="")
        self.open_page.configure(command=lambda:self.open_browser(text), text=f'Click to open http://{IPAddr}:8080')
    def open_browser(self, site_address):
        webbrowser.open(site_address)

def set_appwindow(root):
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    # re-assert the new window style
    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())
def remove_splash_screen():
    #Remove Splsh Screen``
    if "NUITKA_ONEFILE_PARENT" in os.environ:
        import tempfile
        splash_filename = os.path.join(
            tempfile.gettempdir(),
            "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"])
        )
        if os.path.exists(splash_filename):
            os.unlink(splash_filename)

def web_server(shared_dict):
    shared_dict['uids'] = web.uids
    shared_dict['uids_users'] = web.uids_users
    web.shared_dict = shared_dict
    web.run(host=IPAddr, port=8080, server='waitress', threads=4)
def run_message_server(shared_dict):
    socket_server = soket.Messager_Server(shared_dict)
    socket_server.run_server()
if __name__ == "__main__":
    multiprocessing.freeze_support()
    mng =  multiprocessing.Manager()
    shared_dict = mng.dict()
    message_server_p = multiprocessing.Process(target=run_message_server, args=(shared_dict,))
    web_server_p = multiprocessing.Process(target=web_server, args=(shared_dict,))
    message_server_p.daemon=True
    web_server_p.daemon=True
    message_server_p.start()
    web_server_p.start()

    GWL_EXSTYLE = -20
    WS_EX_APPWINDOW = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    window = Window()
    window.eval('tk::PlaceWindow . center')
    window.after(10, lambda: set_appwindow(root=window))
    window.after(300, remove_splash_screen)
    window.mainloop()
