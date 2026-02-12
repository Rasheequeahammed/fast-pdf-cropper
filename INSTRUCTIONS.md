# How to Run the PDF Cropper

## 1. Install Dependencies
Open your terminal in VS Code and run:
```bash
pip install -r requirements.txt
```

## 2. Install Poppler (Done!)
I have configured the script to use the Poppler version you provided at `c:\Users\rasheeque raheem\Downloads\PDF CUTTER\poppler-25.12.0\Library\bin`.

You do **not** need to install anything else or change system paths.

## 3. Prepare Files
1.  Copy your PDF certificates into the `input_pdfs` folder.
2.  Make sure `output_images` folder exists (the script creates it if missing).

## 4. Run the Script
```bash
python crop_pdfs_gui.py
```

## 5. Usage
- **Rotate**: Click "Rotate" (or press `R`) to spin the image 90°.
- **Draw**: Left-click and drag to create a red box. It forces a 3:2 aspect ratio.
- **Save**: Click "Save & Next" (or press `S`) to save the selection.
- **Skip**: Click "Skip" (or press `N`) to ignore the current file.
- **Auto-Fit**: The image automatically fits your window. Resize the window if needed.
