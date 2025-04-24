# Possible filename: pen_canvas.py

import math
from typing import List, Tuple, Dict, Any, Callable, Optional, Union
from enum import Enum

class Alignment(Enum):
    """Enumeration for alignment types."""
    LEFT = 'left'
    RIGHT = 'right'
    CENTER = 'center'
    TOP = 'top'
    BOTTOM = 'bottom'
    MIDDLE = 'middle' # Vertical center

class Element:
    """Represents a drawable object with value, width, and height."""
    def __init__(self, value: Any, width: Union[int, float], height: Union[int, float]):
        """
        Initializes an Element.

        Args:
            value: The content or identifier of the element.
            width: The width of the element.
            height: The height of the element.
        """
        if width < 0 or height < 0:
            raise ValueError("Element width and height must be non-negative")
        self.value = value
        self.width = width
        self.height = height

    def __repr__(self) -> str:
        return f"Element(value={repr(self.value)}, width={self.width}, height={self.height})"

    def get_bounds(self, pos: Tuple[Union[int, float], Union[int, float]]) -> Tuple[Union[int, float], Union[int, float], Union[int, float], Union[int, float]]:
        """
        Calculates the bounding box of the element at a given position.

        Args:
            pos: The (x, y) coordinate of the top-left corner of the element.

        Returns:
            A tuple representing the bounds: (x_min, y_min, x_max, y_max)
        """
        x_min, y_min = pos
        x_max = x_min + self.width
        y_max = y_min + self.height
        return x_min, y_min, x_max, y_max

