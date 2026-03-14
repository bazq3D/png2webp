# bazq - PNG to WebP Batch Converter 🚀

A lightning-fast, multi-core Python script designed to bulk convert PNG images to WebP format. Perfect for shrinking massive asset folders without losing quality.

Our tests showed a massive **~95% reduction** in file size – an incredible space-saving tool for projects!

## 🌟 Features

- **Ultra-Fast Multi-Processing:** Utilizes multiple CPU cores to process thousands of images in seconds.
- **Auto-Detection:** Deep scans sub-folders to find every single `.png` file.
- **Smart CPU Load:** By default, it uses 50-75% of your CPU to prevent freezing your computer, with the option to unlock 100% power.
- **Two Versions Included:**
  - A simple **Console (CLI) Version** for quick, automated runs.
  - A clean **GUI (Graphical) Version** with a progress bar and folder selection.

---

## 💻 How to Use

### Option 1: The Easy GUI

1. Double-click the `run_gui.bat` file.
2. Select your `input` folder (where your PNGs are).
3. Select your `output` folder (where the WebPs will go).
4. Choose how many CPU cores you want to allocate.
5. Click **Start Conversion** and watch the progress bar fly!

### Option 2: The Fast Console

1. Place your `.png` files inside the `input` folder.
2. Double-click the `run_converter.bat` file.
3. If prompted, enter how many CPU cores you want to use (or just press `Enter` for Auto).
4. Find your compressed images mirrored beautifully in the `output` folder!

---

## 🛠️ Requirements & Setup

- You need [Python 3.x](https://www.python.org/downloads/) installed.
- No need to manually install dependencies; the provided `.bat` files will automatically install the required `Pillow` library if you don't have it.
