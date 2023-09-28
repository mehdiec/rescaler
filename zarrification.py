from pathlib import Path
from tqdm import tqdm
import zarr
import glob
import os
import numpy as np
import numcodecs

import scipy.io as spio
import warnings
from copy import deepcopy
from skimage.io import imread, imsave

MAPPING_KEY = {
    "xyStart": ["xStart", "yStart"],
    "xywh": ["xStart", "yStart", "boxWidth", "boxHeight"],
    "Coordinates": ["grid_xStart", "grid_yStart"],
    "FrameArray": ["FrameArray"],
    "TimeArray": ["TimeArray"],
}


QUANTITIES_ATTRIBUTES = [
    "xywh",
    "Overlap",
    "Coordinates",
    "TimeArray",
    "FrameArray",
]


def format_4_decimals(num):
    """
    Format a number to have 4 digits, zero-padded.

    Parameters:
    -----------
    num : int
        The number to format. Must be in the range [0, 9999].

    Returns:
    --------
    str
        The formatted string with four digits.

    Raises:
    -------
    ValueError
        If the provided number is not within the specified range.
    """
    if 0 <= num <= 9999:
        return "{:04}".format(num)
    else:
        raise ValueError(
            "Number out of range. Please provide a number between 0 and 9999."
        )


def save_stack(folder_path, base_name, stack, extension="png"):
    """
    Save a 3D image stack as individual 2D image files.

    This function iterates through each 2D slice of a given 3D image stack and saves
    them as separate image files in the specified folder. The filenames are constructed
    by combining the provided base name with a zero-padded frame number.

    Parameters:
    -----------
    folder_path : str
        Path to the destination folder where the 2D image files will be saved.

    base_name : str
        Base name to be used for the saved image files. Each file will be named in the format:
        {base_name}_{frame_number}.png, where frame_number is a zero-padded four-digit number
        starting from 0001.

    stack : numpy.ndarray
        3D image stack where the first dimension represents the number of 2D slices.
    """
    global current_progress
    for i in tqdm(range(stack.shape[0])):
        current_progress = int((i / (stack.shape[0] - 1)) * 100)
        frame_number = format_4_decimals(i + 1)
        filename = f"{base_name}_{frame_number}.{extension}"
        output_file = os.path.join(folder_path, filename)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            imsave(output_file, stack[i])


def load_stack(
    folder_path: list, motif: str, expected_size=None, as_stack=True
) -> (list, np.array):
    """
    Load a sequence of image files into a stack (3D array) or a list of 2D arrays.

    This function is primarily used for loading frames of a movie or slices of a 3D volume.

    Parameters
    ----------
    folder_path : str
        The path to the directory containing the image files.
    motif : str
        A string that specifies the pattern to match files.
        For example, '*.png' would match all PNG files in the specified directory.
    expected_size : tuple, optional
        The expected size of each image. If provided, only images of this size will be included in the output.
        Default is None.
    as_stack : bool, optional
        Whether to return the images as a 3D array (True) or as a list of 2D arrays (False). Default is True.

    Returns
    -------
    list
        A list containing the paths to the image files that were loaded.
    np.array
        If 'as_stack' is True, a 3D numpy array containing the image data.
        If 'as_stack' is False, a list of 2D numpy arrays with each element representing an individual image.

    """
    # Fetching paths
    global current_progress  # Declare it as a global variable
    files = sorted(glob.glob(os.path.join(folder_path, motif)))
    print(f"Found {len(files)} images matching '{motif}'")
    # Importing individual frames

    pbar = tqdm(files, position=0, leave=True)
    frames = []

    for i, file in enumerate(pbar):  # Add enumerate to get index i
        img = np.array(imread(file))
        if expected_size and img.shape == expected_size:
            frames.append(img)
        else:
            frames.append(img)

        # Update progress
        current_progress = (i / len(files)) * 100
    if as_stack:
        if frames:
            movie = np.stack(frames, axis=0)
        else:
            return 0
    else:
        movie = frames

    return [files, movie]


