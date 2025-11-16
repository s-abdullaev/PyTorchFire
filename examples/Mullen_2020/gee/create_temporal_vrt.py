"""
Create a temporal Virtual Raster (VRT) from MODIS Terra and Aqua GeoTIFF files.

MODIS provides thermal observations four times per day:
- Terra at 10:30 and 22:30 local time
- Aqua at 13:30 and 01:30 local time

This script combines files from MODIS_Terra and MODIS_Aqua folders into a single
VRT with bands ordered chronologically, with proper temporal metadata for QGIS.
"""

import os
import glob
from datetime import datetime, timedelta
from pathlib import Path


def get_observation_time(date_str, platform, band_name):
    """
    Get the observation time for a given date, platform, and band.

    Parameters:
    -----------
    date_str : str
        Date in YYYYMMDD format
    platform : str
        'Terra' or 'Aqua'
    band_name : str
        'LST_Day_1km' or 'LST_Night_1km'

    Returns:
    --------
    datetime : datetime object with the observation time
    """
    date = datetime.strptime(date_str, "%Y%m%d")

    if platform == "Terra":
        if band_name == "LST_Day_1km":
            # Terra Day observation at 10:30
            return date.replace(hour=10, minute=30, second=0)
        else:  # LST_Night_1km
            # Terra Night observation at 22:30
            return date.replace(hour=22, minute=30, second=0)
    else:  # Aqua
        if band_name == "LST_Day_1km":
            # Aqua Day observation at 13:30
            return date.replace(hour=13, minute=30, second=0)
        else:  # LST_Night_1km
            # Aqua Night observation at 01:30 (early morning of the same date)
            return date.replace(hour=1, minute=30, second=0)