class Pen:
    """
    A class simulating a drawing pen on a 2D canvas, placing elements
    and allowing queries and alignment.
    """
    StoredItem = Dict[str, Any] # Type alias for items in the store

    def __init__(self, start_x: Union[int, float] = 0, start_y: Union[int, float] = 0):
        """
        Initializes the Pen.

        Args:
            start_x: The initial x-coordinate. Defaults to 0.
            start_y: The initial y-coordinate. Defaults to 0.
        """
        self._x: Union[int, float] = start_x
        self._y: Union[int, float] = start_y
        self._initial_x: Union[int, float] = start_x
        self._initial_y: Union[int, float] = start_y
        self._store: List[Pen.StoredItem] = []
        # Track max dimensions reached for potential relative queries, though not fully implemented yet
        self._max_x: Union[int, float] = start_x
        self._max_y: Union[int, float] = start_y

    def ctx(self) -> Tuple[Union[int, float], Union[int, float]]:
        """
        Returns the current pen position (x, y).

        Returns:
            A tuple containing the current (x, y) coordinates.
        """
        return self._x, self._y

    def move_to(self, x: Union[int, float], y: Union[int, float]) -> None:
        """
        Moves the pen to an absolute position without drawing.

        Args:
            x: The target x-coordinate.
            y: The target y-coordinate.
        """
        self._x = x
        self._y = y

    def move_by(self, dx: Union[int, float], dy: Union[int, float]) -> None:
        """
        Moves the pen by a relative amount without drawing.

        Args:
            dx: The change in the x-coordinate.
            dy: The change in the y-coordinate.
        """
        self._x += dx
        self._y += dy

    def draw(self, element: Element, move_cursor: bool = True) -> StoredItem:
        """
        Draws an element at the current position and optionally updates the position.

        Args:
            element: The Element object to draw.
            move_cursor: If True (default), moves the pen cursor horizontally
                         by the width of the element after drawing.

        Returns:
            A dictionary representing the stored item (including position and element).
        """
        if not isinstance(element, Element):
            raise TypeError("draw() requires an Element object")

        current_pos = (self._x, self._y)
        stored_item: Pen.StoredItem = {'pos': current_pos, 'element': element}
        self._store.append(stored_item)

        # Update max dimensions reached
        self._max_x = max(self._max_x, self._x + element.width)
        self._max_y = max(self._max_y, self._y + element.height)

        if move_cursor:
            self.move_by(element.width, 0)

        return stored_item

    def _get_bounds(self) -> Tuple[Union[int, float], Union[int, float], Union[int, float], Union[int, float]]:
        """Calculates the bounding box of all drawn elements."""
        if not self._store:
            return self._initial_x, self._initial_y, self._initial_x, self._initial_y

        min_x = min(item['pos'][0] for item in self._store)
        min_y = min(item['pos'][1] for item in self._store)
        max_x = max(item['pos'][0] + item['element'].width for item in self._store)
        max_y = max(item['pos'][1] + item['element'].height for item in self._store)
        return min_x, min_y, max_x, max_y

    def _check_match(
        self,
        item: StoredItem,
        x: Optional[Union[int, float, Callable[[Union[int, float]], bool]]] = None,
        y: Optional[Union[int, float, Callable[[Union[int, float]], bool]]] = None,
        place: Optional[str] = None
    ) -> bool:
        """Helper function to check if a stored item matches query criteria."""
        pos_x, pos_y = item['pos']
        element = item['element']
        el_width = element.width
        el_height = element.height
        el_x_min, el_y_min, el_x_max, el_y_max = element.get_bounds(item['pos'])

        # --- Coordinate Matching (x) ---
        x_match = True
        if x is not None:
            if callable(x):
                x_match = x(pos_x)
            # Handling negative coordinates requires context (like overall bounds)
            # Simple interpretation: treat negative as direct coordinate for now.
            # A more complex interpretation (like 'from the right edge') is possible
            # but requires knowing the canvas/bounding box width.
            elif isinstance(x, (int, float)):
                 if x < 0:
                     # Example interpretation: match elements whose *right edge* is at canvas_width + x
                     # This requires knowing canvas bounds, which we don't strictly have.
                     # Let's defer complex negative handling or use a placeholder.
                     # Placeholder: Treat negative x as a direct coordinate match for now.
                     x_match = (pos_x == x)
                     # print(f"Warning: Negative x ({x}) query behavior is basic. Matching direct coordinate.")
                 else:
                     x_match = (pos_x == x)
            else:
                x_match = False # Invalid type for x

        if not x_match:
            return False

        # --- Coordinate Matching (y) ---
        y_match = True
        if y is not None:
            if callable(y):
                y_match = y(pos_y)
            elif isinstance(y, (int, float)):
                 if y < 0:
                     # Placeholder: Treat negative y as a direct coordinate match for now.
                     y_match = (pos_y == y)
                     # print(f"Warning: Negative y ({y}) query behavior is basic. Matching direct coordinate.")
                 else:
                     y_match = (pos_y == y)
            else:
                y_match = False # Invalid type for y

        if not y_match:
            return False

        # --- Place Matching ---
        # Needs context (overall bounds) for robust implementation (right, bottom, center)
        # Simple interpretation for now:
        place_match = True
        if place is not None:
            place_str = str(place).lower()
            min_bound_x, min_bound_y, max_bound_x, max_bound_y = self._get_bounds()

            if place_str == 'left':
                place_match = (el_x_min == min_bound_x)
            elif place_str == 'top':
                place_match = (el_y_min == min_bound_y)
            elif place_str == 'right':
                 # Requires knowing the overall max_x boundary accurately
                 place_match = (el_x_max == max_bound_x)
            elif place_str == 'bottom':
                 # Requires knowing the overall max_y boundary accurately
                 place_match = (el_y_max == max_bound_y)
            elif place_str == 'center':
                 # Requires knowing overall bounds accurately
                 canvas_center_x = min_bound_x + (max_bound_x - min_bound_x) / 2
                 element_center_x = el_x_min + el_width / 2
                 # Use math.isclose for float comparison
                 place_match = math.isclose(element_center_x, canvas_center_x)
            elif place_str == 'middle': # Vertical center
                 canvas_center_y = min_bound_y + (max_bound_y - min_bound_y) / 2
                 element_center_y = el_y_min + el_height / 2
                 place_match = math.isclose(element_center_y, canvas_center_y)
            else:
                # Unknown place value
                place_match = False
                # print(f"Warning: Unknown place value '{place}'. No match.")


        return place_match # Passed all checks

    def query_selector(
        self,
        x: Optional[Union[int, float, Callable[[Union[int, float]], bool]]] = None,
        y: Optional[Union[int, float, Callable[[Union[int, float]], bool]]] = None,
        place: Optional[str] = None
    ) -> Optional[StoredItem]:
        """
        Finds the first stored element matching the criteria.

        Args:
            x: Criteria for the x-coordinate. Can be a number (exact match),
               or a callable (function) that takes x-coordinate and returns bool.
               Negative numbers are currently treated as direct coordinates.
            y: Criteria for the y-coordinate. Can be a number (exact match),
               or a callable (function) that takes y-coordinate and returns bool.
               Negative numbers are currently treated as direct coordinates.
            place: A string indicating positional constraint ('left', 'right', 'top',
                   'bottom', 'center', 'middle'). Requires elements to be drawn
                   for context. 'right', 'bottom', 'center', 'middle' depend
                   on the calculated bounds of all elements.

        Returns:
            The first matching stored item (dictionary), or None if no match found.
        """
        for item in self._store:
            if self._check_match(item, x, y, place):
                return item
        return None

    def query_selector_all(
        self,
        x: Optional[Union[int, float, Callable[[Union[int, float]], bool]]] = None,
        y: Optional[Union[int, float, Callable[[Union[int, float]], bool]]] = None,
        place: Optional[str] = None
    ) -> List[StoredItem]:
        """
        Finds all stored elements matching the criteria.

        Args:
            x: Criteria for the x-coordinate. Can be a number (exact match),
               or a callable (function) that takes x-coordinate and returns bool.
               Negative numbers are currently treated as direct coordinates.
            y: Criteria for the y-coordinate. Can be a number (exact match),
               or a callable (function) that takes y-coordinate and returns bool.
               Negative numbers are currently treated as direct coordinates.
            place: A string indicating positional constraint ('left', 'right', 'top',
                   'bottom', 'center', 'middle'). Requires elements to be drawn
                   for context. 'right', 'bottom', 'center', 'middle' depend
                   on the calculated bounds of all elements.

        Returns:
            A list of all matching stored items (dictionaries). Empty if no matches.
        """
        matches = []
        for item in self._store:
            if self._check_match(item, x, y, place):
                matches.append(item)
        return matches

    def row(self, elements: List[Element], vertical_spacing: Union[int, float] = 0) -> List[StoredItem]:
        """
        Draws a list of elements horizontally in a row, starting at the current
        pen position. Updates the pen position to be below the drawn row.

        Args:
            elements: A list of Element objects to draw in the row.
            vertical_spacing: Additional vertical space to add after the row's height.

        Returns:
            A list of the stored item dictionaries created for this row.
        """
        if not elements:
            return []

        start_x = self._x
        start_y = self._y
        current_x = start_x
        max_row_height: Union[int, float] = 0
        row_items: List[Pen.StoredItem] = []

        for element in elements:
            if not isinstance(element, Element):
               raise TypeError("row() requires a list of Element objects")

            # Temporarily move pen to draw position for this element
            self.move_to(current_x, start_y)
            # Draw the element without moving the main cursor yet
            stored_item = self.draw(element, move_cursor=False)
            row_items.append(stored_item)

            # Update current_x for the next element in the row
            current_x += element.width
            # Track the maximum height in this row
            max_row_height = max(max_row_height, element.height)

        # After drawing all elements in the row, update the main pen position:
        # Reset x to the starting x of the row
        # Move y below the row just drawn
        self.move_to(start_x, start_y + max_row_height + vertical_spacing)

        return row_items

    def align(self, alignment: Alignment, item_groups: List[List[StoredItem]]) -> None:
        """
        Adjusts the positions of items within groups (like rows) to achieve
        the specified alignment. Modifies the 'pos' within the stored items directly.

        Args:
            alignment: The type of alignment (Alignment.LEFT, Alignment.RIGHT,
                       Alignment.CENTER, Alignment.TOP, Alignment.BOTTOM, Alignment.MIDDLE).
            item_groups: A list where each element is a list of stored items
                         (dictionaries returned by draw/row) that form a group
                         (e.g., a row) to be aligned relative to other groups.
        """
        if not item_groups:
            return

        group_bounds = []
        for group in item_groups:
            if not group:
                group_bounds.append({'min_x': 0, 'max_x': 0, 'min_y': 0, 'max_y': 0, 'width': 0, 'height': 0})
                continue

            min_x = min(item['pos'][0] for item in group)
            max_x = max(item['pos'][0] + item['element'].width for item in group)
            min_y = min(item['pos'][1] for item in group)
            max_y = max(item['pos'][1] + item['element'].height for item in group)
            group_bounds.append({
                'min_x': min_x, 'max_x': max_x, 'width': max_x - min_x,
                'min_y': min_y, 'max_y': max_y, 'height': max_y - min_y
            })

        if not group_bounds:
            return

        # --- Horizontal Alignment ---
        if alignment in [Alignment.LEFT, Alignment.RIGHT, Alignment.CENTER]:
            max_width = max(gb['width'] for gb in group_bounds)

            for i, group in enumerate(item_groups):
                if not group: continue
                bounds = group_bounds[i]
                current_width = bounds['width']
                start_x = bounds['min_x']
                offset_x: Union[int, float] = 0

                if alignment == Alignment.RIGHT:
                    offset_x = max_width - current_width
                elif alignment == Alignment.CENTER:
                    offset_x = (max_width - current_width) / 2
                elif alignment == Alignment.LEFT:
                    # Assuming alignment relative to the leftmost group start
                    # If all started at same x, offset is 0.
                    # If not, shift everything to align with the minimum start x found.
                    min_start_x_overall = min(gb['min_x'] for gb in group_bounds)
                    offset_x = min_start_x_overall - start_x # Negative if needs shifting left

                if not math.isclose(offset_x, 0):
                    for item in group:
                        # Modify the position tuple directly in the stored item
                        original_pos = item['pos']
                        item['pos'] = (original_pos[0] + offset_x, original_pos[1])

        # --- Vertical Alignment ---
        elif alignment in [Alignment.TOP, Alignment.BOTTOM, Alignment.MIDDLE]:
             max_height = max(gb['height'] for gb in group_bounds)

             for i, group in enumerate(item_groups):
                 if not group: continue
                 bounds = group_bounds[i]
                 current_height = bounds['height']
                 start_y = bounds['min_y']
                 offset_y: Union[int, float] = 0

                 if alignment == Alignment.BOTTOM:
                     offset_y = max_height - current_height
                 elif alignment == Alignment.MIDDLE:
                     offset_y = (max_height - current_height) / 2
                 elif alignment == Alignment.TOP:
                     min_start_y_overall = min(gb['min_y'] for gb in group_bounds)
                     offset_y = min_start_y_overall - start_y

                 if not math.isclose(offset_y, 0):
                     for item in group:
                         original_pos = item['pos']
                         item['pos'] = (original_pos[0], original_pos[1] + offset_y)

    def get_store(self) -> List[StoredItem]:
        """Returns a copy of the internal store of drawn items."""
        # Return a shallow copy to prevent external modification of the list structure itself
        return list(self._store)

    def __repr__(self) -> str:
        return f"Pen(pos={self.ctx()}, items={len(self._store)})"