def extract_and_store_data(
    data_path, motif, dataset_name, group, height, width, extension="png"
):
    """
    Load and store data from a specified path into a zarr group.

    Parameters:
    -----------
    data_path : str
        Path to the folder containing data files.
    dataset_name : str
        Name of the dataset to create in the zarr group.
    group : zarr.hierarchy.Group
        Zarr group where the dataset will be stored.
    height : int
        Height of the images.
    width : int
        Width of the images.

    Returns:
    --------
    data : np.ndarray
        Loaded and processed data.
    """
    print(f"Extracting {dataset_name}")
    data = load_stack(data_path, motif=f"{motif}*.{extension}", as_stack=True)[
        1
    ].astype(np.uint8)
    group.create_dataset(
        dataset_name, data=data, dtype=data.dtype, chunks=(1, height, width)
    )
    return data


def store_data_in_zarr(
    zarr_path, raw_image_path, outlines_path, masks_path, sap_folder
):
    """
    Initialize a zarr directory, create groups, and store raw images, outlines, and masks.

    Parameters:
    -----------
    zarr_path : str
        Path to the zarr directory to be created.
    raw_image_path : str
        Path to the folder containing raw images.
    outlines_path : str
        Path to the folder containing image outlines.
    masks_path : str
        Path to the folder containing image masks.

    Note:
    -----
    The function also creates a SAP_folder inside the zarr directory and stores
    the raw images as a sequence of tif images for compatibility with the pipeline
    """

    # Create the output folder
    try:
        # Attempt to create the output folder
        animal = zarr.open_group(zarr_path, mode="w-")
    except zarr.errors.ContainsGroupError:
        # If a group already exists, open it in read-write mode
        animal = zarr.open_group(zarr_path, mode="a")
    animal_name = os.path.basename(os.path.normpath(zarr_path))

    # Create the first level structure if it doesn't exist
    groups = ["METADATA", "TENSORS", "IMAGE", "TRACKING"]
    for group in groups:
        if group in animal:
            continue
        animal.create_groups(group)

    sap_dest = os.path.join(zarr_path, str(sap_folder).split("/")[-1])
    print("sap_dest   ", sap_dest)

    # Load and store raw images
    print("Extracting raw images")
    raw_image = load_stack(raw_image_path, motif="*.tif", as_stack=True)[1].astype(
        np.uint8
    )
    if isinstance(raw_image, int):
        return
    width, height = raw_image.shape[1:]
    if "raw" not in animal.IMAGE:
        animal.IMAGE.create_dataset(
            "raw", data=raw_image, dtype=raw_image.dtype, chunks=(1, height, width)
        )

        # Save raw images as a list of tif files for the pipeline
        save_stack(zarr_path, animal_name, raw_image, extension="tif")

    # Load and store outlines
    if "outlines" not in animal.IMAGE:
        print(outlines_path)
        outlines = extract_and_store_data(
            outlines_path, "seg", "outlines", animal.IMAGE, height, width
        )

    # Load and store masks
    if "masks" not in animal.IMAGE:
        masks = extract_and_store_data(
            masks_path, "roi", "masks", animal.IMAGE, height, width
        )


def format_xyStart_values(value):
    """
    Parse and format 'xyStart' values from a given string.

    Parameters
    ----------
    value : str
        The string containing 'xyStart' values.

    Returns
    -------
    list
        A list of two integers representing 'xStart' and 'yStart'.
        If the value is not valid, returns [None, None].

    Notes
    -----
    The input string is expected to be enclosed in brackets and the values can be separated either by a comma or space.
    """
    values = []
    # Check if the string between brackets is not empty
    if value[1:-1].strip():
        # Split the values based on either comma or space
        if "," in value[1:-1]:
            value = [x for x in value[1:-1].split(",")]
        elif " " in value[1:-1]:
            value = [x for x in value[1:-1].split(" ")]

        # Append integer values for xStart and yStart
        values.append(int(value[0]))
        values.append(int(value[1]))
    else:
        # Append None values if the string is invalid
        values.append(None)
        values.append(None)
    return values


def convert_coordinates_to_numpy(coordinates_matlab):
    """
    Converts a 2D MATLAB array of coordinates into a 3D NumPy array.

    The function reshapes the original MATLAB array, transposes it to match NumPy's indexing order,
    and returns the transformed array.

    Parameters
    ----------
    coordinates_matlab : np.array
        The 2D MATLAB array to be converted. It should be of shape (w, h) where w and h represent width and height respectively.

    Returns
    -------
    coordinates_numpy : np.array
        The converted 3D NumPy array. It is of shape (2, w, h) where 2 represents the x and y coordinates.

    Notes
    -----
    This function is specifically designed to work with a 2D array of coordinates from MATLAB. The input is assumed
    to have a specific structure (array of arrays of coordinates). Deviations from this structure may result in unexpected outcomes.
    """
    # Calculate the dimensions based on the input
    w, h = coordinates_matlab.shape

    # Convert the array of arrays to a 3D numpy array
    coordinates_numpy = np.array(
        [coordinate for row in coordinates_matlab for coordinate in row]
    )

    # Reshape the 3D array to the original shape (w, h, 2)
    coordinates_numpy = coordinates_numpy.reshape(w, h, 2)

    # Transpose the axes to get the desired shape (2, w, h)
    coordinates_numpy = np.transpose(coordinates_numpy, (2, 0, 1))

    return coordinates_numpy


