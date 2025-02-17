from cityjson2ifc import Cityjson2ifc
from cjio import errors, cityjson
import warnings
import gc
import os
import glob
import click
import zipfile

def load_cityjson(infile, ignore_duplicate_keys):
    try:
        cm = cityjson.reader(file=infile, ignore_duplicate_keys=ignore_duplicate_keys)
    except ValueError as e:
        raise click.ClickException('%s: "%s".' % (e, infile.name))
    except IOError as e:
        raise click.ClickException('Invalid file: "%s".\n%s' % (infile.name, e))

    try:
        with warnings.catch_warnings(record=True) as w:
            cm.check_version()
            click.echo(w)
    except errors.CJInvalidVersion as e:
        raise click.ClickException(e.msg)

    cm.cityobjects = dict()
    cm.load_from_j(transform=False)
    cm.j["CityObjects"] = {}
    gc.collect()
    return cm

# -------------------------------------------
# Main test logic
# -------------------------------------------

if __name__ == "__main__":
    # 1. Identify all .city.json files in the directory
    cityjson_files = glob.glob("*.city.json")

    if not cityjson_files:
        click.echo("No .city.json files found in the directory.")
        exit(1)

    for file in cityjson_files:
        with open(file, "r") as infile:
            click.echo(f"Parsing {infile.name}")
            c_m = load_cityjson(infile, None)
            lods = ["0","1.2","1.3","2.2"]
            output_ifc_files = []
            for lod in lods:
                # 3. Instantiate the converter
                converter = Cityjson2ifc()

                # 4. Configure converter
                output_ifc = file.replace(".city.json", f"-{lod}.ifc")
                converter.configuration(
                    name_project="3DBAG Project",
                    name_site="3DBAG Site",
                    name_person_family="3Dgeoinfo",
                    name_person_given="3DGI/",
                    lod=lod,
                    file_destination=output_ifc
                )

                # 5. Run converter
                converter.convert(c_m)

                # Keep track of this output file name
                output_ifc_files.append(output_ifc)  # ADDED

                # 6. (Optional) Print properties after conversion
                print(f"Conversion completed for {file} lod {lod}.")
                            # After generating all 4 IFC files, zip them together  
            zip_filename = file.replace(".city.json", "-ifc.zip")      
            with zipfile.ZipFile(zip_filename, 'w') as zf:         
                for ifc_file in output_ifc_files:                  
                    zf.write(ifc_file, os.path.basename(ifc_file)) 
            print(f"Zipped 4 IFC files into {zip_filename}")       

    click.echo("All CityJSON files have been processed.")