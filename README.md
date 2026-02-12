# PDF Certificate Cropper

A fast, interactive Python tool to manually crop and extract high-resolution images from PDF certificates.

## Features
- **Auto-Fit Display**: Automatically scales the PDF page to fit your screen.
- **Fixed Aspect Ratio**: Enforces a 3:2 aspect ratio for consistent certificate sizes.
- **Interactive Selection**:
    - **Move**: Drag the box to reposition.
    - **Resize**: Drag corners to scale while maintaining ratio.
- **Rotation**: Rotate sideways documents 90° with a click.
- **High Res Output**: Extracts the original 300 DPI quality, ignoring screen resolution.
- **Workflow**: Auto-advances to the next PDF after saving.

## Installation

1.  **Clone the repo**
    ```bash
    git clone https://github.com/yourusername/certificate-cropper.git
    cd certificate-cropper
    ```

2.  **Install Python Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Poppler** (Required for PDF processing)
    - **Windows**: Download [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/), extract it, and place it in the project folder or add to PATH.
    - **Mac**: `brew install poppler`
    - **Linux**: `sudo apt install poppler-utils`

## Usage

1.  Place your PDF files in the `input_pdfs` folder.
2.  Run the script:
    ```bash
    python crop_pdfs_gui.py
    ```
3.  **Controls**:
    - **Draw**: Left-click and drag.
    - **Adjust**: Drag inside to move, drag corners to resize.
    - **Rotate**: `R` key or Rotate button.
    - **Save**: `S` key or Save button.
    - **Skip**: `N` key or Skip button.

## Output
Cropped images are saved to `output_images` as PNG files.