def format_coordinates_values(coordinates):
    """
    Extract the coordinates where all values are zero.

    Parameters
    ----------
    coordinates : numpy.ndarray
        The array containing coordinate information.

    Returns
    -------
    list
        A list of two integers representing the coordinates where all values are zero.

    Notes
    -----
    This function assumes that the array is transformed into a NumPy array before being passed in.
    """
    values = []
    # Convert coordinates to NumPy array
    coordinates = convert_coordinates_to_numpy(coordinates)

    # Find the indices where all elements along the axis are zero
    indices = np.all(coordinates == 0, axis=0)
    y, x = np.where(indices)

    values.append(int(x[0]))
    values.append(int(y[0]))
    return values


def format_frame_array_values(frame_array):
    """
    Format a frame array based on its dimensionality.

    Parameters
    ----------
    frame_array : numpy.ndarray
        The array containing frames.

    Returns
    -------
    list
        A list containing the formatted frame array.
    """
    values = []
    if frame_array.ndim == 1:
        values.append(list(frame_array))
    else:
        values.append([list(frames) for frames in frame_array])
    return values


def format_time_array_values(time_array):
    """
    Format a time array into a list of string pairs.

    Parameters
    ----------
    time_array : numpy.ndarray
        The array containing time values.

    Returns
    -------
    list
        A list containing pairs of strings representing time values.
    """
    values = []
    time_list = [[str(time_arr[0]), str(time_arr[1])] for time_arr in time_array]
    values.append(time_list)
    return values


def format_values(key, value):
    """
    Format values based on their key.

    Parameters
    ----------
    key : str
        The key representing the type of value.
    value : various
        The value to be formatted.

    Returns
    -------
    list
        A list containing the formatted value(s).

    Notes
    -----
    This function acts as a dispatcher that calls the appropriate function to format the value based on its key.
    """
    if key == "xyStart":
        return format_xyStart_values(value)
    elif key == "Coordinates":
        return format_coordinates_values(value)
    elif key == "FrameArray":
        return format_frame_array_values(value)
    elif key == "TimeArray":
        return format_time_array_values(value)
    else:
        return [value]


def field_formatted(key: str, value):
    """
    Homogenizes variable annotations according to a predefined list.

    The function converts a key-value pair into a homogenized list of tuples according to a hard-coded list of keys.
    This is useful in standardizing variables annotated in different ways.

    Parameters
    ----------
    key : str
        The key to be formatted.

    value : str
        The corresponding value to be formatted.

    Returns
    -------
    formatted_key_value : list
        A list of tuples where each tuple is a pair of formatted key-value.

    Notes
    -----
    The keys are formatted as follows: 'xyStart' into 'xStart' and 'yStart',
    'xywh' into 'xStart', 'yStart', 'boxWidth', and 'boxHeight',
    'Overlap' into 'Overlap', 'Coordinates' into 'grid_xStart' and 'grid_yStart',
    'FrameArray' and 'TimeArray' are retained as is, all others are added without formatting.

    This function is designed to work with a specific set of keys and may not work as expected with
    a different set of keys.
    """

    keys = MAPPING_KEY.get(key, [key])
    values = format_values(key, value)

    return list(zip(keys, values))


