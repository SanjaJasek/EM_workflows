#!/usr/bin/env python3
import sys
import os
import numpy as np
import tifffile as tiff

def convert_file(in_path, out_path):
    img = tiff.imread(in_path)

    # Ensure it's signed
    if not np.issubdtype(img.dtype, np.signedinteger):
        print(f"Skipping (not signed): {in_path}")
        return

    min_val = img.min()
    
    # Shift values so minimum becomes 0
    img_shifted = img.astype(np.int32) - int(min_val)

    # Clip to uint16 range just in case
    img_shifted = np.clip(img_shifted, 0, 65535).astype(np.uint16)

    tiff.imwrite(out_path, img_shifted)

def main():
    if len(sys.argv) != 3:
        print("Usage: script.py <input_dir> <output_dir>")
        sys.exit(1)

    in_dir = sys.argv[1]
    out_dir = sys.argv[2]

    os.makedirs(out_dir, exist_ok=True)

    for fname in os.listdir(in_dir):
        if fname.lower().endswith((".tif", ".tiff")):
            in_path = os.path.join(in_dir, fname)
            out_path = os.path.join(out_dir, fname)

            print(f"Processing: {fname}")
            convert_file(in_path, out_path)

if __name__ == "__main__":
    main()
