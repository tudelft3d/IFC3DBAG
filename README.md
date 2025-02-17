# CityJSON to IFC Batch Converter for 3DBAG

This repository provides scripts and modified library files to convert [3DBAG](https://3dbag.nl/) CityJSON files into the Industry Foundation Classes (IFC) format. It leverages modified versions of [ifccityjson](https://github.com/IfcOpenShell/IfcOpenShell/tree/master/src/ifccityjson) from the [IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) project to handle conversion logic.

---

## Contents

- **`batch_converter`**  
  Main script to process multiple CityJSON files in batch and produce corresponding IFC files.

- **`modified_file_1.py`** and **`modified_file_2.py`**  
  Customized modules based on the ifccityjson library. Changes could include additional geometry handling, feature support, or bug fixes specifically for the 3DBAG dataset.

---

## Features

- **Batch Conversion**: Convert entire folders of 3DBAG CityJSON files into IFC in a single run.  
- **Custom Logic**: Enhanced geometry and attribute handling tailored to the 3DBAG dataset.  
- **Command-Line Interface**: Simple CLI usage — provide the input folder and the output folder to generate IFCs.

---

## Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/your-username/cityjson-to-ifc-batch.git
   cd cityjson-to-ifc-batch
