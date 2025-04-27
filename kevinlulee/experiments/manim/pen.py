from manimlib import *
import numpy as np

class GridPen(VMobject):
    def __init__(self, start_point=ORIGIN, **kwargs):
        super().__init__(**kwargs)
        self.cursor = np.array([start_point[0], start_point[1], 0])
        self.elements = []
        self.row_heights = {}  # Maps row index to height
        self.current_row = 0

    def draw(self, mobject, move_cursor=True):
        """Draw a mobject at the current cursor position and track it."""
        # Position the mobject so its top-left corner is at the cursor
        mobject.move_to(self.cursor + mobject.get_top_left() * -1)

        # Add the mobject to our elements list and add it as a submobject
        self.elements.append(mobject)
        self.add(mobject)

        # Update row height if necessary
        if self.current_row not in self.row_heights:
            self.row_heights[self.current_row] = 0

        current_height = mobject.get_height()
        if current_height > self.row_heights[self.current_row]:
            self.row_heights[self.current_row] = current_height

        # Move cursor if requested
        if move_cursor:
            self.cursor[0] += mobject.get_width()

        return self

    def newline(self):
        """Move to the next line based on the height of the current row."""
        if self.elements:
            first_element_in_row = next((
                elem for elem in self.elements
                if np.isclose(elem.get_top()[1], max(e.get_top()[1] for e in self.get_row(self.current_row)))
            ), None)
            self.cursor[0] = first_element_in_row.get_left()[0] if first_element_in_row else 0
        else:
            self.cursor[0] = 0

        current_row_height = self.row_heights.get(self.current_row, 0)
        self.cursor[1] -= current_row_height
        self.current_row += 1
        return self

    def select(self, *args, **kwargs):
        """Select elements based on index or edge vector."""
        if 'index' in kwargs:
            indices = kwargs['index']
            if isinstance(indices, int):
                indices = [indices]
            return [self.elements[i] for i in indices if 0 <= i < len(self.elements)]

        elif 'edge' in kwargs:
            edge_vector = np.array(kwargs['edge'])
            bounding_box = self.get_bounding_box()
            selected = []

            for element in self.elements:
                element_point = element.get_boundary_point(edge_vector)
                box_point = self.get_boundary_point(edge_vector)
                if np.allclose(element_point, box_point):
                    selected.append(element)

            return selected

        return []

    def get_bounding_box(self):
        """Return the bounding box of all elements."""
        return super().get_bounding_box()

    @property
    def columns(self):
        """Return elements grouped by x-coordinate, ordered from left to right."""
        if not self.elements:
            return []

        x_coordinates = {}
        for element in self.elements:
            left_edge = element.get_left()[0]
            if not any(np.isclose(left_edge, x) for x in x_coordinates):
                x_coordinates[left_edge] = []
            for x in x_coordinates:
                if np.isclose(left_edge, x):
                    x_coordinates[x].append(element)
                    break
        return [x_coordinates[x] for x in sorted(x_coordinates.keys())]

    @property
    def rows(self):
        """Return elements grouped by y-coordinate (row), ordered from top to bottom."""
        if not self.elements:
            return []

        y_coordinates = {}
        for element in self.elements:
            top_edge = element.get_top()[1]
            if not any(np.isclose(top_edge, y) for y in y_coordinates):
                y_coordinates[top_edge] = []
            for y in y_coordinates:
                if np.isclose(top_edge, y):
                    y_coordinates[y].append(element)
                    break
        return [y_coordinates[y] for y in sorted(y_coordinates.keys(), reverse=True)]

    def get_row(self, row_index):
        """Get elements of a specific row (based on the order they were added via newline)."""
        row_start_index = sum(len(r) for i, r in self.rows_dict.items() if i < row_index)
        if row_index in self.rows_dict:
            return self.rows_dict[row_index]
        return []

    @property
    def rows_dict(self):
        """Return a dictionary mapping row index to a list of elements in that row."""
        rows = {}
        current_y = None
        current_row_index = 0
        for element in sorted(self.elements, key=lambda m: m.get_y(UP), reverse=True):
            top_y = element.get_top()[1]
            if current_y is None or not np.isclose(top_y, current_y, atol=1e-2):
                current_y = top_y
                current_row_index += 1
                rows[current_row_index - 1] = []
            rows[current_row_index - 1].append(element)
        return rows
