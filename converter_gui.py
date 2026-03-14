import os
import sys
import glob
import time
import threading
from multiprocessing import Pool, cpu_count
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from PIL import Image
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

QUALITY = 80
DEFAULT_CORES = max(1, int(cpu_count() * 0.5))

def convert_image(args):
    input_path, output_dir, base_input_dir = args
    try:
        # Create corresponding output path preserving nested folders
        rel_path = os.path.relpath(input_path, base_input_dir)
        base_name = os.path.splitext(rel_path)[0]
        output_path = os.path.join(output_dir, f"{base_name}.webp")
        
        # Ensure output directory for this file exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Skip if already exists
        if os.path.exists(output_path):
            return True, f"Skipped: {os.path.basename(output_path)}"
            
        with Image.open(input_path) as img:
            img.save(output_path, "WEBP", quality=QUALITY)
            
        return True, f"Converted: {os.path.basename(rel_path)}"
    except Exception as e:
        return False, f"Failed: {os.path.basename(input_path)} - Error: {e}"

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("bazq - PNG to WebP Batch Converter")
        self.root.geometry("550x450")
        self.root.resizable(False, False)
        
        # Styling
        style = ttk.Style()
        style.theme_use('clam')
        
        self.input_dir = tk.StringVar(value=os.path.join(os.getcwd(), "input"))
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        self.cores_var = tk.StringVar(value=str(DEFAULT_CORES))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, pady=15)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="PNG to WebP Converter", font=("Arial", 16, "bold")).pack()
        tk.Label(header_frame, text="High-speed batch processor", font=("Arial", 10)).pack()
        
        main_frame = tk.Frame(self.root, padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input Directory Selection
        tk.Label(main_frame, text="Input Folder (PNGs):", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        tk.Entry(main_frame, textvariable=self.input_dir, width=45, state="readonly").grid(row=1, column=0, ipady=4)
        tk.Button(main_frame, text="Browse", command=self.browse_input, width=10).grid(row=1, column=1, padx=10)
        
        # Output Directory Selection
        tk.Label(main_frame, text="Output Folder (WebPs):", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(15, 5))
        tk.Entry(main_frame, textvariable=self.output_dir, width=45, state="readonly").grid(row=3, column=0, ipady=4)
        tk.Button(main_frame, text="Browse", command=self.browse_output, width=10).grid(row=3, column=1, padx=10)
        
        # CPU Cores Selection
        core_frame = tk.Frame(main_frame, pady=20)
        core_frame.grid(row=4, column=0, columnspan=2, sticky="w")
        
        total_cores = cpu_count()
        tk.Label(core_frame, text=f"CPU Cores to use (Total available: {total_cores}):", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        core_spinbox = ttk.Spinbox(core_frame, from_=1, to=total_cores, textvariable=self.cores_var, width=5, font=("Arial", 10))
        core_spinbox.pack(side=tk.LEFT, padx=10)
        
        tk.Label(core_frame, text=f"(Default: {DEFAULT_CORES} - Half load)", font=("Arial", 9, "italic")).pack(side=tk.LEFT)
        
        # Progress and Status
        self.status_label = tk.Label(main_frame, text="Ready.", font=("Arial", 10))
        self.status_label.grid(row=5, column=0, columnspan=2, pady=(10, 5))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100, length=480)
        self.progress_bar.grid(row=6, column=0, columnspan=2, pady=5)
        
        self.details_label = tk.Label(main_frame, text="", font=("Arial", 9, "italic"), fg="gray")
        self.details_label.grid(row=7, column=0, columnspan=2)
        
        # Convert Button
        self.convert_btn = tk.Button(self.root, text="START CONVERSION", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", height=2, command=self.start_conversion_thread)
        self.convert_btn.pack(fill=tk.X, padx=20, pady=15)

    def browse_input(self):
        folder = filedialog.askdirectory(initialdir=self.input_dir.get(), title="Select Input Folder")
        if folder:
            self.input_dir.set(folder)

    def browse_output(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir.get(), title="Select Output Folder")
        if folder:
            self.output_dir.set(folder)

    def start_conversion_thread(self):
        self.convert_btn.config(state=tk.DISABLED, text="CONVERTING...", bg="#9E9E9E")
        self.progress_var.set(0)
        self.status_label.config(text="Scanning for PNG files...", fg="blue")
        self.details_label.config(text="")
        
        # Run in a separate thread so GUI doesn't freeze
        threading.Thread(target=self.run_conversion, daemon=True).start()

    def run_conversion(self):
        in_dir = self.input_dir.get()
        out_dir = self.output_dir.get()
        
        try:
            cores = int(self.cores_var.get())
            if cores < 1 or cores > cpu_count():
                cores = DEFAULT_CORES
        except ValueError:
            cores = DEFAULT_CORES
            
        if not os.path.exists(in_dir):
            self.root.after(0, self.conversion_finished, False, f"Input directory '{in_dir}' does not exist.")
            return

        os.makedirs(out_dir, exist_ok=True)
        
        png_files = glob.glob(os.path.join(in_dir, "**", "*.png"), recursive=True)
        total_files = len(png_files)
        
        if total_files == 0:
            self.root.after(0, self.conversion_finished, False, "No PNG files found in the selected input folder.")
            return
            
        self.root.after(0, lambda: self.status_label.config(text=f"Found {total_files} PNGs. Starting conversion on {cores} cores..."))
        
        start_time = time.time()
        success_count = 0
        fail_count = 0
        
        # Prepare arguments for multiprocessing pool
        args_list = [(filepath, out_dir, in_dir) for filepath in png_files]
        
        try:
            with Pool(processes=cores) as pool:
                for i, (success, msg) in enumerate(pool.imap_unordered(convert_image, args_list), 1):
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                    
                    # Update GUI safely from thread
                    if i % 10 == 0 or i == total_files:
                        percent = (i / total_files) * 100
                        time_passed = time.time() - start_time
                        speed = i / time_passed if time_passed > 0 else 0
                        
                        status_text = f"Processing: {i}/{total_files} ({percent:.1f}%)"
                        details_text = f"Success: {success_count} | Failed: {fail_count} | Speed: {speed:.1f} img/sec"
                        
                        self.root.after(0, self.update_progress, percent, status_text, details_text)
                        
            elapsed = time.time() - start_time
            result_msg = f"Done! Converted {success_count} files in {elapsed:.1f}s."
            if fail_count > 0:
                result_msg += f" ({fail_count} failed)"
                
            self.root.after(0, self.conversion_finished, True, result_msg)
            
        except Exception as e:
            self.root.after(0, self.conversion_finished, False, f"An error occurred: {str(e)}")

    def update_progress(self, percent, status, details):
        self.progress_var.set(percent)
        self.status_label.config(text=status)
        self.details_label.config(text=details)

    def conversion_finished(self, success, message):
        self.convert_btn.config(state=tk.NORMAL, text="START CONVERSION", bg="#4CAF50")
        if success:
            self.status_label.config(text=message, fg="green")
            self.progress_var.set(100)
            messagebox.showinfo("Success", message)
        else:
            self.status_label.config(text=message, fg="red")
            self.progress_var.set(0)
            messagebox.showerror("Error", message)

if __name__ == "__main__":
    # Required for Windows multiprocessing when packaged
    sys.setrecursionlimit(2000)
    
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()
