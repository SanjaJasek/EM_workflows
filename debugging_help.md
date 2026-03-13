fabas immediately reported "Finished." but did nothing.
: Check if all your paths are corect. Is your project directory defined correctly in general_configs.yaml? Are stitch coordinates in your project directory stitch/stitch_coord? Are the tile paths correct?
feabas and the shell it was running from is gone.
: Probably OOM killer got it. Reduce number of workers for stitch matching in stitching_configs.yaml
stitching looks terrible
: increase matching margin in stitching_configs.yaml
thumbnail alignment looks good, but deformable looks bad
: change matching: working_mip_level in alignment_configs.yaml
