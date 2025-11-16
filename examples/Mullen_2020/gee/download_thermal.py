import ee

# Initialize Earth Engine with your project
ee.Initialize(project="gisday-477302")

# ----------------------- COMMON PARAMETERS -----------------------

# AOI: W S E N (your Mullen region)
west = -106.478103457299
south = 40.9156198271091
east = -106.020931772113
north = 41.2802105182423
aoi = ee.Geometry.Rectangle([west, south, east, north])

# Date range (inclusive start, exclusive end for filterDate)
start_date = "2020-09-17"
end_date_exclusive = "2020-10-21"  # to cover up to 2020-10-20

# LST bands we care about
lst_bands = ["LST_Day_1km", "LST_Night_1km"]


# ----------------------- HELPER: EXPORT EACH IMAGE SEPARATELY -----------------------


def export_modis_lst(collection_id, platform_tag, export_prefix):
    """
    Export each MODIS LST image separately with date-based filenames.
    collection_id: e.g. 'MODIS/061/MOD11A1'
    platform_tag:  e.g. 'Terra' or 'Aqua'
    export_prefix: base prefix for description/fileNamePrefix
    """
    # 1) Load, filter, and select bands
    col = (
        ee.ImageCollection(collection_id)
        .filterDate(start_date, end_date_exclusive)
        .filterBounds(aoi)
        .select(lst_bands)
    )

    # 2) Export each image separately
    def export_single_image(img, date_str):
        """Export a single image with date and platform in filename"""
        img_float = img.toFloat()

        description = f"{export_prefix}_{platform_tag}_LST_{date_str}"
        file_prefix = f"{export_prefix}_{platform_tag}_LST_{date_str}"

        task = ee.batch.Export.image.toDrive(
            image=img_float,
            description=description,
            folder=f"GEE_exports/thermal_data/{platform_tag}",  # separate folders by platform
            fileNamePrefix=file_prefix,
            region=aoi,
            scale=1000,  # ~1 km native MODIS LST resolution
            maxPixels=1e13,
            crs="EPSG:4326",
        )
        return task

    # Get list of images and export each one
    image_list = col.toList(col.size())
    num_images = image_list.size().getInfo()

    print(f"Found {num_images} images for {platform_tag}. Starting exports...")

    for i in range(num_images):
        img = ee.Image(image_list.get(i))
        date_str = img.date().format("yyyyMMdd").getInfo()  # Get Python string first
        task = export_single_image(img, date_str)
        task.start()
        print(f"Started export for {platform_tag} date {date_str}")

    print(f"All {num_images} exports started for {platform_tag}.")


# ----------------------- RUN EXPORTS FOR TERRA & AQUA -----------------------

# Terra LST (MOD11A1)
export_modis_lst(
    collection_id="MODIS/061/MOD11A1",
    platform_tag="Terra",
    export_prefix="MODIS_MullenRegion",
)

# Aqua LST (MYD11A1)
export_modis_lst(
    collection_id="MODIS/061/MYD11A1",
    platform_tag="Aqua",
    export_prefix="MODIS_MullenRegion",
)
