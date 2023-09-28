import os
import pandas as pd
from pathlib import Path
from sap_map_templates import create_sap_parameters, generate_animal_config

import os
from pathlib import Path
import pandas as pd


class SAPConfigGenerator:
    def __init__(self, input_folder, output_folder, animal_name):
        """
        Initialize the SAPConfigGenerator class.

        Parameters
        ----------
        input_folder : str or Path
            The path to the input folder containing the images.
        output_folder : str or Path
            The path to the folder where the output configuration files will be stored.
        animal_name : str
            The name of the animal whose data is being analyzed.

        """
        self.input_folder = input_folder
        self.animal_name = animal_name
        self.output_folder = output_folder
        self.ensure_output_folder_exists()

    def ensure_output_folder_exists(self):
        """
        Ensure that the output folder exists. Create it if it does not.
        """
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def read_rescaling_file(self, rescaling_file_path):
        """
        Read a rescaling file and return its contents as a dictionary.

        Parameters
        ----------
        rescaling_file_path : str or Path
            The path to the rescaling file.

        Returns
        -------
        dict
            The rescaling data in dictionary form.
        """
        df = pd.read_table(rescaling_file_path, sep=" ")
        df.set_index("Name", inplace=True)
        return df.to_dict()

    def count_tif_files(self, folder_path):
        """
        Count the number of TIFF files in a folder.

        Parameters
        ----------
        folder_path : str or Path
            The path to the folder to search for TIFF files.

        Returns
        -------
        int
            The number of TIFF files in the folder.
        """
        return sum(
            1 for file in os.listdir(folder_path) if file.lower().endswith(".tif")
        )

    def generate_sap_config(self, rescaling_data, time_ref_dict):
        """
        Generate a SAP configuration file.

        Parameters
        ----------
        rescaling_data : dict
            The rescaling data for the animal.
        time_ref_dict : dict
            The time reference data for the animal.

        Notes
        -----
        The function creates a SAP configuration file and saves it in the output folder.
        """
        # Count the number of TIFF files for the current animal
        end_frame = self.count_tif_files(
            os.path.join(self.input_folder.parent, self.animal_name)
        )

        # Determine the output file path
        output_file_path = os.path.join(
            self.output_folder, f"SAP_info_{self.animal_name.replace('-', '_')}.m"
        )

        # Extract specific rescaling data for the current animal
        resize_data = rescaling_data.get(self.animal_name, {})
        yml = resize_data.get("yML(pix)", "")
        xFactor = resize_data.get("xFactor", 1)
        yFactor = resize_data.get("yFactor", 1)
        ox = resize_data.get("Ox(pix)", 1100)
        oy = resize_data.get("Oy(pix)", 700)

        # Get time reference for the current animal
        t_ref = time_ref_dict.get(self.animal_name, 71)
        start_frame = 1

        # Generate the content for the configuration file
        content = generate_animal_config(
            self.animal_name,
            start_frame,
            end_frame,
            4,  # This appears to be a constant, consider documenting or making it a parameter
            yml,
            xFactor,
            yFactor,
            ox,
            oy,
            t_ref,
            input_folder=self.input_folder.parent,
        )

        # Write the configuration file
        with open(output_file_path, "w") as file:
            file.write(content)
        print(f"Generated file: {output_file_path}")

    def generate_sap_files(self, rescaling_data, time_ref_dict):
        """
        Generate SAP configuration files for all relevant files in the input folder.

        Parameters
        ----------
        rescaling_data : dict
            The rescaling data for the animals.
        time_ref_dict : dict
            The time reference data for the animals.
        """
        movie_path = Path("full_movies")
        for file_name in os.listdir(self.input_folder / movie_path):
            if file_name[0].isalpha() and not file_name.lower().endswith(
                (".png", ".tif")
            ):
                continue
            self.generate_sap_config(rescaling_data, time_ref_dict)


def generate_sap_files(
    input_folder_path, animal_name, algorithm_to_run={}, experience_parameters={}
):
    """
    Main function to generate SAP configuration and parameter files.

    Parameters
    ----------
    input_folder_path : Path
        The path to the input folder containing the animal's data.
    animal_name : str
        The name of the animal whose data is being processed.
    algorithm_to_run : dict
        Dictionary specifying which algorithms to run. Expected keys are 'sr', 'piv', 'vm', 'ffbp', 'ct', 'aot'.
    experience_parameters : dict, optional
        Additional parameters for the experience. Default is an empty dictionary.

    Notes
    -----
    This function initializes a `SAPConfigGenerator` object, reads rescaling data,
    generates SAP configuration files, and finally generates a SAP parameters file.
    """

    # Create output folder path
    output_folder_path = input_folder_path / "SAP_info"

    # Initialize the SAPConfigGenerator
    config_generator = SAPConfigGenerator(
        input_folder_path, output_folder_path, animal_name
    )

    # Define the path for the rescaling file
    rescaling_file_path = f"{input_folder_path}/{animal_name}_rescaled_21h40_nMacroUsed=4/rescalingOutput.txt"

    # Try to read the rescaling file
    try:
        rescaling_data = config_generator.read_rescaling_file(rescaling_file_path)
    except FileNotFoundError:
        print("file does not exist")
        return

    # Check if rescaling data is available
    if not rescaling_data:
        print("Warning: No rescaling file could be read.")
        return

    # Placeholder for time reference data, populate this as needed
    time_ref_dict = {}

    # Generate SAP configuration files
    config_generator.generate_sap_files(rescaling_data, time_ref_dict)

    # Create SAP parameters based on the algorithms to run
    content = create_sap_parameters(
        algorithm_to_run.get("sr", 0),
        algorithm_to_run.get("piv", 0),
        algorithm_to_run.get("vm", 0),
        algorithm_to_run.get("ffbp", 0),
        algorithm_to_run.get("ct", 0),
        algorithm_to_run.get("aot", 0),
    )

    # Write the SAP parameters to a file
    output_file_path = output_folder_path / "SAP_parameters.m"
    with open(output_file_path, "w") as file:
        file.write(content)
    print(f"Generated file: {output_file_path}")
