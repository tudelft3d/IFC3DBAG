# CityJSON to IFC Batch Converter for 3DBAG

This repository provides scripts and modified library files to convert [3DBAG](https://3dbag.nl/) CityJSON files into the Industry Foundation Classes (IFC) format. It leverages modified versions of [ifccityjson](https://github.com/IfcOpenShell/IfcOpenShell/tree/master/src/ifccityjson) from the [IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) project to handle conversion logic.

---

## Contents

- **`batch_converter`**  
  Main script to process multiple CityJSON files in batch and produce corresponding IFC files.

- **`cityjson2ifc.py`** and **`geometry.py`**  
  Customized modules based on the ifccityjson library. Changes could include additional geometry handling, feature support, or bug fixes specifically for the 3DBAG dataset.

---

## Features

- **Batch Conversion**: Convert entire folders of 3DBAG CityJSON files into separate zipped IFC files for each tile in a single run.  
- **Custom Logic**: Enhanced geometry and attribute handling tailored to the 3DBAG dataset.  
- **Command-Line Interface**: Simple CLI usage — provide the input folder and the output folder to generate IFCs.

---

## Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/tudelft3d/IFC3DBAG.git
   cd IFC3DBAG
2. **(Optional) Create a virtual environment:**:

   ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/Mac
    venv\Scripts\activate      # Windows
   
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

---
## Usage

1. **Batch Convert CityJSON to IFC**

  Make the batch_converter script executable or run it using Python:

   ```bash
    # Make it executable (Linux/Mac)
    chmod +x batch_converter
    
    # Run directly
    ./batch_converter /path/to/cityjson_folder /path/to/output_ifc_folder
    
    # Or via Python
    python batch_converter /path/to/cityjson_folder /path/to/output_ifc_folder
