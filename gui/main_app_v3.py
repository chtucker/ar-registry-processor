import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui.registry_processor import RegistryProcessor

class RegistryAppV3:
    def __init__(self, root):
        self.root = root
        self.root.title("Arkansas Registry Processor - ttk UI")
        self.root.geometry("850x600")
        self.selected_file = tk.StringVar(value="No file selected.")
        self.output_file = tk.StringVar(value="No output file selected.")
        self.processing = False
        self.processor = None
        self.names = []
        self.create_widgets()
        self.set_default_output_path()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=("Arial", 11, "bold"))
        style.configure('TLabel', font=("Arial", 10))
        style.configure('Header.TLabel', font=("Arial", 16, "bold"))
        style.configure('SubHeader.TLabel', font=("Arial", 10, "italic"))
        style.configure('Treeview', font=("Arial", 10))
        style.configure('TFrame', background='#f7f7f7')
        style.configure('TLabelframe', background='#f0f0f0', font=("Arial", 11, "bold"))
        style.configure('TLabelframe.Label', font=("Arial", 11, "bold"))

        main_frame = ttk.Frame(self.root, padding=15, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Arkansas Registry Processor", style='Header.TLabel').grid(row=0, column=0, columnspan=3, pady=(0, 5), sticky="w")
        ttk.Label(main_frame, text="TTK THEMED UI", style='SubHeader.TLabel').grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky="w")

        # File selection
        ttk.Label(main_frame, text="Excel File:").grid(row=2, column=0, sticky="e")
        file_entry = ttk.Entry(main_frame, textvariable=self.selected_file, width=40, state='readonly')
        file_entry.grid(row=2, column=1, sticky="we", padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_file).grid(row=2, column=2, sticky="w", padx=5)

        # Output location
        ttk.Label(main_frame, text="Output File:").grid(row=3, column=0, sticky="e")
        out_entry = ttk.Entry(main_frame, textvariable=self.output_file, width=40, state='readonly')
        out_entry.grid(row=3, column=1, sticky="we", padx=5)
        ttk.Button(main_frame, text="Change", command=self.change_output_location).grid(row=3, column=2, sticky="w", padx=5)

        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)

        # Names list
        names_frame = ttk.Labelframe(main_frame, text="Names to Process", padding=5)
        names_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(0, 5))
        names_frame.grid_rowconfigure(0, weight=1)
        names_frame.grid_columnconfigure(0, weight=1)
        self.names_tree = ttk.Treeview(names_frame, columns=("First Name", "Last Name", "Gender"), show='headings', height=10)
        self.names_tree.heading("First Name", text="First Name")
        self.names_tree.heading("Last Name", text="Last Name")
        self.names_tree.heading("Gender", text="Gender")
        self.names_tree.column("First Name", width=120)
        self.names_tree.column("Last Name", width=120)
        self.names_tree.column("Gender", width=80)
        self.names_tree.grid(row=0, column=0, sticky="nsew")
        names_scroll = ttk.Scrollbar(names_frame, orient=tk.VERTICAL, command=self.names_tree.yview)
        names_scroll.grid(row=0, column=1, sticky="ns")
        self.names_tree.config(yscrollcommand=names_scroll.set)
        # Placeholder row
        self.names_tree.insert('', 'end', values=("No names loaded.", "", ""))

        # Controls
        ctrl_frame = ttk.Frame(main_frame, style='TFrame')
        ctrl_frame.grid(row=6, column=0, columnspan=3, pady=10)
        self.start_btn = ttk.Button(ctrl_frame, text="Start Processing", command=self.start_processing)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = ttk.Button(ctrl_frame, text="Stop", command=self.stop_processing, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.open_results_btn = ttk.Button(ctrl_frame, text="Open Results", command=self.open_results, state=tk.DISABLED)
        self.open_results_btn.pack(side=tk.LEFT, padx=5)

        # Progress
        self.progress_label = ttk.Label(main_frame, text="Ready to process", font=("Arial", 10))
        self.progress_label.grid(row=7, column=0, columnspan=3, pady=(0, 5), sticky="w")

        # Status log
        status_frame = ttk.Labelframe(main_frame, text="Status Log", padding=5)
        status_frame.grid(row=8, column=0, columnspan=3, sticky="nsew", pady=(5, 0))
        status_frame.grid_rowconfigure(0, weight=1)
        status_frame.grid_columnconfigure(0, weight=1)
        self.status_text = tk.Text(status_frame, height=6, width=80, state='normal', relief=tk.SUNKEN, borderwidth=2, font=("Arial", 10))
        self.status_text.grid(row=0, column=0, sticky="nsew")
        status_scroll = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        status_scroll.grid(row=0, column=1, sticky="ns")
        self.status_text.config(yscrollcommand=status_scroll.set)
        self.status_text.insert(tk.END, "Status messages will appear here.\n")
        self.status_text.config(state='disabled')

        # Configure grid weights for resizing
        main_frame.grid_rowconfigure(5, weight=2)
        main_frame.grid_rowconfigure(8, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

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
        processor = RegistryProcessor()
        df = processor.read_excel_file(file_path)
        self.names = []
        for i in self.names_tree.get_children():
            self.names_tree.delete(i)
        if df is not None and not df.empty:
            for idx, row in df.iterrows():
                self.names.append((row['First Name'], row['Last Name'], row['Gender']))
                self.names_tree.insert('', 'end', values=(row['First Name'], row['Last Name'], row['Gender']))
            self.log_status(f"Loaded {len(self.names)} names from file.")
        else:
            self.names_tree.insert('', 'end', values=("No names loaded.", "", ""))
            self.log_status("No valid names found in file.")

    def change_output_location(self):
        file_path = filedialog.asksaveasfilename(title="Save Results As", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if file_path:
            self.output_file.set(file_path)
            self.log_status(f"Output location set to: {os.path.basename(file_path)}")

    def start_processing(self):
        if not self.selected_file.get() or self.selected_file.get() == "No file selected.":
            messagebox.showerror("Error", "Please select an Excel file first.")
            return
        if not self.output_file.get() or self.output_file.get() == "No output file selected.":
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
        self.status_text.config(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state='disabled')
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
        self.root.after(0, self.reset_name_highlights)

    def update_progress(self, current, total, name):
        if total > 0:
            self.root.after(0, lambda: self.progress_label.config(text=f"Processing: {name} ({current}/{total})"))
            self.root.after(0, lambda: self.highlight_current_name(current, total))

    def highlight_current_name(self, current, total):
        # Remove all highlights
        for i, item in enumerate(self.names_tree.get_children()):
            self.names_tree.item(item, tags=())
        # Highlight current name
        idx = current - 1
        items = list(self.names_tree.get_children())
        if 0 <= idx < len(items):
            self.names_tree.item(items[idx], tags=('current',))
            self.names_tree.tag_configure('current', background='#d1ffd1')
        # Mark completed names
        for i in range(idx):
            self.names_tree.item(items[i], tags=('done',))
            self.names_tree.tag_configure('done', background='#e0e0e0', foreground='gray')

    def reset_name_highlights(self):
        for item in self.names_tree.get_children():
            self.names_tree.item(item, tags=())

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
    app = RegistryAppV3(root)
    root.mainloop()

if __name__ == "__main__":
    main() 