def create_temporal_vrt(terra_dir, aqua_dir, output_vrt, band_selection="both"):
    """
    Create a temporal VRT combining MODIS Terra and Aqua observations.

    Parameters:
    -----------
    terra_dir : str
        Directory containing MODIS Terra GeoTIFF files
    aqua_dir : str
        Directory containing MODIS Aqua GeoTIFF files
    output_vrt : str
        Output VRT file path
    band_selection : str
        'both' for all observations, 'day' for day only, 'night' for night only
    """
    # Find all Terra and Aqua files
    terra_pattern = os.path.join(terra_dir, "MODIS_MullenRegion_Terra_LST_*.tif")
    aqua_pattern = os.path.join(aqua_dir, "MODIS_MullenRegion_Aqua_LST_*.tif")

    terra_files = sorted(glob.glob(terra_pattern))
    aqua_files = sorted(glob.glob(aqua_pattern))

    if not terra_files and not aqua_files:
        raise ValueError(f"No .tif files found in {terra_dir} or {aqua_dir}")

    print(f"Found {len(terra_files)} Terra files and {len(aqua_files)} Aqua files")

    # Collect all observations with their metadata
    observations = []

    # Process Terra files
    for tif_file in terra_files:
        basename = os.path.basename(tif_file)
        date_str = basename.split("_")[-1].replace(".tif", "")

        # Add Day observation (band 1)
        if band_selection in ["both", "day"]:
            obs_time = get_observation_time(date_str, "Terra", "LST_Day_1km")
            observations.append(
                {
                    "file": tif_file,
                    "band": 1,
                    "platform": "Terra",
                    "band_name": "LST_Day_1km",
                    "date_str": date_str,
                    "datetime": obs_time,
                    "description": f"{date_str}_Terra_Day_1030",
                }
            )

        # Add Night observation (band 2)
        if band_selection in ["both", "night"]:
            obs_time = get_observation_time(date_str, "Terra", "LST_Night_1km")
            observations.append(
                {
                    "file": tif_file,
                    "band": 2,
                    "platform": "Terra",
                    "band_name": "LST_Night_1km",
                    "date_str": date_str,
                    "datetime": obs_time,
                    "description": f"{date_str}_Terra_Night_2230",
                }
            )

    # Process Aqua files
    for tif_file in aqua_files:
        basename = os.path.basename(tif_file)
        date_str = basename.split("_")[-1].replace(".tif", "")

        # Add Night observation (band 2) - this is 01:30, earliest in the day
        if band_selection in ["both", "night"]:
            obs_time = get_observation_time(date_str, "Aqua", "LST_Night_1km")
            observations.append(
                {
                    "file": tif_file,
                    "band": 2,
                    "platform": "Aqua",
                    "band_name": "LST_Night_1km",
                    "date_str": date_str,
                    "datetime": obs_time,
                    "description": f"{date_str}_Aqua_Night_0130",
                }
            )

        # Add Day observation (band 1)
        if band_selection in ["both", "day"]:
            obs_time = get_observation_time(date_str, "Aqua", "LST_Day_1km")
            observations.append(
                {
                    "file": tif_file,
                    "band": 1,
                    "platform": "Aqua",
                    "band_name": "LST_Day_1km",
                    "date_str": date_str,
                    "datetime": obs_time,
                    "description": f"{date_str}_Aqua_Day_1330",
                }
            )

    # Sort observations chronologically
    observations.sort(key=lambda x: x["datetime"])

    print(f"Total observations to include: {len(observations)}")
    print(
        f"Date range: {observations[0]['datetime']} to {observations[-1]['datetime']}"
    )

    # Get raster properties from first available file
    try:
        import rasterio
    except ImportError:
        raise ImportError(
            "rasterio is required. Install with: pip install rasterio or uv pip install rasterio"
        )

    # Try to open a file to get raster properties
    sample_file = None
    sample_obs = None
    sample_dataset = None
    for obs in observations:
        try:
            sample_dataset = rasterio.open(obs["file"])
            sample_file = obs["file"]
            sample_obs = obs
            break
        except Exception as e:
            continue

    if sample_dataset is None:
        raise RuntimeError(
            f"Could not open any sample file. Check that files exist and are valid GeoTIFFs."
        )

    xsize = sample_dataset.width
    ysize = sample_dataset.height
    # Rasterio transform is Affine(a, b, c, d, e, f) which represents:
    #   [a  b  c]   =   [pixel_width  row_rotation  top_left_x]
    #   [d  e  f]       [col_rotation  -pixel_height  top_left_y]
    # GDAL geotransform is [top_left_x, pixel_width, row_rotation, top_left_y, col_rotation, -pixel_height]
    affine_transform = sample_dataset.transform
    gt_list = [
        affine_transform[2],  # top-left x
        affine_transform[0],  # pixel width
        affine_transform[1],  # row rotation
        affine_transform[5],  # top-left y
        affine_transform[3],  # col rotation
        affine_transform[4],  # -pixel_height (rasterio stores as negative already)
    ]
    projection = sample_dataset.crs.to_wkt() if sample_dataset.crs else ""

    # Get data type - rasterio uses numpy dtypes, convert to GDAL type names
    band_data_type = sample_dataset.dtypes[sample_obs["band"] - 1]
    dtype_mapping = {
        "uint8": "Byte",
        "uint16": "UInt16",
        "int16": "Int16",
        "uint32": "UInt32",
        "int32": "Int32",
        "float32": "Float32",
        "float64": "Float64",
    }
    data_type_name = dtype_mapping.get(str(band_data_type), "Float32")

    print(f"Raster properties (from {os.path.basename(sample_file)}):")
    print(f"  Size: {xsize} x {ysize}")
    print(f"  Data type: {data_type_name}")

    sample_dataset.close()

    # Create VRT XML
    vrt_xml = f"""<VRTDataset rasterXSize="{xsize}" rasterYSize="{ysize}">
    <SRS>{projection}</SRS>
    <GeoTransform>{', '.join(map(str, gt_list))}</GeoTransform>
"""

    # Add each observation as a band
    for i, obs in enumerate(observations):
        rel_path = os.path.relpath(obs["file"], os.path.dirname(output_vrt))
        # Use forward slashes for VRT (works on Windows too)
        rel_path = rel_path.replace("\\", "/")

        # Format datetime for metadata
        dt_str = obs["datetime"].strftime("%Y-%m-%dT%H:%M:%S")
        date_str_iso = obs["datetime"].strftime("%Y-%m-%d")

        vrt_xml += f"""    <VRTRasterBand dataType="{data_type_name}" band="{i+1}">
        <Description>{obs['description']}</Description>
        <Metadata>
            <MDI key="ACQUISITION_DATE">{date_str_iso}</MDI>
            <MDI key="ACQUISITION_TIME">{obs['datetime'].strftime("%H:%M:%S")}</MDI>
            <MDI key="START_TIME">{dt_str}</MDI>
            <MDI key="END_TIME">{dt_str}</MDI>
            <MDI key="PLATFORM">{obs['platform']}</MDI>
            <MDI key="BAND_NAME">{obs['band_name']}</MDI>
        </Metadata>
        <SimpleSource>
            <SourceFilename relativeToVRT="1">{rel_path}</SourceFilename>
            <SourceBand>{obs['band']}</SourceBand>
            <SourceProperties RasterXSize="{xsize}" RasterYSize="{ysize}" DataType="{data_type_name}"/>
            <SrcRect xOff="0" yOff="0" xSize="{xsize}" ySize="{ysize}"/>
            <DstRect xOff="0" yOff="0" xSize="{xsize}" ySize="{ysize}"/>
        </SimpleSource>
    </VRTRasterBand>
"""

    vrt_xml += "</VRTDataset>"

    # Write VRT file
    with open(output_vrt, "w") as f:
        f.write(vrt_xml)

    print(f"\nCreated temporal VRT: {output_vrt}")
    print(f"Total bands: {len(observations)}")
    print(f"\nFirst 5 observations:")
    for obs in observations[:5]:
        print(f"  {obs['datetime']}: {obs['description']}")
    print(f"\nLast 5 observations:")
    for obs in observations[-5:]:
        print(f"  {obs['datetime']}: {obs['description']}")

    return output_vrt


