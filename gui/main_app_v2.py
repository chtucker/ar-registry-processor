import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from datetime import datetime
import sys

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.registry_processor import RegistryProcessor

class RegistryAppV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Arkansas Registry Processor - Improved Basic UI")
        self.root.geometry("800x600")
        self.selected_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.processing = False
        self.processor = None
        self.names = []
        self.create_widgets()
        self.set_default_output_path()

    def create_widgets(self):
        # Use a main frame for padding and background
        main_frame = tk.Frame(self.root, padx=15, pady=15, bg='#f7f7f7')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = tk.Label(main_frame, text="Arkansas Registry Processor", font=("Arial", 16, "bold"), bg='#f7f7f7')
        title.grid(row=0, column=0, columnspan=3, pady=(0, 5), sticky="w")
        subtitle = tk.Label(main_frame, text="IMPROVED BASIC MODE", font=("Arial", 10), bg='#f7f7f7')
        subtitle.grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky="w")

        # File selection
        tk.Label(main_frame, text="Excel File:", bg='#f7f7f7').grid(row=2, column=0, sticky="e")
        file_entry = tk.Entry(main_frame, textvariable=self.selected_file, width=40, state='readonly', relief=tk.SUNKEN, borderwidth=2)
        file_entry.grid(row=2, column=1, sticky="we", padx=5)
        browse_btn = tk.Button(main_frame, text="Browse", command=self.browse_file, bg='#e0eaff', font=("Arial", 10, "bold"))
        browse_btn.grid(row=2, column=2, sticky="w", padx=5)

        # Output location
        tk.Label(main_frame, text="Output File:", bg='#f7f7f7').grid(row=3, column=0, sticky="e")
        out_entry = tk.Entry(main_frame, textvariable=self.output_file, width=40, state='readonly', relief=tk.SUNKEN, borderwidth=2)
        out_entry.grid(row=3, column=1, sticky="we", padx=5)
        change_btn = tk.Button(main_frame, text="Change", command=self.change_output_location, bg='#e0eaff', font=("Arial", 10, "bold"))
        change_btn.grid(row=3, column=2, sticky="w", padx=5)

        # Names list
        names_frame = tk.LabelFrame(main_frame, text="Names to Process", padx=5, pady=5, bg='#f0f0f0', font=("Arial", 11, "bold"))
        names_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(15, 5))
        names_frame.grid_rowconfigure(0, weight=1)
        names_frame.grid_columnconfigure(0, weight=1)
        self.names_list = tk.Listbox(names_frame, height=10, width=60, relief=tk.SUNKEN, borderwidth=2, font=("Arial", 10))
        self.names_list.grid(row=0, column=0, sticky="nsew")
        self.names_scroll = tk.Scrollbar(names_frame, orient=tk.VERTICAL, command=self.names_list.yview)
        self.names_scroll.grid(row=0, column=1, sticky="ns")
        self.names_list.config(yscrollcommand=self.names_scroll.set)
        # Placeholder for names list
        self.names_list.insert(tk.END, "No names loaded.")
        self.names_list.config(state='disabled')

        # Controls
        ctrl_frame = tk.Frame(main_frame, bg='#f7f7f7')
        ctrl_frame.grid(row=5, column=0, columnspan=3, pady=10)
        self.start_btn = tk.Button(ctrl_frame, text="Start Processing", command=self.start_processing, bg='#d1ffd1', font=("Arial", 11, "bold"))
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = tk.Button(ctrl_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED, bg='#ffe0e0', font=("Arial", 11, "bold"))
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.open_results_btn = tk.Button(ctrl_frame, text="Open Results", command=self.open_results, state=tk.DISABLED, bg='#e0eaff', font=("Arial", 11, "bold"))
        self.open_results_btn.pack(side=tk.LEFT, padx=5)

        # Progress
        self.progress_label = tk.Label(main_frame, text="Ready to process", font=("Arial", 10), bg='#f7f7f7')
        self.progress_label.grid(row=6, column=0, columnspan=3, pady=(0, 5), sticky="w")

        # Status log
        status_frame = tk.LabelFrame(main_frame, text="Status Log", padx=5, pady=5, bg='#f0f0f0', font=("Arial", 11, "bold"))
        status_frame.grid(row=7, column=0, columnspan=3, sticky="nsew", pady=(5, 0))
        status_frame.grid_rowconfigure(0, weight=1)
        status_frame.grid_columnconfigure(0, weight=1)
        self.status_text = tk.Text(status_frame, height=6, width=80, state='normal', relief=tk.SUNKEN, borderwidth=2, font=("Arial", 10))
        self.status_text.grid(row=0, column=0, sticky="nsew")
        status_scroll = tk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        status_scroll.grid(row=0, column=1, sticky="ns")
        self.status_text.config(yscrollcommand=status_scroll.set)
        # Placeholder for status log
        self.status_text.insert(tk.END, "Status messages will appear here.")
        self.status_text.config(state='disabled')

        # Configure grid weights for resizing
        main_frame.grid_rowconfigure(4, weight=2)
        main_frame.grid_rowconfigure(7, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Set default file text
        self.selected_file.set("No file selected.")
        self.output_file.set("No output file selected.")

        self.log_status("Application started. Select an Excel file to begin.")

    def set_default_output_path(self):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"registry_results_{timestamp}.xlsx"
        default_path = os.path.join(desktop, default_name)
        self.output_file.set(default_path)

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if file_path:
            self.selected_file.set(file_path)
            self.log_status(f"Selected file: {os.path.basename(file_path)}")
            self.extract_names(file_path)

    def extract_names(self, file_path):
        # Use RegistryProcessor's read_excel_file to extract names
        processor = RegistryProcessor()
        df = processor.read_excel_file(file_path)
        self.names = []
        self.names_list.config(state='normal')
        self.names_list.delete(0, tk.END)
        if df is not None and not df.empty:
            for idx, row in df.iterrows():
                name_str = f"{row['First Name']} {row['Last Name']} ({row['Gender']})"
                self.names.append((row['First Name'], row['Last Name'], row['Gender']))
                self.names_list.insert(tk.END, name_str)
            self.log_status(f"Loaded {len(self.names)} names from file.")
        else:
            self.names_list.insert(tk.END, "No names loaded.")
            self.names_list.config(state='disabled')
            self.log_status("No valid names found in file.")

    def change_output_location(self):
        file_path = filedialog.asksaveasfilename(title="Save Results As", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if file_path:
            self.output_file.set(file_path)
            self.log_status(f"Output location set to: {os.path.basename(file_path)}")

    def start_processing(self):
        if not self.selected_file.get():
            messagebox.showerror("Error", "Please select an Excel file first.")
            return
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output location.")
            return
        if not self.names:
            messagebox.showerror("Error", "No names to process. Please select a valid Excel file.")
            return
        self.processing = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.open_results_btn.config(state=tk.DISABLED)
        self.progress_label.config(text="Initializing...")
        self.status_text.delete(1.0, tk.END)
        self.processing_thread = threading.Thread(target=self._process_file)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def stop_processing(self):
        if self.processor:
            self.processor.stop_processing()

    def _process_file(self):
        try:
            self.processor = RegistryProcessor(progress_callback=self.update_progress, status_callback=self.log_status)
            success = self.processor.process_file(self.selected_file.get(), self.output_file.get())
            self.root.after(0, self._processing_complete, success)
        except Exception as e:
            self.root.after(0, self.log_status, f"Unexpected error: {str(e)}")
            self.root.after(0, self._processing_complete, False)

    def _processing_complete(self, success):
        self.processing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        if success:
            self.open_results_btn.config(state=tk.NORMAL)
            self.progress_label.config(text="Processing completed successfully!")
            messagebox.showinfo("Success", f"Processing completed successfully!\n\nResults saved to:\n{self.output_file.get()}")
        else:
            self.progress_label.config(text="Processing failed or was stopped")
            messagebox.showerror("Error", "Processing failed. Check the status log for details.")
        if self.processor:
            self.processor.cleanup()
            self.processor = None
        # Reset name highlights
        self.root.after(0, self.reset_name_highlights)

    def update_progress(self, current, total, name):
        if total > 0:
            self.root.after(0, lambda: self.progress_label.config(text=f"Processing: {name} ({current}/{total})"))
            self.root.after(0, lambda: self.highlight_current_name(current, total))

    def highlight_current_name(self, current, total):
        # Remove all highlights
        for i in range(self.names_list.size()):
            self.names_list.itemconfig(i, {'bg': 'white', 'fg': 'black'})
        # Highlight current name
        idx = current - 1
        if 0 <= idx < self.names_list.size():
            self.names_list.itemconfig(idx, {'bg': '#d1ffd1', 'fg': 'black'})
        # Mark completed names
        for i in range(idx):
            self.names_list.itemconfig(i, {'bg': '#e0e0e0', 'fg': 'gray'})

    def reset_name_highlights(self):
        for i in range(self.names_list.size()):
            self.names_list.itemconfig(i, {'bg': 'white', 'fg': 'black'})

    def log_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, log_message)
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')

    def open_results(self):
        try:
            import subprocess
            import platform
            if platform.system() == 'Windows':
                os.startfile(self.output_file.get())
            elif platform.system() == 'Darwin':
                subprocess.call(['open', self.output_file.get()])
            else:
                subprocess.call(['xdg-open', self.output_file.get()])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open results file: {str(e)}")

def main():
    root = tk.Tk()
    app = RegistryAppV2(root)
    root.mainloop()

if __name__ == "__main__":
    main() 