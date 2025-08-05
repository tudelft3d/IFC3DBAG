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
   ```

2. **(Optional) Create a virtual environment:**

For linux:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  
   ```
For Windows:
   ```
   python -m venv .venv
   .venv\Scripts\activate      
   ```
3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Batch Convert CityJSON to IFC**

   ```bash
   python3 batch_converter.py --input_dir /dir/to/cityjsongz
   ```

2. **Arguments:**

   - `--input_dir`: Used to difine the directory containing one or more compressed CityJSON files (`city.json.gz`) (CityJSON) from 3DBAG.
   - `--ignore_duplicate`: Ignore duplicate JSON keys in the CityJSON files.

---

## Contributing

1. Fork the repository.
2. Create a branch for your feature/fix:
   ```bash
   git checkout -b feature/some-improvement
   ```
3. Commit your changes:
   ```bash
   git commit -am 'Add some improvement'
   ```
4. Push to your branch:
   ```bash
   git push origin feature/some-improvement
   ```
5. Open a Pull Request on GitHub.

---


## Contact

For questions or suggestions, feel free to open an issue.


