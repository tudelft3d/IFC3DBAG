import sys
import warnings
import gc
import os
import glob
import click
import zipfile

from cjio import errors, cityjson
from cityjson2ifc import Cityjson2ifc

def load_cityjson(infile, ignore_duplicate_keys=False):
    """
    Loads a CityJSON file using cjio's cityjson.reader with optional duplicate key ignoring.
    Returns a CityJSON object.
    """
    try:
        cm = cityjson.reader(file=infile, ignore_duplicate_keys=ignore_duplicate_keys)
    except ValueError as e:
        raise click.ClickException(f'{e}: "{infile.name}".')
    except IOError as e:
        raise click.ClickException(f'Invalid file: "{infile.name}".\n{e}')

    # Check version and capture warnings
    try:
        with warnings.catch_warnings(record=True) as w:
            cm.check_version()
            if w:  # If any warnings were captured
                for warn in w:
                    # Print or log the warning messages if needed
                    click.echo(f"Warning: {warn.message}")
    except errors.CJInvalidVersion as e:
        raise click.ClickException(e.msg)

    # If the purpose is to clear out cityobjects for memory reasons, do it explicitly
    cm.cityobjects = {}
    cm.load_from_j(transform=False)

    # The next line also clears the "CityObjects" in cm.j explicitly
    cm.j["CityObjects"] = {}

    # Force garbage collection to free memory
    gc.collect()

    return cm

@click.command()
@click.option('--input_dir', default="/data/amir/decompressed", show_default=True,
              help="Directory containing .city.json files.")
@click.option('--ignore_duplicate', is_flag=True, default=False,
              help="Ignore duplicate JSON keys in CityJSON files.")
def main(input_dir, ignore_duplicate):
    """
    Finds all .city.json files in the input directory, converts each to IFC for multiple LoDs,
    and then zips the results in ~/IFC3DBAG/ZIP/.
    """
    # 1. Identify all .city.json files
    input_dir = os.path.abspath(os.path.expanduser(input_dir))
    cityjson_files = glob.glob(os.path.join(input_dir, "*.city.json"))

    if not cityjson_files:
        click.echo("No .city.json files found in the specified directory.")
        sys.exit(1)

    # Define your output locations
    ifc_output_dir = os.path.abspath(os.path.expanduser("~/IFC3DBAG/output"))
    zip_output_dir = os.path.abspath(os.path.expanduser("~/IFC3DBAG/ZIP"))

    # Ensure both directories exist
    os.makedirs(ifc_output_dir, exist_ok=True)
    os.makedirs(zip_output_dir, exist_ok=True)

    # Define which LODs to export
    lods = ["0", "1.2", "1.3", "2.2"]

    for cityjson_file in cityjson_files:
        # Build the zip file name in ~/IFC3DBAG/ZIP
        zip_filename = os.path.join(
            zip_output_dir,
            os.path.basename(cityjson_file).replace(".city.json", "-ifc.zip")
        )

        # If that ZIP already exists, skip processing
        if os.path.isfile(zip_filename):
            click.echo(f"Zip file {zip_filename} found. Skipping {cityjson_file}.")
            continue

        # Otherwise, process the city.json file
        with open(cityjson_file, "r") as infile:
            click.echo(f"Parsing {infile.name} ...")

            # 2. Load the CityJSON
            cm = load_cityjson(infile, ignore_duplicate_keys=ignore_duplicate)

            output_ifc_files = []

            # 3. Convert for each LOD
            for lod in lods:
                converter = Cityjson2ifc()

                # Create the IFC output path
                base_name = os.path.basename(cityjson_file).replace(".city.json", f"-{lod}.ifc")
                output_ifc_path = os.path.join(ifc_output_dir, base_name)

                # 4. Configure the converter
                converter.configuration(
                    name_project="3DBAG Project",
                    name_site="3DBAG Site",
                    name_person_family="3Dgeoinfo",
                    name_person_given="3DGI/",
                    lod=lod,
                    file_destination=output_ifc_path
                )

                # 5. Run conversion
                try:
                    converter.convert(cm)
                    click.echo(f"Conversion completed for {cityjson_file} at LoD {lod}.")
                except Exception as ex:
                    click.echo(f"Failed to convert {cityjson_file} at LoD {lod}.\nError: {ex}")
                    continue

                output_ifc_files.append(output_ifc_path)

            # 6. After generating all IFC files, zip them together
            if output_ifc_files:  # Only try to zip if we actually have IFC files
                with zipfile.ZipFile(zip_filename, 'w') as zf:
                    for ifc_file in output_ifc_files:
                        # Write the IFC file into the ZIP, 
                        # but store it under its base name inside the ZIP
                        zf.write(ifc_file, os.path.basename(ifc_file))
                click.echo(f"Zipped IFC files into {zip_filename}.")

                # Delete the IFC files after zipping
                for ifc_file in output_ifc_files:
                    try:
                        os.remove(ifc_file)
                        click.echo(f"Deleted IFC file: {ifc_file}")
                    except OSError as e:
                        click.echo(f"Error deleting {ifc_file}: {e}")



    click.echo("All CityJSON files have been processed.")

if __name__ == "__main__":
    main()