# Example Usage:
if __name__ == "__main__":
    # pen = Pen()
    #
    # print("--- Basic Drawing ---")
    # objects_data = [
    #     {'value': 'cat', 'width': 3, 'height': 1},
    #     {'value': 'apple', 'width': 5, 'height': 1},
    #     {'value': 'dog', 'width': 3, 'height': 2},
    # ]
    #
    # elements = [Element(o['value'], width=o['width'], height=o['height']) for o in objects_data]
    #
    # print(f"Initial pos: {pen.ctx()}")
    # item1 = pen.draw(elements[0])
    # print(f"After drawing '{elements[0].value}': Pos={pen.ctx()}")
    # print(f"Stored item 1: {item1}")
    #
    # item2 = pen.draw(elements[1])
    # print(f"After drawing '{elements[1].value}': Pos={pen.ctx()}")
    # print(f"Stored item 2: {item2}")
    #
    # item3 = pen.draw(elements[2])
    # print(f"After drawing '{elements[2].value}': Pos={pen.ctx()}")
    # print(f"Stored item 3: {item3}")

    # print("\nCurrent Store:")
    # for item in pen.get_store():
    #     print(item)
    #
    # print("\n--- Querying ---")
    # query1 = pen.query_selector(x=0, y=0)
    # print(f"Query (x=0, y=0): {query1}")
    #
    # query2 = pen.query_selector(x=3) # Matches 'apple' starting pos
    # print(f"Query (x=3): {query2}")
    #
    # query3 = pen.query_selector_all(y=0) # Matches 'cat', 'apple', 'dog'
    # print(f"Query All (y=0): {query3}")
    #
    # query4 = pen.query_selector(lambda x: x > 5) # Matches 'dog' starting at x=8
    # print(f"Query (x > 5): {query4}")
    #
    # Example using place (basic implementation)
    # query5 = pen.query_selector(place='left') # Should match 'cat' at x=0
    # print(f"Query (place='left'): {query5}")
    #
    # # Query for element based on height
    # query6 = pen.query_selector_all(lambda x: True, lambda y: True) # Select all
    # elements_height_2 = [item for item in query6 if item['element'].height == 2]
    # print(f"Query All (element.height == 2): {elements_height_2}")
    #
    #
    print("\n--- Rows and Alignment ---")
    pen = Pen() # Reset pen

    row1_elements = [Element('A', 2, 1), Element('B', 3, 1)]
    row2_elements = [Element('X', 1, 1), Element('Y', 1, 1), Element('Z', 4, 1)]
    row3_elements = [Element('P', 5, 2)] # Different height

    print(f"Initial pos: {pen.ctx()}")
    row1_items = pen.row(row1_elements, vertical_spacing=0)
    print(f"After row 1: Pos={pen.ctx()}")

    row2_items = pen.row(row2_elements, vertical_spacing=0)
    print(f"After row 2: Pos={pen.ctx()}")
    row3_items = pen.row(row3_elements, vertical_spacing=0)
    print(f"After row 3: Pos={pen.ctx()}")

    print("\nStore before alignment:")
    for item in pen.get_store():
        print(item)

    rows_to_align = [row1_items, row2_items, row3_items]
    pen.align(Alignment.RIGHT, rows_to_align)

    print("\nStore after RIGHT alignment:")
    for item in pen.get_store():
        print(item)
    #
    # # Example: Reset and try center alignment
    # pen = Pen()
    # row1_items = pen.row(row1_elements, vertical_spacing=1)
    # row2_items = pen.row(row2_elements, vertical_spacing=1)
    # row3_items = pen.row(row3_elements, vertical_spacing=1)
    # rows_to_align = [row1_items, row2_items, row3_items]
    # print("\nStore before CENTER alignment:")
    # # print(pen.get_store()) # Already printed before previous alignment, positions are same initially
    # pen.align(Alignment.CENTER, rows_to_align)
    # print("\nStore after CENTER alignment:")
    # for item in pen.get_store():
    #     print(item)
    #
    # # Example: Vertical alignment (align centers of elements within a group - less common usage)
    # pen = Pen()
    # col1_elements = [Element('V1', 1, 1), Element('V2', 1, 3), Element('V3', 1, 2)]
    # col1_items = []
    # start_pos = pen.ctx()
    # current_y = start_pos[1]
    # max_h = 0
    # for el in col1_elements:
    #     pen.move_to(start_pos[0], current_y)
    #     col1_items.append(pen.draw(el, move_cursor=False))
    #     current_y += el.height
    #     max_h = max(max_h, el.height)
    # # Move cursor past the column
    # pen.move_to(start_pos[0] + 1, start_pos[1]) # Move right by 1
    #
    #
    # col2_elements = [Element('W1', 2, 4), Element('W2', 2, 1)]
    # col2_items = []
    # start_pos = pen.ctx()
    # current_y = start_pos[1]
    # max_h = 0
    # for el in col2_elements:
    #     pen.move_to(start_pos[0], current_y)
    #     col2_items.append(pen.draw(el, move_cursor=False))
    #     current_y += el.height
    #     max_h = max(max_h, el.height)
    # pen.move_to(start_pos[0] + 2, start_pos[1])
    #
    #
    # print("\nStore before TOP alignment (columns):")
    # for item in pen.get_store():
    #     print(item)
    #
    # # Align the tops of the columns
    # pen.align(Alignment.TOP, [col1_items, col2_items])
    #
    # print("\nStore after TOP alignment (columns):")
    # for item in pen.get_store():
    #     print(item)
