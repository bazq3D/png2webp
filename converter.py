import os
import sys
import glob
import time
from multiprocessing import Pool, cpu_count

try:
    from PIL import Image
except ImportError:
    print("Pillow library is missing. Installing it now...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

# Configuration
INPUT_DIR = "input"
OUTPUT_DIR = "output"
QUALITY = 80 # WebP quality factor (0 to 100)

# Multi-processing (CPU) Ayarları:
# Script çalıştığında kaç çekirdek kullanılacağını soracak.
# Boş bırakılırsa (Enter'a basılırsa) buradaki varsayılan değer (çekirdeklerin YARISI) kullanılacak.
DEFAULT_CORES = max(1, int(cpu_count() * 0.5))

def convert_image(input_path):
    try:
        # Create corresponding output path
        rel_path = os.path.relpath(input_path, INPUT_DIR)
        base_name = os.path.splitext(rel_path)[0]
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}.webp")
        
        # Ensure output directory for this file exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Skip if already exists
        if os.path.exists(output_path):
            return True, f"Skipped (already exists): {output_path}"
            
        with Image.open(input_path) as img:
            img.save(output_path, "WEBP", quality=QUALITY)
            
        return True, f"Converted: {rel_path}"
    except Exception as e:
        return False, f"Failed: {input_path} - Error: {e}"

def main():
    if not os.path.exists(INPUT_DIR):
        print(f"Creating '{INPUT_DIR}' directory. Please put your PNG files there and run again.")
        os.makedirs(INPUT_DIR, exist_ok=True)
        return
        
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Find all PNGs recursively
    print("Scanning for PNG files...")
    png_files = glob.glob(os.path.join(INPUT_DIR, "**", "*.png"), recursive=True)
    
    if not png_files:
        print(f"No PNG files found in the '{INPUT_DIR}' directory.")
        return
        
    total_files = len(png_files)
    print(f"Found {total_files} PNG files to convert.")
    
    start_time = time.time()
    
    # Kullanıcıya kaç çekirdek kullanmak istediğini sor
    total_cores = cpu_count()
    print(f"\n[Sistem] Toplam {total_cores} CPU çekirdeğiniz var.")
    user_input = input(f"Kaç çekirdek kullanmak istersiniz? (Varsayılan olarak yarısı ({DEFAULT_CORES}) kullanılacak. Enter'a basarak geçebilirsiniz): ").strip()
    
    if user_input.isdigit():
        num_processes = max(1, min(int(user_input), total_cores))
    else:
        num_processes = DEFAULT_CORES
        
    print(f"\nStarting conversion using {num_processes} concurrent workers...")
    
    success_count = 0
    fail_count = 0
    
    with Pool(processes=num_processes) as pool:
        for i, (success, msg) in enumerate(pool.imap_unordered(convert_image, png_files), 1):
            if success:
                success_count += 1
            else:
                fail_count += 1
            
            # Print progress every 100 files or if failed
            if not success or i % 100 == 0 or i == total_files:
                percent = (i / total_files) * 100
                print(f"[{percent:.1f}%] Processed {i}/{total_files} (Success: {success_count}, Failed: {fail_count})")
                if not success:
                    print(msg)
                    
    elapsed_time = time.time() - start_time
    print("\n--- Conversion Complete ---")
    print(f"Total files: {total_files}")
    print(f"Successfully converted: {success_count}")
    print(f"Failed conversions: {fail_count}")
    print(f"Time taken: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
    print(f"Average speed: {total_files/elapsed_time:.2f} images/second")

if __name__ == "__main__":
    # Workaround for multiprocessing on Windows
    # Add support for being packaged into an executable
    sys.setrecursionlimit(2000)
    main()