def extract_AOT_results_folder(
    group: zarr.hierarchy.Group, SAP_results_folder, quantities, verbose=True
):
    """
    Extracts information from .mat files in the AveragesOverTime (AOT) folder and stores them in a zarr group.

    This function iterates over all .mat files present in the AOT folder (excluding any file that contains "alltime"
    in its name), extracts the quantities of interest, and stores them in the zarr hierarchy.
    The function creates subgroups in the zarr group to match the file structure in the AOT folder.

    Parameters
    ----------
    group : zarr.hierarchy.Group
        The zarr group where the extracted datasets will be stored.
    SAP_results_folder : str
        The path to the SAP results folder.
    quantities : list
        The list of quantities to be extracted from the .mat files.
    verbose : bool, optional
        If True, the function will print warnings when a quantity is not found in the backup file.

    Raises
    ------
    IOError
        If there are more than one or no AOT folders in the SAP results folder.

    Returns
    -------
    None
        This function doesn't return anything. It modifies the provided zarr group in-place.

    """
    AOT_folder = find_AOT_folder(SAP_results_folder)
    traverse_and_extract_AOT(group, AOT_folder, quantities, verbose=True)


def find_AOT_folder(SAP_results_folder):
    """
    Find the AOT folder within the given SAP results directory.

    Parameters
    ----------
    SAP_results_folder : str
        The path to the SAP results directory.

    Returns
    -------
    str
        The path to the AOT folder within the SAP results directory.

    Raises
    ------
    IOError
        If there is more than one or no AOT folder detected.

    Notes
    -----
    The function expects a single AOT folder to exist within the SAP results folder.
    """
    path_AOT = os.path.join(SAP_results_folder, "AOT*")
    AOT_folder = glob.glob(path_AOT)

    if len(AOT_folder) > 1:
        raise IOError(
            f"There should only be an AOT folder in the analysis, right now you have {AOT_folder}"
        )

    if len(AOT_folder) == 0:
        raise IOError(f"There is not AOT folder detected in {path_AOT}")

    return AOT_folder[0]


def traverse_and_extract_AOT(group, AOT_folder, quantities, verbose=True):
    """
    Traverse the AOT folder and extract relevant AOT information into a Zarr group.

    Parameters
    ----------
    group : zarr.hierarchy.Group
        The Zarr group where the extracted AOT information will be stored.
    AOT_folder : str
        The path to the AOT folder containing MATLAB `.mat` files.
    quantities : list
        A list of quantities that need to be extracted from the AOT files.
    verbose : bool, optional
        Whether to display verbose messages. Default is True.

    Notes
    -----
    The function walks through the AOT folder to find relevant `.mat` files.
    """
    for root, _, files in os.walk(AOT_folder):
        for file in files:
            if file.endswith(".mat") and "alltime" not in file:
                fullpath = os.path.join(root, file)
                index = fullpath.find(AOT_folder)
                parts = fullpath[index + len(AOT_folder) + 1 :].split(os.path.sep)[:-1]

                group_tmp = group
                for part in parts:
                    if part not in group_tmp:
                        group_tmp = group_tmp.create_group(part)
                    else:
                        group_tmp = group_tmp[part]

                extract_AOT(
                    group_tmp, os.path.join(root, file), quantities, verbose=verbose
                )


def check_keys(matlab_dict):
    """
    Convert any mat_struct objects in a dictionary to standard Python dictionaries.

    Parameters
    ----------
    matlab_dict : dict
        A dictionary potentially containing mat_struct objects.

    Returns
    -------
    dict
        The updated dictionary with mat_struct objects converted to Python dictionaries.

    Notes
    -----
    This function is specific to handling MATLAB `.mat` files.
    """
    for key in matlab_dict:
        if isinstance(matlab_dict[key], spio.matlab.mio5_params.mat_struct):
            matlab_dict[key] = todict(matlab_dict[key])
    return matlab_dict


def todict(matobj):
    """
    Convert a mat_struct object to a Python dictionary.

    Parameters
    ----------
    matobj : spio.matlab.mio5_params.mat_struct
        The mat_struct object to be converted.

    Returns
    -------
    dict
        A Python dictionary representation of the mat_struct object.
    """
    python_dict = {}
    for field in matobj._fieldnames:
        elem = matobj.__dict__[field]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            python_dict[field] = todict(elem)
        else:
            python_dict[field] = elem
    return python_dict


def loadmat(filename):
    """
    Load a MATLAB `.mat` file and convert it to a Python dictionary.

    Parameters
    ----------
    filename : str
        The path to the `.mat` file.

    Returns
    -------
    dict
        A Python dictionary containing the data from the `.mat` file.
    """
    data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return check_keys(data)


