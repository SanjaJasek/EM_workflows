#!/usr/bin/env python3
import sys
import os
import numpy as np
import tifffile as tiff

def convert_file(in_path, out_path, global_min=None, global_max=None):
    img = tiff.imread(in_path)

    if not np.issubdtype(img.dtype, np.signedinteger):
        print(f"Skipping (not signed): {in_path}")
        return

    img = img.astype(np.float32)

    if global_min is None or global_max is None:
        min_val = img.min()
        max_val = img.max()
    else:
        min_val = global_min
        max_val = global_max

    if max_val == min_val:
        print(f"Skipping (flat image): {in_path}")
        return

    # Normalize to 0–255
    img_norm = (img - min_val) / (max_val - min_val)
    img_uint8 = (img_norm * 255).clip(0, 255).astype(np.uint8)

    tiff.imwrite(out_path, img_uint8)

def main():
    if len(sys.argv) not in [3, 5]:
        print("Usage:")
        print("  script.py <input_dir> <output_dir>")
        print("  script.py <input_dir> <output_dir> <global_min> <global_max>")
        sys.exit(1)

    in_dir = sys.argv[1]
    out_dir = sys.argv[2]

    global_min = float(sys.argv[3]) if len(sys.argv) == 5 else None
    global_max = float(sys.argv[4]) if len(sys.argv) == 5 else None

    os.makedirs(out_dir, exist_ok=True)

    for fname in os.listdir(in_dir):
        if fname.lower().endswith((".tif", ".tiff")):
            in_path = os.path.join(in_dir, fname)
            out_path = os.path.join(out_dir, fname)

            print(f"Processing: {fname}")
            convert_file(in_path, out_path, global_min, global_max)

if __name__ == "__main__":
    main()
