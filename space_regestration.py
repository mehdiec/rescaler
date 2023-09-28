import time
import napari
import numpy as np
import zarr
from qtpy.QtWidgets import QPushButton


class RoiManager:
    """
    Manages the Region of Interest (ROI) and line interactions in a napari viewer.

    Parameters
    ----------
    viewer : napari.Viewer
        The napari viewer.

    Attributes
    ----------
    viewer : napari.Viewer
        The napari viewer.
    animal : zarr
        The Zarr of the animal.
    clicked_coordinates : list of np.ndarray
        Coordinates where mouse was clicked for ROI.
    line_layer : napari.layers.Shapes
        Layer for drawing lines.
    line_click_count : int
        Number of times line layer was clicked.
    first_line_point : np.ndarray or None
        The starting coordinate of the line.
    line_in_progress : TODO: Type and description
        ...
    index : int
        The index for the ROI.
    layer_removed : bool
        Whether the ROI layer is removed.
    points_layer : napari.layers.Points
        Layer for ROI points.
    """

    def __init__(self, viewer, animal):
        self.viewer = viewer
        self.animal = animal

        self.clicked_coordinates = []
        self.line_layer = self.viewer.add_shapes(
            [], shape_type="line", edge_color="blue", edge_width=3
        )
        self.line_click_count = 0
        self.first_line_point = None
        self.line_in_progress = None

        self.viewer.mouse_drag_callbacks.append(self.get_click)

        self.index = 1
        self.layer_removed = False
        self.points_layer = self.viewer.add_points(
            name="ROIs", face_color="red", size=30
        )
        undo_button = QPushButton("Undo")
        undo_button.clicked.connect(self.on_undo)
        self.viewer.window.add_dock_widget(undo_button)

        skip_button = QPushButton("Skip")
        skip_button.clicked.connect(self.on_skip)
        self.viewer.window.add_dock_widget(skip_button)

        self.viewer.bind_key("z", self.on_undo)
        self.viewer.bind_key("q", self.on_skip)

        # TO DO undo button for
        # the line the neckline
        # get this into a file .txt for pipeline
        attributes = ["Macro_XYs", "MidLine_XYs", "Neck_XYs"]
        for attribute in attributes:
            if attribute in self.animal.attrs:
                print(f"Attribute {attribute} exists.")
            else:
                print(f"Attribute {attribute} does not exist. Creating it.")
                if attribute == "Macro_XYs":
                    self.animal.attrs[attribute] = [["NaN", "NaN"] for _ in range(8)]
                else:
                    self.animal.attrs[attribute] = [["NaN", "NaN"] for _ in range(2)]

    def on_save():
        pass

    def get_click(self, viewer, event) -> None:
        """
        Mouse click and drag event handler.

        Parameters
        ----------
        viewer : napari.Viewer
            The napari viewer.
        event : napari.utils.event.Event
            The event triggered.

        Yields
        ------
        None
        """
        print(f"Mouse down for {'line' if self.layer_removed else 'roi'}")
        dragged = False
        yield

        while event.type == "mouse_move":
            dragged = True
            yield

        if dragged:
            print(f"Drag end for {'line' if self.layer_removed else 'roi'}")
            return

        self.handle_click(event)

    def handle_click(self, event):
        """
        Handle click event to either draw a line or set an ROI point.

        Parameters
        ----------
        event : napari.utils.event.Event
            The event triggered.
        """
        print(f"Clicked for {'line' if self.layer_removed else 'roi'}!")
        coordinates = np.round(event.position).astype(int)[1:]

        if self.layer_removed:
            self.line_logic(coordinates)
            time.sleep(1)
            self.line_layer.visible = False
        else:
            self.roi_logic(coordinates)

    def line_logic(self, coordinates):
        """
        Logic for line drawing.

        Parameters
        ----------
        coordinates : np.ndarray
            The coordinates where the line should be drawn.
        """
        self.line_click_count += 1

        if self.line_click_count == 1:
            self.first_line_point = coordinates
        elif self.line_click_count == 2:
            self.draw_line(self.first_line_point, coordinates)
            self.line_coordinates = [self.first_line_point, coordinates]
            self.line_click_count = 0

    def draw_line(self, start_coord, end_coord):
        """
        Draw a line on the line layer.

        Parameters
        ----------
        start_coord : np.ndarray
            The starting coordinate of the line.
        end_coord : np.ndarray
            The ending coordinate of the line.
        """
        self.line_layer.add(np.array([start_coord, end_coord]), shape_type="line")

    def roi_logic(self, coordinates):
        """
        Logic for ROI point setting.

        Parameters
        ----------
        coordinates : np.ndarray
            The coordinates where the ROI point should be set.
        """
        coordinates = coordinates[np.newaxis, :]
        self.clicked_coordinates.append(coordinates)
        self.points_layer.add(coordinates)
        self.update_properties_and_index()

    def update_properties_and_index(self):
        """
        Update properties and index for the points layer.
        """
        properties = {"index": [self.index]}
        self.points_layer.text.refresh(properties)
        self.points_layer.text.visible = True
        self.points_layer.text.size = 20
        self.index += 1
        if self.index > 8:
            self.finalize_and_remove_layer()

    def finalize_and_remove_layer(self):
        """
        Finalize the ROI and remove the points layer.
        """
        self.layer_removed = True
        stored_coordinates = self.clicked_coordinates.copy()
        print(f"Coordinates stored: {stored_coordinates}")

        self.points_layer.visible = False

        print("Layer hidden.")

    def on_undo(self):
        """
        Undo the last action.
        """
        if (not self.line_layer.visible) & self.layer_removed:
            self.line_layer.visible = True
            self.line_layer.data = np.delete(self.line_layer.data, -1, axis=0)
            self.line_coordinates.clear()
            return

        if self.layer_removed:
            self.points_layer.visible = True
            self.layer_removed = False
        if self.layer_removed:
            self.points_layer.visible = True
            self.layer_removed = False

        if self.clicked_coordinates:
            self.points_layer.data = np.delete(self.points_layer.data, -1, axis=0)
            self.clicked_coordinates.pop()
            self.points_layer.text.refresh(self.points_layer.properties)
            self.index -= 1
            print("Last action undone.")

    def on_skip(self, viewer):
        """
        Skip the current ROI and finalize.

        Parameters
        ----------
        viewer : napari.Viewer
            The napari viewer.
        """
        print("Skipped.")
        self.finalize_and_remove_layer()


def main():
    """
    Main function to initialize the napari viewer and ROI manager.
    """
    animal = zarr.open(
        "/Volumes/u934/equipe_bellaiche/m_ech-chouini/test_zar/wRNAi_6", "a"
    )
    image = animal.IMAGE.raw

    viewer = napari.Viewer()
    image_layer = viewer.add_image(image)

    roi_manager = RoiManager(viewer, animal)

    napari.run()


if __name__ == "__main__":
    main()
