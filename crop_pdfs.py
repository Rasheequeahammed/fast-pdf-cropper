
import cv2
import numpy as np
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

# Optional: Set this if Poppler is not in your PATH
# POPPLER_PATH = r"C:\path\to\poppler-xx\bin" 
POPPLER_PATH = r"c:\Users\rasheeque raheem\Downloads\PDF CUTTER\poppler-25.12.0\Library\bin"

def main():
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"Created {INPUT_FOLDER}. Please add PDF files there.")
        return

    pdf_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {INPUT_FOLDER}.")
        return

    print(f"Found {len(pdf_files)} PDF files.")
    print("Controls:")
    print("  Drag mouse to select area (forces 3:2 aspect ratio)")
    print("  's': Save selection and Next")
    print("  'n': Next (skip current)")
    print("  'q' or ESC: Quit")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(INPUT_FOLDER, pdf_file)
        print(f"Processing: {pdf_file}")
        
        try:
            # Convert first page to image
            # 300 DPI for high resolution
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300, poppler_path=POPPLER_PATH)
            
            if not images:
                print(f"  Could not convert {pdf_file}")
                continue
                
            pil_image = images[0]
            # Convert PIL image to OpenCV format (BGR)
            img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Setup interactive window
            window_name = f"Crop: {pdf_file}"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 1200, 800) # Initial window size
            
            # Variables for mouse callback
            rect_start = None
            rect_end = None
            drawing = False
            
            def mouse_callback(event, x, y, flags, param):
                nonlocal rect_start, rect_end, drawing
                
                if event == cv2.EVENT_LBUTTONDOWN:
                    drawing = True
                    rect_start = (x, y)
                    rect_end = (x, y)
                
                elif event == cv2.EVENT_MOUSEMOVE:
                    if drawing and rect_start:
                        # Force 3:2 aspect ratio logic
                        current_x = x
                        width = current_x - rect_start[0]
                        
                        # Apply aspect ratio constraint
                        # Height should be width / ASPECT_RATIO
                        abs_width = abs(width)
                        abs_height = int(abs_width / ASPECT_RATIO)
                        
                        # Determine direction for y
                        # If we just use current y to determine sign?
                        # Let's say if we drag up (y < start_y), sign is -1
                        # if we drag down (y > start_y), sign is 1
                        
                        current_y = y
                        height_diff = current_y - rect_start[1]
                        sign_y = 1 if height_diff >= 0 else -1
                        
                        new_y = rect_start[1] + (abs_height * sign_y)
                        rect_end = (current_x, new_y)
                        
                elif event == cv2.EVENT_LBUTTONUP:
                    drawing = False

            cv2.setMouseCallback(window_name, mouse_callback)
            
            while True:
                display_img = img.copy()
                
                if rect_start and rect_end:
                    cv2.rectangle(display_img, rect_start, rect_end, (0, 255, 0), 2)
                
                cv2.imshow(window_name, display_img)
                key = cv2.waitKey(1) & 0xFF
                
                # 's' to save
                if key == ord('s'):
                    if rect_start and rect_end:
                        # Calculate crop coordinates
                        x1 = min(rect_start[0], rect_end[0])
                        y1 = min(rect_start[1], rect_end[1])
                        x2 = max(rect_start[0], rect_end[0])
                        y2 = max(rect_start[1], rect_end[1])
                        
                        # Ensure we have some area
                        if x2 > x1 and y2 > y1:
                            crop = img[y1:y2, x1:x2]
                            
                            # Resize to 600x400
                            # Use INTER_AREA for shrinking, INTER_CUBIC for enlarging
                            resized = cv2.resize(crop, (TARGET_WIDTH, TARGET_HEIGHT), interpolation=cv2.INTER_AREA)
                            
                            output_filename = os.path.splitext(pdf_file)[0] + ".png"
                            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                            cv2.imwrite(output_path, resized)
                            print(f"  Saved {output_path}")
                            break
                        else:
                            print("  Invalid selection. Please draw a rectangle.")
                    else:
                        print("  No selection made. Please draw a rectangle.")
                
                # 'n' for next
                elif key == ord('n'):
                    print("  Skipped.")
                    break
                
                # 'q' or ESC to quit
                elif key == ord('q') or key == 27:
                    cv2.destroyAllWindows()
                    print("Exiting...")
                    return
            
            cv2.destroyWindow(window_name)

        except PDFInfoNotInstalledError:
            print("Error: Poppler is not installed or not found in PATH.")
            print("Please install Poppler and add it to your PATH, or set POPPLER_PATH in the script.")
            print("See INSTRUCTIONS.md for details.")
            return

        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
            # import traceback
            # traceback.print_exc()

    cv2.destroyAllWindows()
    print("All done!")

if __name__ == "__main__":
    main()