def load_and_update_backup(path_AOT):
    """
    Load a backup MATLAB `.mat` file and update its structure.

    Parameters
    ----------
    path_AOT : str
        The path to the `.mat` file.

    Returns
    -------
    dict
        The updated backup dictionary.

    Notes
    -----
    If the key "REG" exists in the backup, its contents will be moved to the root level of the backup dictionary.
    """
    backup = loadmat(path_AOT)

    if "REG" in backup.keys():
        reg_dict = deepcopy(backup["REG"])
        del backup["REG"]
        backup.update(reg_dict)

    return backup


def update_zarr_group(group, quantity, value, group_name):
    """
    Update a Zarr group with a given quantity and value.

    Parameters
    ----------
    group : zarr.hierarchy.Group
        The Zarr group to be updated.
    quantity : str
        The quantity name that needs to be updated or added.
    value : various
        The value associated with the quantity.
    group_name : str
        The name of the group being updated.

    Notes
    -----
    1. If the quantity already exists in the group, no action is taken.
    2. The function supports specialized formatting for quantities listed in `QUANTITIES_ATTRIBUTES`.
    3. The values are either pickled or harmonized based on their nature.
    """
    # Check if quantity already exists in the group
    if quantity in group:
        return

    # Handle special quantities listed in QUANTITIES_ATTRIBUTES
    if quantity in QUANTITIES_ATTRIBUTES:
        results = field_formatted(quantity, value)
        for key, formatted_value in results:
            # Handle NumPy array by converting it to list
            if isinstance(formatted_value, np.ndarray):
                formatted_value = list(formatted_value)

            # Create a dataset if the key does not exist in the group
            if not key in group:
                ds = group.create_dataset(
                    key,
                    shape=(1,),
                    dtype=object,
                    object_codec=numcodecs.Pickle(),
                )
                ds[0] = formatted_value
            else:
                group[key][0] = formatted_value
    else:
        # Harmonize the shape of the value
        harmonized_value = harmonize_shape(
            value, quantity_name=quantity, group_name=group_name
        )
        group.create_dataset(quantity, data=harmonized_value, dtype=np.float16)


def extract_AOT(group, path_AOT, quantities, verbose=True):
    """
    Extracts given quantities from the backup file and stores them in a zarr group.

    This function reads quantities from a MATLAB backup file and stores each quantity either as
    a dataset or attribute in the provided zarr group. The storage method depends on the quantity itself.
    Some quantities are positioned differently depending on their name and some belong to attributes
    instead of arrays. Some of the axes are also moved to correct their positions.

    Parameters
    ----------
    group : zarr.hierarchy.Group
        The zarr group where the extracted datasets and attributes will be stored.
    path_AOT : str
        The path to the MATLAB backup file.
    quantities : list
        The list of quantities that are to be extracted from the backup file.
    verbose : bool, optional
        If True, the function will print warnings when a quantity is not found in the backup file.

    Returns
    -------
    None
        This function doesn't return anything. It modifies the provided zarr group in-place.

    """
    group_name = os.path.basename(group.name)
    backup = load_and_update_backup(path_AOT)

    for quantity in quantities:
        if quantity not in backup.keys() and verbose:
            print(quantity, backup.keys())
            warnings.warn(f"{quantity} not found in {path_AOT}")
        elif quantity in backup.keys():
            update_zarr_group(group, quantity, backup[quantity], group_name)
        # update_zarr_group(group, quantity, backup[quantity], group_name)


