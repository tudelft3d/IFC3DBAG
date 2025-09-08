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
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Define which LODs to export
LODS = ["0", "1.2", "1.3", "2.2"]

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

def unzip_cityjson_files(input_dir: Path):
    # Find all zipped files
    cityjson_gz_files = glob.glob(os.path.join(input_dir, "**", "*.city.json.gz"), recursive=True)
    if not cityjson_gz_files:
        click.echo("No .city.json.gz files found in the specified directory.")
        sys.exit(1)

    click.echo(f"Found {len(cityjson_gz_files)} .city.json.gz files.")
    click.echo("Unzipping files...")
    # Unzip the .city.json.gz files
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

def process_cityjson_file(cityjson_file: Path, ignore_duplicate: bool) -> None:
    zip_filename = cityjson_file.replace(".city.json", ".ifc.zip")
    if os.path.isfile(zip_filename):
        click.echo(f"Zip file {zip_filename} exists. Skipping {cityjson_file}.")
        try:
            os.remove(cityjson_file)
        except Exception:
            pass
        return

    output_ifc_files = []
    try:
        with open(cityjson_file, "r") as infile:
            click.echo(f"Parsing {infile.name} ...")
            cm = load_cityjson(infile, ignore_duplicate_keys=ignore_duplicate)
            for lod in LODS:
                converter = Cityjson2ifc()
                output_ifc_path = cityjson_file.replace(".city.json", f"-{lod}.ifc")
                converter.configuration(
                    name_project="3DBAG Project",
                    name_site="3DBAG Site",
                    name_person_family="3Dgeoinfo",
                    name_person_given="3DGI/",
                    lod=lod,
                    file_destination=output_ifc_path
                )
                try:
                    converter.convert(cm)
                    #click.echo(f"Conversion completed for {cityjson_file} at LoD {lod}.")
                    output_ifc_files.append(output_ifc_path)
                except Exception as ex:
                    #click.echo(f"Failed to convert {cityjson_file} at LoD {lod}.\nError: {ex}")
                    continue
            if output_ifc_files:
                with zipfile.ZipFile(zip_filename, 'w') as zf:
                    for ifc_file in output_ifc_files:
                        zf.write(ifc_file, os.path.basename(ifc_file))
                click.echo(f"Zipped IFC files into {zip_filename}.")
    except Exception as e:
        click.echo(f"Error processing {cityjson_file}: {e}")
    finally:
        for ifc_file in output_ifc_files:
            try:
                os.remove(ifc_file)
                #click.echo(f"Deleted IFC file: {ifc_file}")
            except Exception:
                pass
        # try:
        #     os.remove(cityjson_file)
        #     #click.echo(f"Cleaned up temporary file: {cityjson_file}")
        # except Exception:
        #     pass
    click.echo(f"Processed {cityjson_file} and created {zip_filename}.")


@click.command()
@click.option('--input_dir', default="/data/amir/decompressed", show_default=True,
              help="Directory containing .city.json.gz files.")
@click.option('--ignore_duplicate', is_flag=True, default=False,
              help="Ignore duplicate JSON keys in CityJSON files.")
@click.option('--unzip-files', is_flag=True, default=False,
              help="Unzip .city.json.gz files before processing.")
def main(input_dir, ignore_duplicate, unzip_files):
    """
    Finds all .city.json.gz files in the input directory, unzips them, converts each to IFC for multiple LoDs and zips them in one file.
    """
    input_dir = os.path.abspath(os.path.expanduser(input_dir))

    if unzip_files:
        unzip_cityjson_files(input_dir)

    cityjson_files = glob.glob(os.path.join(input_dir, "**", "*.city.json"), recursive=True)
    click.echo(f"Found {len(cityjson_files)} .city.json files.")


    #Use ProcessPoolExecutor to process files in parallel
    with ProcessPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_cityjson_file, cityjson_file, ignore_duplicate) for cityjson_file in cityjson_files]
        for future in as_completed(futures):
            result = future.result()

    click.echo("All CityJSON files have been processed.")

if __name__ == "__main__":
    main()
