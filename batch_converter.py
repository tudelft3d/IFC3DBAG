import sys
import warnings
import gc
import os
import glob
import click
import zipfile
import gzip

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
              help="Directory containing .city.json.gz files.")
@click.option('--ignore_duplicate', is_flag=True, default=False,
              help="Ignore duplicate JSON keys in CityJSON files.")
def main(input_dir, ignore_duplicate):
    """
    Finds all .city.json.gz files in the input directory, unzips them, converts each to IFC for multiple LoDs and zips them in one file.
    """
    # 1. Identify all .city.json.gz files recursively
    input_dir = os.path.abspath(os.path.expanduser(input_dir))
    cityjson_gz_files = glob.glob(os.path.join(input_dir, "**", "*.city.json.gz"), recursive=True)

    if not cityjson_gz_files:
        click.echo("No .city.json.gz files found in the specified directory.")
        sys.exit(1)

    click.echo(f"Found {len(cityjson_gz_files)} .city.json.gz files.")

    click.echo("Unzipping files...")
    # 2. Unzip the .city.json.gz files
    cityjson_files = []
    for gz_file in cityjson_gz_files:
        try:
            with gzip.open(gz_file, 'rb') as f_in:
                cityjson_file = gz_file.replace('.gz', '')
                with open(cityjson_file, 'wb') as f_out:
                    f_out.write(f_in.read())
            cityjson_files.append(cityjson_file)
            click.echo(f"Unzipped {gz_file} to {cityjson_file}.")
        except Exception as e:
            click.echo(f"Failed to unzip {gz_file}: {e}")
    if not cityjson_files:
        click.echo("No valid CityJSON files found after unzipping.")
        sys.exit(1)
    click.echo(f"Total unzipped CityJSON files: {len(cityjson_files)}")

    # Define which LODs to export
    lods = ["0", "1.2", "1.3", "2.2"]

    for cityjson_file in cityjson_files:
        # Build the zip file name with the same path as cityjson_file but with .ifc.zip suffix
        zip_filename = cityjson_file.replace(".city.json", ".ifc.zip")

        # If that ZIP already exists, skip processing
        if os.path.isfile(zip_filename):
            click.echo(f"Zip file {zip_filename} found. Skipping {cityjson_file}.")
            os.remove(cityjson_file)  # Remove the unzipped file
            continue

        # Track files to clean up
        output_ifc_files = []
        
        try:
            # Process the city.json file
            with open(cityjson_file, "r") as infile:
                click.echo(f"Parsing {infile.name} ...")

                # 2. Load the CityJSON
                cm = load_cityjson(infile, ignore_duplicate_keys=ignore_duplicate)

                # 3. Convert for each LOD
                for lod in lods:
                    converter = Cityjson2ifc()

                    # Create the IFC output path
                    output_ifc_path = cityjson_file.replace(".city.json", f"-{lod}.ifc")

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
                        output_ifc_files.append(output_ifc_path)
                    except Exception as ex:
                        click.echo(f"Failed to convert {cityjson_file} at LoD {lod}.\nError: {ex}")
                        continue

                # 6. After generating all IFC files, zip them together
                if output_ifc_files:  # Only try to zip if we actually have IFC files
                    with zipfile.ZipFile(zip_filename, 'w') as zf:
                        for ifc_file in output_ifc_files:
                            # Write the IFC file into the ZIP, 
                            # but store it under its base name inside the ZIP
                            zf.write(ifc_file, os.path.basename(ifc_file))
                    click.echo(f"Zipped IFC files into {zip_filename}.")

        except Exception as e:
            click.echo(f"Error processing {cityjson_file}: {e}")
            
        finally:
            try:
                # Delete the IFC files after zipping
                for ifc_file in output_ifc_files:
                        os.remove(ifc_file)
                        click.echo(f"Deleted IFC file: {ifc_file}")     
                # Clean up the temporary unzipped file

                os.remove(cityjson_file)
                click.echo(f"Cleaned up temporary file: {cityjson_file}")
            except OSError as e:
                click.echo(f"Error deleting temporary files: {e}")
            
        click.echo(f"Processed {cityjson_file} and created {zip_filename}.")


    click.echo("All CityJSON files have been processed.")

if __name__ == "__main__":
    main()
