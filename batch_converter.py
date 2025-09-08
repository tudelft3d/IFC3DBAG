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
import concurrent.futures

def load_cityjson(infile, ignore_duplicate_keys=False):
    """
    Loads a CityJSON file using cjio's cityjson.reader with optional duplicate key ignoring.
    Returns a CityJSON object.
    """
    try:
        cm = cityjson.reader(file=infile, ignore_duplicate_keys=ignore_duplicate_keys)
    import concurrent.futures
    import multiprocessing

    def process_cityjson_file(cityjson_file, lods, ignore_duplicate):
        import os, zipfile
        from cityjson2ifc import Cityjson2ifc
        from batch_converter import load_cityjson
        zip_filename = cityjson_file.replace(".city.json", ".ifc.zip")
        if os.path.isfile(zip_filename):
            print(f"Zip file {zip_filename} found. Skipping {cityjson_file}.")
            try:
                os.remove(cityjson_file)
            except Exception:
                pass
            return f"Skipped {cityjson_file}"

        output_ifc_files = []
        try:
            with open(cityjson_file, "r") as infile:
                print(f"Parsing {infile.name} ...")
                cm = load_cityjson(infile, ignore_duplicate_keys=ignore_duplicate)
                for lod in lods:
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
                        print(f"Conversion completed for {cityjson_file} at LoD {lod}.")
                        output_ifc_files.append(output_ifc_path)
                    except Exception as ex:
                        print(f"Failed to convert {cityjson_file} at LoD {lod}.\nError: {ex}")
                        continue
                if output_ifc_files:
                    with zipfile.ZipFile(zip_filename, 'w') as zf:
                        for ifc_file in output_ifc_files:
                            zf.write(ifc_file, os.path.basename(ifc_file))
                    print(f"Zipped IFC files into {zip_filename}.")
        except Exception as e:
            print(f"Error processing {cityjson_file}: {e}")
        finally:
            for ifc_file in output_ifc_files:
                try:
                    os.remove(ifc_file)
                    print(f"Deleted IFC file: {ifc_file}")
                except Exception:
                    pass
            try:
                os.remove(cityjson_file)
                print(f"Cleaned up temporary file: {cityjson_file}")
            except Exception:
                pass
        print(f"Processed {cityjson_file} and created {zip_filename}.")
        return f"Processed {cityjson_file} and created {zip_filename}."

    max_workers = multiprocessing.cpu_count()
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_cityjson_file, cityjson_file, lods, ignore_duplicate) for cityjson_file in cityjson_files]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            print(result)

    click.echo("All CityJSON files have been processed.")


    cityjson_files = glob.glob(os.path.join(input_dir, "**", "*.city.json"), recursive=True)
    click.echo(f"Found {len(cityjson_files)} .city.json files.")


    # Define which LODs to export
    lods = ["0", "1.2", "1.3", "2.2"]

    

    def process_cityjson_file(cityjson_file):
        zip_filename = cityjson_file.replace(".city.json", ".ifc.zip")
        if os.path.isfile(zip_filename):
            click.echo(f"Zip file {zip_filename} found. Skipping {cityjson_file}.")
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
                for lod in lods:
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
            try:
                os.remove(cityjson_file)
                #click.echo(f"Cleaned up temporary file: {cityjson_file}")
            except Exception:
                pass
        click.echo(f"Processed {cityjson_file} and created {zip_filename}.")

    # Use ThreadPoolExecutor to process files in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
        futures = [executor.submit(process_cityjson_file, cityjson_file) for cityjson_file in cityjson_files]
        for future in concurrent.futures.as_completed(futures):
            # This will raise any exceptions that occurred in the threads
            result = future.result()
            #print(result)

    click.echo("All CityJSON files have been processed.")

if __name__ == "__main__":
    main()
