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

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Batch Convert CityJSON to IFC**

   Make the `batch_converter` script executable or run it using Python:

   ```bash
   chmod +x batch_converter                                                     # Make it executable (Linux/Mac)
   ./batch_converter /path/to/cityjson_folder /path/to/output_ifc_folder        # Run directly
   python batch_converter /path/to/cityjson_folder /path/to/output_ifc_folder   # Or via Python
   ```

2. **Parameters:**

   - `/path/to/cityjson_folder`: Directory containing one or more `.json` (CityJSON) files from 3DBAG.
   - `/path/to/output_ifc_folder`: Directory where the generated IFC files will be saved.

3. **Example Execution**:

   ```bash
   python batch_converter ./cityjson_data ./ifc_output
   ```

   This command processes all CityJSON files in `./cityjson_data` and saves IFC files into `./ifc_output`.

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

## License

This project incorporates code from the ifccityjson library, which is distributed under the LGPLv3 (or a similar license).

Your repository should:

- Retain the same license OR
- Use a license compatible with the LGPLv3.

Include a LICENSE file and make sure you adhere to any additional requirements (such as listing changes, including copyright notices, etc.).

---

## Contact

For questions or suggestions, feel free to open an issue or contact [your email / GitHub handle].

---

## Additional Tips

- **Validate Conversions**: Always check the output IFC files in a compatible IFC viewer (e.g., BlenderBIM, FreeCAD, or other IFC validation tools) to ensure accuracy.
- **Documentation**: Keep this README updated if you add new features or change CLI parameters.
- **Automated Testing**: Consider adding unit tests or sample data tests to ensure consistent conversion results over time.

