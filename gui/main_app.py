import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
from datetime import datetime
import sys
import webdriver_manager

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.registry_processor import RegistryProcessor

class RegistryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arkansas Registry Processor - Basic Mode")
        self.root.geometry("600x400")
        self.selected_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.processing = False
        self.processor = None
        self.create_widgets()
        self.set_default_output_path()

    def create_widgets(self):
        # Title
        tk.Label(self.root, text="Arkansas Registry Processor", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(self.root, text="BASIC MODE - No custom styles", font=("Arial", 10)).pack(pady=2)
        # File selection
        file_frame = tk.Frame(self.root)
        file_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(file_frame, text="Excel File:").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=self.selected_file, width=40, state='readonly').pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT)
        # Output location
        out_frame = tk.Frame(self.root)
        out_frame.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(out_frame, text="Output File:").pack(side=tk.LEFT)
        tk.Entry(out_frame, textvariable=self.output_file, width=40, state='readonly').pack(side=tk.LEFT, padx=5)
        tk.Button(out_frame, text="Change", command=self.change_output_location).pack(side=tk.LEFT)
        # Controls
        ctrl_frame = tk.Frame(self.root)
        ctrl_frame.pack(pady=10)
        self.start_btn = tk.Button(ctrl_frame, text="Start Processing", command=self.start_processing)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = tk.Button(ctrl_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.open_results_btn = tk.Button(ctrl_frame, text="Open Results", command=self.open_results, state=tk.DISABLED)
        self.open_results_btn.pack(side=tk.LEFT, padx=5)
        # Progress
        self.progress_label = tk.Label(self.root, text="Ready to process", font=("Arial", 10))
        self.progress_label.pack(pady=5)
        # Status log
        self.status_text = tk.Text(self.root, height=8, width=70, state='normal')
        self.status_text.pack(padx=20, pady=10)
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

    def update_progress(self, current, total, name):
        if total > 0:
            self.root.after(0, lambda: self.progress_label.config(text=f"Processing: {name} ({current}/{total})"))

    def log_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        def _update_text():
            self.status_text.insert(tk.END, log_message)
            self.status_text.see(tk.END)
        self.root.after(0, _update_text)

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
    app = RegistryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 