if __name__ == "__main__":
    # Paths
    base_dir = Path(__file__).parent
    terra_dir = base_dir / "MODIS_Terra"
    aqua_dir = base_dir / "MODIS_Aqua"

    # Create VRT with all observations
    output_vrt = base_dir / "MODIS_Temporal_All.vrt"

    print("Creating temporal VRT from MODIS Terra and Aqua observations...")
    print("=" * 70)

    create_temporal_vrt(
        str(terra_dir), str(aqua_dir), str(output_vrt), band_selection="both"
    )

    # Also create separate VRTs for day and night if desired
    print("\n" + "=" * 70)
    print("Creating separate VRTs for Day and Night observations...")

    output_vrt_day = base_dir / "MODIS_Temporal_Day.vrt"
    create_temporal_vrt(
        str(terra_dir), str(aqua_dir), str(output_vrt_day), band_selection="day"
    )

    output_vrt_night = base_dir / "MODIS_Temporal_Night.vrt"
    create_temporal_vrt(
        str(terra_dir), str(aqua_dir), str(output_vrt_night), band_selection="night"
    )

    print("\n" + "=" * 70)
    print("Done! Created VRT files:")
    print(f"  - {output_vrt.name} (all observations)")
    print(f"  - {output_vrt_day.name} (day observations only)")
    print(f"  - {output_vrt_night.name} (night observations only)")
    print("\nTo use in QGIS:")
    print("1. Load the VRT file")
    print("2. Right-click layer → Properties → Temporal tab")
    print("3. Enable Temporal, Mode: 'Single Field with Date/Time'")
    print("4. Field: Use expression: to_datetime(@band_name, 'yyyyMMdd_HHmm')")
    print("   Or use: START_TIME metadata field")
