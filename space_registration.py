from pathlib import Path
import napari
from roi_manager import RoiManager
import zarr


def attributes_to_text_file(animal, path_animal: Path, animal_name: str):
    attributes = ["Macro_XYs", "MidLine_XYs", "Neck_XYs"]

    # Create the target directory if it doesn't exist
    target_dir = path_animal / f"SAP_{animal_name}" / f"spaceReg_{animal_name}_999"
    target_dir.mkdir(parents=True, exist_ok=True)

    for attribute in attributes:
        # Fetch the attribute data
        attribute_data = animal.attrs[attribute]

        # File name and path
        file_name = f"{attribute}_{animal_name}.txt"
        file_path = target_dir / file_name

        # Convert the 2D list to a string with tab-separated values and newlines
        attribute_str = "\n".join(["\t".join(map(str, row)) for row in attribute_data])

        # Write to file
        with open(file_path, "w") as f:
            f.write(attribute_str)


def main():
    """
    Main function to initialize the napari viewer and ROI manager.
    """
    path_animal = Path("/Volumes/u934/equipe_bellaiche/m_ech-chouini/test_zar/wRNAi_6")
    animal_name = "wRNAi_6"
    animal = zarr.open(path_animal, "a")
    image = animal.IMAGE.raw

    viewer = napari.Viewer()
    image_layer = viewer.add_image(image)

    roi_manager = RoiManager(viewer, animal)

    napari.run()
    attributes_to_text_file(animal, path_animal, animal_name)


if __name__ == "__main__":
    main()
