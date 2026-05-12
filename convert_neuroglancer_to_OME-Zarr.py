#!/usr/bin/env python3

import json
import argparse
import dask.array as da
from cloudvolume import CloudVolume
from ome_zarr.writer import write_multiscale

def main():
    parser = argparse.ArgumentParser(description="Convert Neuroglancer precomputed to OME-Zarr")
    parser.add_argument("input", help="Input precomputed directory")
    parser.add_argument("output", help="Output OME-Zarr directory")
    parser.add_argument("--chunks", type=int, nargs=3, default=[2048, 2048, 16],
                        help="Chunk size (X Y Z)")
    args = parser.parse_args()

    base = f"precomputed://file://{args.input}"
    info_path = f"{args.input}/info"

    # Load metadata
    with open(info_path) as f:
        info = json.load(f)

    scales = info["scales"]
    print(f"Found {len(scales)} scales")

    multiscale_arrays = []
    coordinate_transformations = []

    for mip, scale in enumerate(scales):
        print(f"\nOpening mip {mip}")

        vol = CloudVolume(
            base,
            mip=mip,
            progress=True,
            fill_missing=True
        )

        data = da.from_array(vol, chunks=(*args.chunks, 1))

        # Remove channel axis properly
        data = data.map_blocks(
            lambda x: x[..., 0],
            dtype=data.dtype,
            drop_axis=3
        )

        print("  shape:", data.shape)
        multiscale_arrays.append(data)

        res_nm = scale["resolution"]  # [X, Y, Z]

        coordinate_transformations.append([
            {
                "type": "scale",
                "scale": res_nm
            }
        ])

    # Explicit NGFF axes with units
    axes = [
        {"name": "x", "type": "space", "unit": "nanometer"},
        {"name": "y", "type": "space", "unit": "nanometer"},
        {"name": "z", "type": "space", "unit": "nanometer"},
    ]

    write_multiscale(
        multiscale_arrays,
        args.output,
        axes=axes,
        chunks=tuple(args.chunks),
        dtype="uint8",
        coordinate_transformations=coordinate_transformations
    )

    print("\n Done!")

if __name__ == "__main__":
    main()
