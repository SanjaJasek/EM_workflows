#!/usr/bin/env python3

import os
import re
import argparse
import tifffile
import xml.etree.ElementTree as ET

def get_fibics_metadata(filepath):
    # extract resolution and stage coordinates from Fibics Tag 51023
    with tifffile.TiffFile(filepath) as tiff:
        xml_str = tiff.pages[0].tags[51023].value
        root = ET.fromstring(xml_str)
        
        fov_x = float(root.find(".//Scan/FOV_X").text)
        width = int(root.find(".//Image/Width").text)
        pixel_size = fov_x / width
        
        x_um = float(root.find(".//MosaicInfo/X").text)
        y_um = float(root.find(".//MosaicInfo/Y").text)
        
        return {
            "name": os.path.basename(filepath),
            "x": x_um, "y": y_um, 
            "res": pixel_size, "w": width
        }

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def process_dir(dir_path, output_filepath):
    data = []
    for f in os.listdir(dir_path):
        if f.lower().endswith(('.tif', '.tiff')):
            try:
                data.append(get_fibics_metadata(os.path.join(dir_path, f)))
            except Exception as e:
                print(f"Error processing {f}: {e}")

    if not data:
        return False

    # calculate offsets relative to the top-left tile
    origin_x = min(d['x'] for d in data)
    origin_y = max(d['y'] for d in data)
    pixel_size = data[0]['res']
    tile_size = data[0]['w']

    data.sort(key=lambda d: natural_sort_key(d['name']))

    with open(output_filepath, 'w') as f:
        f.write(f"{{RESOLUTION}}\t{pixel_size * 1000:.0f}\n")
        f.write(f"{{TILE_SIZE}}\t{tile_size}\t{tile_size}\n")
        for d in data:
            px_off_x = round((d['x'] - origin_x) / pixel_size)
            px_off_y = round((origin_y - d['y']) / pixel_size)
            f.write(f"{d['name']}\t{px_off_x}\t{px_off_y}\n")
    return True

def main():
    parser = argparse.ArgumentParser(description="Create stitch coordinates for feabas workflow. Assumes that tiles have already been sorted with sort.sh")
    parser.add_argument("-i", "--input", required=True, help="Input directory containing numbered subfolders")
    parser.add_argument("-o", "--output", required=True, help="Output directory for stitch coordinates")
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # iterate through files in directory
    images = sorted(os.listdir(args.input), key=natural_sort_key)
	
    for imgfile in images:
        subdir_path = os.path.join(args.input, imgfile)
        
        if os.path.isdir(subdir_path):
            output_file = os.path.join(args.output, f"{imgfile}.txt")
            print(f"Processing folder: {imgfile}...", end=" ")
            
            if process_dir(subdir_path, output_file):
                print("Done.")
            else:
                print("Skipped (no valid TIFFs).")

if __name__ == "__main__":
    main()
