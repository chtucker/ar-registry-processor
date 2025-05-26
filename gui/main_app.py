import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from datetime import datetime
import sys

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.registry_processor import RegistryProcessor

class RegistryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arkansas Registry Processor")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Configure style
        self.setup_styles()
        
        # Variables
        self.selected_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.processing = False
        self.processor = None
        
        # Create GUI
        self.create_widgets()
        
        # Set default output location
        self.set_default_output_path()
        
    def setup_styles(self):
        """Configure modern styling for the application"""
        style = ttk.Style()
        
        # Configure modern theme
        style.theme_use('clam')
        
        # Custom colors
        bg_color = '#f0f0f0'
        button_color = '#0078d4'
        button_hover = '#106ebe'
        text_color = '#323130'
        
        self.root.configure(bg=bg_color)
        
        # Configure button styles
        style.configure('Modern.TButton',
                       background=button_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(10, 8))
        
        style.map('Modern.TButton',
                 background=[('active', button_hover),
                           ('pressed', button_hover)])
        
        # Configure frame styles
        style.configure('Card.TFrame',
                       background='white',
                       relief='solid',
                       borderwidth=1)
        
        # Configure label styles
        style.configure('Title.TLabel',
                       background='white',
                       foreground=text_color,
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background='white',
                       foreground=text_color,
                       font=('Segoe UI', 10))
        
        style.configure('Status.TLabel',
                       background='white',
                       foreground=text_color,
                       font=('Segoe UI', 9))
    
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="Arkansas Registry Processor",
                               style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame,
                                  text="Process Excel files against the Arkansas Sex Offender Registry",
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 20))
        
        # File selection card
        self.create_file_selection_card(main_frame)
        
        # Processing controls card
        self.create_processing_card(main_frame)
        
        # Progress card
        self.create_progress_card(main_frame)
        
        # Status card
        self.create_status_card(main_frame)
    
    def create_file_selection_card(self, parent):
        """Create the file selection section"""
        card_frame = ttk.Frame(parent, style='Card.TFrame', padding="15")
        card_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Card title
        title_label = ttk.Label(card_frame, 
                               text="1. Select Excel File",
                               font=('Segoe UI', 12, 'bold'),
                               style='Status.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # File selection frame
        file_frame = ttk.Frame(card_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File path entry
        self.file_entry = ttk.Entry(file_frame, 
                                   textvariable=self.selected_file,
                                   font=('Segoe UI', 9),
                                   state='readonly')
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Browse button
        browse_btn = ttk.Button(file_frame,
                               text="Browse...",
                               command=self.browse_file,
                               style='Modern.TButton')
        browse_btn.pack(side=tk.RIGHT)
        
        # Instructions
        instructions = ttk.Label(card_frame,
                                text="Select an Excel file (.xlsx) with names in columns B (First Name), D (Last Name), and G (Gender)",
                                style='Subtitle.TLabel',
                                wraplength=600)
        instructions.pack(anchor=tk.W)
    
    def create_processing_card(self, parent):
        """Create the processing controls section"""
        card_frame = ttk.Frame(parent, style='Card.TFrame', padding="15")
        card_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Card title
        title_label = ttk.Label(card_frame,
                               text="2. Output Location",
                               font=('Segoe UI', 12, 'bold'),
                               style='Status.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Output file frame
        output_frame = ttk.Frame(card_frame)
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Output path entry
        self.output_entry = ttk.Entry(output_frame,
                                     textvariable=self.output_file,
                                     font=('Segoe UI', 9),
                                     state='readonly')
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Change output button
        output_btn = ttk.Button(output_frame,
                               text="Change...",
                               command=self.change_output_location,
                               style='Modern.TButton')
        output_btn.pack(side=tk.RIGHT)
        
        # Control buttons frame
        controls_frame = ttk.Frame(card_frame)
        controls_frame.pack(fill=tk.X)
        
        # Start button
        self.start_btn = ttk.Button(controls_frame,
                                   text="Start Processing",
                                   command=self.start_processing,
                                   style='Modern.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_btn = ttk.Button(controls_frame,
                                  text="Stop Processing",
                                  command=self.stop_processing,
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        # Open results button
        self.open_results_btn = ttk.Button(controls_frame,
                                          text="Open Results",
                                          command=self.open_results,
                                          state=tk.DISABLED)
        self.open_results_btn.pack(side=tk.RIGHT)
    
    def create_progress_card(self, parent):
        """Create the progress display section"""
        card_frame = ttk.Frame(parent, style='Card.TFrame', padding="15")
        card_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Card title
        title_label = ttk.Label(card_frame,
                               text="3. Progress",
                               font=('Segoe UI', 12, 'bold'),
                               style='Status.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(card_frame,
                                           mode='determinate',
                                           length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Progress text
        self.progress_text = ttk.Label(card_frame,
                                      text="Ready to process",
                                      style='Status.TLabel')
        self.progress_text.pack(anchor=tk.W)
    
    def create_status_card(self, parent):
        """Create the status log section"""
        card_frame = ttk.Frame(parent, style='Card.TFrame', padding="15")
        card_frame.pack(fill=tk.BOTH, expand=True)
        
        # Card title
        title_label = ttk.Label(card_frame,
                               text="4. Status Log",
                               font=('Segoe UI', 12, 'bold'),
                               style='Status.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Status text area with scrollbar
        text_frame = ttk.Frame(card_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(text_frame,
                                  height=8,
                                  wrap=tk.WORD,
                                  font=('Consolas', 9),
                                  bg='#f8f8f8',
                                  fg='#323130',
                                  relief='sunken',
                                  borderwidth=1)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add initial status message
        self.log_status("Application started. Select an Excel file to begin.")
    
    def set_default_output_path(self):
        """Set default output file path"""
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"registry_results_{timestamp}.xlsx"
        default_path = os.path.join(desktop, default_name)
        self.output_file.set(default_path)
    
    def browse_file(self):
        """Open file dialog to select Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.selected_file.set(file_path)
            self.log_status(f"Selected file: {os.path.basename(file_path)}")
    
    def change_output_location(self):
        """Change output file location"""
        file_path = filedialog.asksaveasfilename(
            title="Save Results As",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.output_file.set(file_path)
            self.log_status(f"Output location set to: {os.path.basename(file_path)}")
    
    def start_processing(self):
        """Start the registry processing in a background thread"""
        if not self.selected_file.get():
            messagebox.showerror("Error", "Please select an Excel file first.")
            return
        
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output location.")
            return
        
        # Update UI state
        self.processing = True
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.open_results_btn.configure(state=tk.DISABLED)
        
        # Reset progress
        self.progress_bar['value'] = 0
        self.progress_text.configure(text="Initializing...")
        
        # Clear status log
        self.status_text.delete(1.0, tk.END)
        
        # Start processing in background thread
        self.processing_thread = threading.Thread(target=self._process_file)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def stop_processing(self):
        """Stop the current processing"""
        if self.processor:
            self.processor.stop_processing()
    
    def _process_file(self):
        """Background thread function for processing the file"""
        try:
            # Create processor with callbacks
            self.processor = RegistryProcessor(
                progress_callback=self.update_progress,
                status_callback=self.log_status
            )
            
            # Process the file
            success = self.processor.process_file(
                self.selected_file.get(),
                self.output_file.get()
            )
            
            # Update UI based on result
            self.root.after(0, self._processing_complete, success)
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.root.after(0, self.log_status, error_msg)
            self.root.after(0, self._processing_complete, False)
    
    def _processing_complete(self, success):
        """Called when processing is complete"""
        self.processing = False
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        
        if success:
            self.open_results_btn.configure(state=tk.NORMAL)
            self.progress_text.configure(text="Processing completed successfully!")
            messagebox.showinfo("Success", 
                              f"Processing completed successfully!\n\nResults saved to:\n{self.output_file.get()}")
        else:
            self.progress_text.configure(text="Processing failed or was stopped")
            messagebox.showerror("Error", "Processing failed. Check the status log for details.")
        
        # Cleanup
        if self.processor:
            self.processor.cleanup()
            self.processor = None
    
    def update_progress(self, current, total, name):
        """Update progress bar and text"""
        if total > 0:
            progress_value = (current / total) * 100
            self.root.after(0, lambda: self.progress_bar.configure(value=progress_value))
            self.root.after(0, lambda: self.progress_text.configure(
                text=f"Processing: {name} ({current}/{total})"
            ))
    
    def log_status(self, message):
        """Add message to status log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        def _update_text():
            self.status_text.insert(tk.END, log_message)
            self.status_text.see(tk.END)
        
        self.root.after(0, _update_text)
    
    def open_results(self):
        """Open the results file"""
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(self.output_file.get())
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', self.output_file.get()])
            else:  # Linux
                subprocess.call(['xdg-open', self.output_file.get()])
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not open results file: {str(e)}")

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = RegistryApp(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Handle window closing
    def on_closing():
        if hasattr(app, 'processing') and app.processing:
            if messagebox.askokcancel("Quit", "Processing is still running. Do you want to stop and quit?"):
                if app.processor:
                    app.processor.cleanup()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main() 