def harmonize_shape(quantity_value, quantity_name=None, group_name=""):
    """
    Reformat the array shapes such that time is in the first dimension.

    This function is used to standardize the dimensions of input arrays for further processing or analysis.
    The time dimension (t) is moved to the first position, if it exists and is not already there.

    Parameters
    ----------
    quantity_value : np.ndarray
        The input array whose dimensions need to be reformatted.
    quantity_name : str, optional
        Name of the quantity represented by the array. This is used in error messages.

    Returns
    -------
    np.ndarray
        The reformatted array with the time dimension moved to the first position, if applicable.

    Raises
    ------
    ValueError
        If the input array has less than two dimensions.

    """

    if quantity_value.ndim < 2:
        raise ValueError(f"There should be at least two dimensions in {quantity_name}")

    conditions = [
        (lambda: quantity_value.ndim == 2, lambda: quantity_value),
        (
            lambda: quantity_value.ndim == 3
            and "DBA" in group_name
            and quantity_name not in ["EpsilonPIV", "UPIV"],
            lambda: np.moveaxis(quantity_value, 2, 0),
        ),
        (
            lambda: quantity_value.ndim == 3 and "AOA" in group_name,
            lambda: quantity_value,
        ),
        (lambda: quantity_value.ndim == 3, lambda: np.moveaxis(quantity_value, 2, 0)),
        (
            lambda: quantity_value.ndim == 4 and "DBA" in group_name,
            lambda: np.moveaxis(quantity_value, 3, 0),
        ),
        (
            lambda: quantity_value.ndim == 4
            and "AOA" in group_name
            and quantity_name in ["EpsilonPIV", "UPIV"],
            lambda: quantity_value,
        ),
        (
            lambda: quantity_value.ndim == 4
            and "AOA" in group_name
            and quantity_name in ["OmegaPIV", "AreaRatios"],
            lambda: np.moveaxis(quantity_value, 2, 0),
        ),
        (
            lambda: quantity_value.ndim == 4 and "AOA" in group_name,
            lambda: np.moveaxis(quantity_value, 3, 0),
        ),
        (
            lambda: quantity_value.ndim == 4
            and quantity_name in ["EpsilonPIV", "UPIV"],
            lambda: np.moveaxis(quantity_value, 3, 0),
        ),
        (
            lambda: quantity_value.ndim == 4
            and quantity_name in ["OmegaPIV", "AreaRatios", "AreaRatios_VM"],
            lambda: np.moveaxis(quantity_value, 2, 0),
        ),
        (lambda: quantity_value.ndim == 4, lambda: np.moveaxis(quantity_value, 3, 0)),
        (lambda: quantity_value.ndim > 4, lambda: np.moveaxis(quantity_value, 3, 0)),
    ]

    for condition, action in conditions:
        if condition():
            return action()

    return quantity_value  # Default return value in case no condition is met


def zarr_cellpose(project_folder, data_folder, output_folder):
    zarr_path = Path(output_folder)
    input_dir = Path(project_folder)
    raw_image_path = input_dir

    seg_dir = Path(f"SEG_{str(data_folder)}")
    sap_folder = input_dir / f"SAP_{str(data_folder)}/"

    output_dir = input_dir / seg_dir
    output_dir = input_dir / seg_dir
    masks_path = output_dir / Path(f"roi_{str(data_folder)}")
    outlines_path = output_dir / Path(f"results_{str(data_folder)}")
    store_data_in_zarr(zarr_path, raw_image_path, outlines_path, masks_path, sap_folder)
    quantities = [
        "EpsilonPIV",
        "OmegaPIV",
        "UPIV",
        "xywh",
        "Overlap",
        "Coordinates",
        "TimeArray",
        "FrameArray",
    ]

    animal = zarr.open(zarr_path, "a")

    extract_AOT_results_folder(
        animal.TENSORS,
        sap_folder,
        quantities=quantities,
        verbose=True,
    )


def run_zarrification(project_folder, output_folder=None):
    project_folder = Path(project_folder)
    data_folder = project_folder.name
    if output_folder is None:
        output_folder = project_folder
        output_folder = output_folder  # / data_folder
    output_folder = Path(output_folder)

    zarr_cellpose(project_folder, data_folder, output_folder)


if __name__ == "__main__":
    run_zarrification(
        "/Volumes/u934/equipe_bellaiche/m_ech-chouini/fb_analysis/substraction-RNAi_selection/wRNAi_8"
    )
    # animal = zarr.open(
    #     "/Volumes/u934/equipe_bellaiche/m_ech-chouini/test_zar/wRNAi_12", "a"
    # )

    # SAP_data_folder = "/Volumes/u934/equipe_bellaiche/m_ech-chouini/test_zar/wRNAi_12/"
    # name_analysis = "wRNAi_12"
    # verbose = 1
    # groups = ["METADATA", "TENSORS", "IMAGE", "TRACKING"]
    # for group in groups:
    #     if group in animal:
    #         continue
    #     animal.create_groups(group)

    # # Adding the 'quantities'
    # quantities = [
    #     "EpsilonPIV",
    #     "OmegaPIV",
    #     "UPIV",
    #     "xywh",
    #     "Overlap",
    #     "Coordinates",
    #     "TimeArray",
    #     "FrameArray",
    # ]
    # extract_AOT_results_folder(
    #     animal.TENSORS,
    #     os.path.join(SAP_data_folder, f"SAP_{name_analysis}"),
    #     quantities=quantities,
    #     verbose=True,
    # )
