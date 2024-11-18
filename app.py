from tkinter import *
from chatbot import get_response, bot_name

BG_GRAY = "#ABB2B9"
BG_COLOR = "#1E1E1E"
TEXT_COLOR = "#FFFFFF"
ENTRY_BG_COLOR = "#2C2C2C"
BUTTON_BG_COLOR = "#4CAF50"
BUTTON_TEXT_COLOR = "#FFFFFF"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"
class ChatApplication:
    
    def __init__(self):
        self.window = Tk()
        self.user_name = None
        self._setup_main_window()

    def run(self):
        self.window.mainloop()
        
    def _setup_main_window(self):
        self.window.title("Chat")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=470, height=550, bg=BG_COLOR)
        
        # Head label
        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR, text="Welcome", font=FONT_BOLD, pady=10)
        head_label.place(relwidth=1)
        
        # Divider
        line = Label(self.window, width=450, bg=BG_GRAY)
        line.place(relwidth=1, rely=0.07, relheight=0.012)
        
        # Text widget
        self.text_widget = Text(self.window, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, padx=5, pady=5)
        self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget.configure(cursor="arrow", state=DISABLED)
        
        # Scroll bar
        scrollbar = Scrollbar(self.text_widget)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.configure(command=self.text_widget.yview)
        
        # Bottom label
        bottom_label = Label(self.window, bg=BG_GRAY, height=80)
        bottom_label.place(relwidth=1, rely=0.825)
        
        # Message entry box
        self.msg_entry = Entry(bottom_label, bg=ENTRY_BG_COLOR, fg=TEXT_COLOR, font=FONT, borderwidth=2, relief="groove")
        self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)
        
        # Send button
        send_button = Button(bottom_label, text="Send", font=FONT_BOLD, width=20, bg=BUTTON_BG_COLOR, fg=BUTTON_TEXT_COLOR, command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)
        
    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        self._insert_message(msg, "You")
        
    def _insert_message(self, msg, sender):
        if not msg:
            return

        self.msg_entry.delete(0, END)
        msg1 = f"{sender}: {msg}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg1)
        self.text_widget.configure(state=DISABLED)
        
        msg2 = f"{bot_name}: {get_response(msg)}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg2)
        self.text_widget.configure(state=DISABLED)
        
        self.text_widget.see(END)

if __name__ == "__main__":
    print("Starting Chatbot Application...")
    app = ChatApplication()
    app.run()