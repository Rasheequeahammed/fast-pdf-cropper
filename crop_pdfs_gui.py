
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError
import sys

# Configuration
INPUT_FOLDER = "input_pdfs"
OUTPUT_FOLDER = "output_images"
TARGET_WIDTH = 600
TARGET_HEIGHT = 400
ASPECT_RATIO = TARGET_WIDTH / TARGET_HEIGHT  # 1.5

# Poppler Path
POPPLER_PATH = r"c:\Users\rasheeque raheem\Downloads\PDF CUTTER\poppler-25.12.0\Library\bin"

class PDFCropperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Certificate Cropper")
        self.root.geometry("1400x900")
        
        # Data
        self.pdf_files = []
        self.current_index = 0
        self.current_pil_image = None
        self.photo_image = None
        self.scale_factor = 1.0 # If we resize for display
        
        # Selection state
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.selection_coords = None # (x1, y1, x2, y2) in original image coordinates
        
        # GUI Setup
        self._setup_ui()
        
        # Load Files
        self._load_files()
        
    def _setup_ui(self):
        # Top Control Panel
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.lbl_status = tk.Label(control_frame, text="Ready", font=("Arial", 12))
        self.lbl_status.pack(side=tk.LEFT, padx=20)
        
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(side=tk.RIGHT, padx=20)
        
        self.btn_save = tk.Button(btn_frame, text="Save & Next (S)", command=self.save_and_next, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
        self.btn_save.pack(side=tk.LEFT, padx=10)
        
        self.btn_rotate = tk.Button(btn_frame, text="Rotate (R)", command=self.rotate_image, bg="#2196F3", fg="white", font=("Arial", 11))
        self.btn_rotate.pack(side=tk.LEFT, padx=10)

        self.btn_skip = tk.Button(btn_frame, text="Skip (N)", command=self.skip_next, bg="#f44336", fg="white", font=("Arial", 11))
        self.btn_skip.pack(side=tk.LEFT, padx=10)
        
        # Canvas Area (No Scrollbars needed for Fit-to-Screen)
        canvas_frame = tk.Frame(self.root, bg="#333333")
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#333333", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Configure>", self.on_resize) # Handle window resize
        
        # Keyboard shortcuts
        self.root.bind('<s>', lambda e: self.save_and_next())
        self.root.bind('<n>', lambda e: self.skip_next())
        self.root.bind('<r>', lambda e: self.rotate_image())
        
    def _load_files(self):
        # Create directories
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)
        if not os.path.exists(INPUT_FOLDER):
            os.makedirs(INPUT_FOLDER)
            messagebox.showinfo("Info", f"Created '{INPUT_FOLDER}'. Please add PDFs.")
            return

        self.pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.pdf')]
        
        if not self.pdf_files:
            messagebox.showinfo("Info", f"No PDF files found in '{INPUT_FOLDER}'.")
            return
            
        self.load_current_pdf()

    def on_resize(self, event):
        # Redraw image when window resizes
        if self.current_pil_image:
            self.display_image()

    def display_image(self):
        if not self.current_pil_image:
            return
            
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return # Too small or not ready
            
        # Calculate scale factor to fit
        img_w, img_h = self.current_pil_image.size
        
        scale_w = canvas_width / img_w
        scale_h = canvas_height / img_h
        
        self.scale_factor = min(scale_w, scale_h) * 0.95 # Leave a small margin
        
        new_w = int(img_w * self.scale_factor)
        new_h = int(img_h * self.scale_factor)
        
        # Resize for display
        resized_img = self.current_pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(resized_img)
        
        # Center image
        self.offset_x = (canvas_width - new_w) // 2
        self.offset_y = (canvas_height - new_h) // 2
        
        self.canvas.delete("all")
        self.canvas.create_image(self.offset_x, self.offset_y, image=self.photo_image, anchor=tk.NW)
        
        # Clear selection on reload/resize
        self.rect_id = None
        self.selection_coords = None

    def load_current_pdf(self):
        if self.current_index >= len(self.pdf_files):
            messagebox.showinfo("Done", "All files processed!")
            self.root.quit()
            return
            
        pdf_file = self.pdf_files[self.current_index]
        self.lbl_status.config(text=f"Processing [{self.current_index + 1}/{len(self.pdf_files)}]: {pdf_file}")
        
        pdf_path = os.path.join(INPUT_FOLDER, pdf_file)
        
        try:
            # Convert PDF to Image
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300, poppler_path=POPPLER_PATH)
            if not images:
                self.lbl_status.config(text=f"Error reading {pdf_file}")
                return
            
            self.current_pil_image = images[0]
            self.display_image()
            
        except PDFInfoNotInstalledError:
            messagebox.showerror("Error", "Poppler not found. Please check configuration.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")
            
    def on_press(self, event):
        x, y = event.x, event.y
        self.start_x = x
        self.start_y = y
        self.interaction_mode = 'CREATE'
        self.resize_anchor = None # The fixed point when resizing
        
        # Check if we have an existing selection
        if self.selection_coords:
            # Convert image coords back to canvas coords for hit testing
            ix1, iy1, ix2, iy2 = self.selection_coords
            cx1 = ix1 * self.scale_factor + self.offset_x
            cy1 = iy1 * self.scale_factor + self.offset_y
            cx2 = ix2 * self.scale_factor + self.offset_x
            cy2 = iy2 * self.scale_factor + self.offset_y
            
            # Normalize for hit testing
            x1, y1 = min(cx1, cx2), min(cy1, cy2)
            x2, y2 = max(cx1, cx2), max(cy1, cy2)
            
            # Check corners (tolerance 10px)
            tol = 10
            # Corners: nw, ne, sw, se
            if abs(x - x1) < tol and abs(y - y1) < tol:
                self.interaction_mode = 'RESIZE'
                self.resize_corner = 'nw'
                self.resize_anchor = (x2, y2)
                return
            elif abs(x - x2) < tol and abs(y - y1) < tol:
                self.interaction_mode = 'RESIZE'
                self.resize_corner = 'ne'
                self.resize_anchor = (x1, y2)
                return
            elif abs(x - x1) < tol and abs(y - y2) < tol:
                self.interaction_mode = 'RESIZE'
                self.resize_corner = 'sw'
                self.resize_anchor = (x2, y1)
                return
            elif abs(x - x2) < tol and abs(y - y2) < tol:
                self.interaction_mode = 'RESIZE'
                self.resize_corner = 'se'
                self.resize_anchor = (x1, y1)
                return
                
            # Check inside for move
            if x1 < x < x2 and y1 < y < y2:
                self.interaction_mode = 'MOVE'
                self.move_offset = (x - x1, y - y1) # Offset from top-left
                self.current_box_dims = (x2 - x1, y2 - y1)
                return

        # If we reached here, we are creating a new box
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        self.rect_id = self.canvas.create_rectangle(x, y, x, y, outline="red", width=2, dash=(5, 5))
        self.selection_coords = None

    def on_drag(self, event):
        cur_x, cur_y = event.x, event.y
        
        if self.interaction_mode == 'CREATE':
            if not self.rect_id: return
            
            width = cur_x - self.start_x
            height = cur_y - self.start_y
            
            # Force Ratio Logic (same as before)
            abs_width = abs(width)
            abs_height = abs(height)
            
            if abs_width > abs_height * ASPECT_RATIO:
                 target_h = abs_width / ASPECT_RATIO
                 target_w = abs_width
            else:
                 target_w = abs_height * ASPECT_RATIO
                 target_h = abs_height

            sign_x = 1 if width >= 0 else -1
            sign_y = 1 if height >= 0 else -1
            
            new_x = self.start_x + (target_w * sign_x)
            new_y = self.start_y + (target_h * sign_y)
            
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, new_x, new_y)
            
        elif self.interaction_mode == 'MOVE':
            if not self.rect_id: return
            
            # Calculate new top-left based on mouse position and initial offset
            w, h = self.current_box_dims
            new_x1 = cur_x - self.move_offset[0]
            new_y1 = cur_y - self.move_offset[1]
            new_x2 = new_x1 + w
            new_y2 = new_y1 + h
            
            # Clamp to canvas bounds
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            
            if new_x1 < 0: new_x1 = 0; new_x2 = w
            if new_y1 < 0: new_y1 = 0; new_y2 = h
            if new_x2 > cw: new_x2 = cw; new_x1 = cw - w
            if new_y2 > ch: new_y2 = ch; new_y1 = ch - h
            
            self.canvas.coords(self.rect_id, new_x1, new_y1, new_x2, new_y2)
            
        elif self.interaction_mode == 'RESIZE':
            if not self.rect_id or not self.resize_anchor: return
            
            anchor_x, anchor_y = self.resize_anchor
            
            # Calculate new width/height relative to anchor
            width = cur_x - anchor_x
            height = cur_y - anchor_y
            
            # Force Aspect Ratio
            abs_width = abs(width)
            # abs_height = abs_width / ASPECT_RATIO
            
            # Use strict width-based resizing for stability
            target_w = abs_width
            target_h = abs_width / ASPECT_RATIO
            
            sign_x = 1 if width >= 0 else -1
            sign_y = 1 if height >= 0 else -1
            
            # However, sign_y needs to be consistent with the quadrant we are in relative to anchor
            # If resizing 'se' (bottom-right) from 'nw' (top-left anchor), signs should be matching box direction
            # Actually simpler: determine new point based on anchor and ratio
            
            new_width = target_w * sign_x
            new_height = target_h * sign_y
            
            # Check if this movement direction matches the corner we are dragging
            # e.g. if dragging SE corner, x > anchor_x and y > anchor_y usually
            
            # Simplify: Just update the relevant corner coordinate
            new_x = anchor_x + new_width
            new_y = anchor_y + new_height
            
            self.canvas.coords(self.rect_id, anchor_x, anchor_y, new_x, new_y)

    def on_release(self, event):
        if not self.rect_id:
            return
            
        # Finalize coords (Canvas Coordinates)
        coords = self.canvas.coords(self.rect_id)
        if coords:
            x1, y1, x2, y2 = coords
            
            # Convert Canvas Coords -> Image Coords
            img_x1 = (min(x1, x2) - self.offset_x) / self.scale_factor
            img_y1 = (min(y1, y2) - self.offset_y) / self.scale_factor
            img_x2 = (max(x1, x2) - self.offset_x) / self.scale_factor
            img_y2 = (max(y1, y2) - self.offset_y) / self.scale_factor
            
            self.selection_coords = (img_x1, img_y1, img_x2, img_y2)
        
        self.interaction_mode = None
            
    def save_and_next(self):
        if not self.selection_coords:
            messagebox.showwarning("Warning", "Please draw a selection box first.")
            return
            
        try:
            x1, y1, x2, y2 = self.selection_coords
            
            # Crop
            # Ensure we are within bounds of the ORIGINAL image
            img_w, img_h = self.current_pil_image.size
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(img_w, x2)
            y2 = min(img_h, y2)

            if x2 <= x1 + 5 or y2 <= y1 + 5: # Small threshold
                messagebox.showwarning("Error", "Selection too small.")
                return

            crop = self.current_pil_image.crop((x1, y1, x2, y2))
            
            # Resize
            # Use LANCZOS (formerly ANTIALIAS)
            resized = crop.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            
            # Save
            if self.current_index < len(self.pdf_files):
                current_file = self.pdf_files[self.current_index]
                output_filename = os.path.splitext(current_file)[0] + ".png"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                
                resized.save(output_path, "PNG")
                print(f"Saved: {output_path}")
                
            self.skip_next()
                 
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

    def rotate_image(self):
        if not self.current_pil_image:
            return
            
        # Rotate 90 degrees clockwise (PIL rotate is counter-clockwise, so -90)
        # expand=True resizing the canvas to fit the new dimensions
        self.current_pil_image = self.current_pil_image.rotate(-90, expand=True)
        
        # Clear any existing selection as coords are invalid now
        self.rect_id = None
        self.selection_coords = None
        
        self.display_image()
            
    def skip_next(self):
        self.current_index += 1
        self.load_current_pdf()

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFCropperApp(root)
    root.mainloop()
