import tkinter as tk
import tkinter.messagebox as messagebox
from threading import Thread
import re

class CodeDisplay:
    def __init__(self):
        pass
        
    def __call__(self, text):
        text = re.sub(r'```(.*\n?)', '', text)  
        display_thread = Thread(target=self.__display, args=(text,))
        display_thread.start()

    def __display(self, code):
        root = tk.Tk()
        text_editor = TextEditorGUI(root)
        text_editor.insert_text(code)
        root.mainloop()
    

class TextEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Example")
        self.root.config(bg="#88769c")

        # Create a frame to hold the text area with padding
        text_frame = tk.Frame(self.root, padx=5, pady=5)
        text_frame.pack(expand=True, fill="both")

        # Create the vertical scrollbar
        v_scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create the horizontal scrollbar
        h_scrollbar = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create the text area with a border and set it to read-only
        self.text_area = tk.Text(text_frame, wrap="word", 
                                 state=tk.DISABLED, 
                                 bd=2, 
                                 highlightthickness=1,
                                 yscrollcommand=v_scrollbar.set, 
                                 xscrollcommand=h_scrollbar.set)
        self.text_area.pack(expand=True, fill="both")

        # Configure the scrollbars to scroll the text area
        v_scrollbar.config(command=self.text_area.yview)
        h_scrollbar.config(command=self.text_area.xview)

        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.TOP, fill=tk.X)

        self.copy_button = tk.Button(button_frame, 
                                     text="Copy to Clipboard", 
                                     command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.RIGHT, padx=5)

    def copy_to_clipboard(self):
        text_to_copy = self.text_area.get("1.0", tk.END).strip()
        if text_to_copy:
            self.root.clipboard_clear()
            self.root.clipboard_append(text_to_copy)
            messagebox.showinfo("Success", "Text copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No text to copy!")

    def insert_text(self, text_to_insert):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text_to_insert)
        self.text_area.config(state=tk.DISABLED)





