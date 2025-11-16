import ee

# Initialize the Earth Engine module.
ee.Initialize(project="gisday-477302")

# ----------------------- PARAMETERS -----------------------
collection_id = "ECMWF/ERA5_LAND/DAILY_AGGR"
bands_to_select = ["u_component_of_wind_10m", "v_component_of_wind_10m"]

# Date range (inclusive for 2020-09-17 .. 2020-10-20)
start_date = "2020-09-17"
# filterDate end is exclusive, so use 2020-10-21 to include 2020-10-20
end_date_exclusive = "2020-10-21"

# AOI: W, S, E, N
west = -106.478103457299
south = 40.9156198271091
east = -106.020931772113
north = 41.2802105182423

aoi = ee.Geometry.Rectangle([west, south, east, north])

# ----------------------- LOAD & PREPARE COLLECTION -----------------------

# Load and filter collection by date and bands
col = (
    ee.ImageCollection(collection_id)
    .filterDate(start_date, end_date_exclusive)
    .select(bands_to_select)
    .filterBounds(aoi)
)

# ----------------------- EXPORT EACH IMAGE SEPARATELY -----------------------


def export_single_image(img, date_str):
    """Export a single image with date-based filename"""
    img_float = img.toFloat()

    description = f"ERA5L_wind_10m_{date_str}"
    file_prefix = f"era5land_wind_10m_{date_str}"

    task = ee.batch.Export.image.toDrive(
        image=img_float,
        description=description,
        folder="GEE_exports/wind_data",  # separate folder for wind data
        fileNamePrefix=file_prefix,
        region=aoi,
        scale=11132,  # ~0.1 degree (~11 km); adjust if you want native resolution (~9 km)
        maxPixels=1e13,
        crs="EPSG:4326",
    )
    return task


# Get list of images and export each one
image_list = col.toList(col.size())
num_images = image_list.size().getInfo()

print(f"Found {num_images} images. Starting exports...")

for i in range(num_images):
    img = ee.Image(image_list.get(i))
    date_str = img.date().format("yyyyMMdd").getInfo()  # Get Python string first
    task = export_single_image(img, date_str)
    task.start()
    print(f"Started export for date {date_str}")

print(
    f'All {num_images} exports started. Check the Tasks tab in the Code Editor or "earthengine task list".'
)
