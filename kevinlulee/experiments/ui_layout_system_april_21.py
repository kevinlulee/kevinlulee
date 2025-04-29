
# core/geometry.py


class Size:
    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height
        
    def __repr__(self):
        return f"Size({self.width}, {self.height})"




# core/constraints.py
class Anchor:
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    CENTER_X = "center_x"
    CENTER_Y = "center_y"
    WIDTH = "width"
    HEIGHT = "height"
    
    def __init__(self, type, value=None, target_element=None, target_anchor=None):
        self.type = type
        self.value = value
        self.target_element = target_element
        self.target_anchor = target_anchor
        
    def __repr__(self):
        if self.target_element:
            return f"Anchor({self.type}, target={self.target_element.id}.{self.target_anchor})"
        return f"Anchor({self.type}, value={self.value})"


class Constraint:
    def __init__(self, source_element, source_anchor, target_element=None, 
                 target_anchor=None, constant=0):
        self.source_element = source_element
        self.source_anchor = source_anchor
        self.target_element = target_element
        self.target_anchor = target_anchor
        self.constant = constant
        
    def resolve(self):
        if self.target_element is None:
            # Absolute constraint
            return self.constant
            
        # Get target value
        target_value = 0
        if self.target_anchor == Anchor.LEFT:
            target_value = self.target_element.frame.left
        elif self.target_anchor == Anchor.RIGHT:
            target_value = self.target_element.frame.right
        elif self.target_anchor == Anchor.TOP:
            target_value = self.target_element.frame.top
        elif self.target_anchor == Anchor.BOTTOM:
            target_value = self.target_element.frame.bottom
        elif self.target_anchor == Anchor.CENTER_X:
            target_value = self.target_element.frame.center.x
        elif self.target_anchor == Anchor.CENTER_Y:
            target_value = self.target_element.frame.center.y
        elif self.target_anchor == Anchor.WIDTH:
            target_value = self.target_element.frame.width
        elif self.target_anchor == Anchor.HEIGHT:
            target_value = self.target_element.frame.height
            
        return target_value + self.constant
        
    def __repr__(self):
        if self.target_element:
            return f"Constraint({self.source_element.id}.{self.source_anchor} -> {self.target_element.id}.{self.target_anchor} + {self.constant})"
        return f"Constraint({self.source_element.id}.{self.source_anchor} = {self.constant})"


# core/element.py
class Element:
    _id_counter = 0
    
    @classmethod
    def _generate_id(cls):
        cls._id_counter += 1
        return cls._id_counter
        
    def __init__(self, id=None, frame=None):
        self.id = id if id else f"element_{Element._generate_id()}"
        self.frame = frame if frame else Rect()
        self.constraints = {}
        self.is_visible = True
        self.parent = None
        
    def add_constraint(self, source_anchor, target_element=None, target_anchor=None, constant=0):
        constraint = Constraint(self, source_anchor, target_element, target_anchor, constant)
        self.constraints[source_anchor] = constraint
        return constraint
        
    def set_position(self, x, y):
        self.frame.origin = Point(x, y)
        
    def set_size(self, width, height):
        self.frame.size = Size(width, height)
        
    def apply_constraints(self):
        # Apply horizontal constraints
        if Anchor.LEFT in self.constraints:
            self.frame.origin.x = self.constraints[Anchor.LEFT].resolve()
        elif Anchor.CENTER_X in self.constraints:
            center_x = self.constraints[Anchor.CENTER_X].resolve()
            self.frame.origin.x = center_x - self.frame.width / 2
        elif Anchor.RIGHT in self.constraints:
            right = self.constraints[Anchor.RIGHT].resolve()
            self.frame.origin.x = right - self.frame.width
            
        # Apply vertical constraints
        if Anchor.TOP in self.constraints:
            self.frame.origin.y = self.constraints[Anchor.TOP].resolve()
        elif Anchor.CENTER_Y in self.constraints:
            center_y = self.constraints[Anchor.CENTER_Y].resolve()
            self.frame.origin.y = center_y - self.frame.height / 2
        elif Anchor.BOTTOM in self.constraints:
            bottom = self.constraints[Anchor.BOTTOM].resolve()
            self.frame.origin.y = bottom - self.frame.height
            
        # Apply size constraints
        if Anchor.WIDTH in self.constraints:
            self.frame.size.width = self.constraints[Anchor.WIDTH].resolve()
        if Anchor.HEIGHT in self.constraints:
            self.frame.size.height = self.constraints[Anchor.HEIGHT].resolve()
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, frame={self.frame})"


# core/container.py
class Container(Element):
    def __init__(self, id=None, frame=None):
        super().__init__(id, frame)
        self.children = []
        
    def add_child(self, element):
        if element.parent:
            element.parent.remove_child(element)
        
        self.children.append(element)
        element.parent = self
        return element
        
    def remove_child(self, element):
        if element in self.children:
            self.children.remove(element)
            element.parent = None
            
    def find_element_by_id(self, id):
        if self.id == id:
            return self
            
        for child in self.children:
            if child.id == id:
                return child
            
            if isinstance(child, Container):
                element = child.find_element_by_id(id)
                if element:
                    return element
                    
        return None
        
    def apply_constraints(self):
        super().apply_constraints()
        
        for child in self.children:
            child.apply_constraints()


# layout/engine.py
class LayoutEngine:
    def __init__(self, root_container):
        self.root_container = root_container
        
    def layout(self):
        # Clear all frames
        self._reset_frames(self.root_container)
        
        # Apply layout strategy to each container
        self._layout_container(self.root_container)
        
        # Apply constraints
        self.root_container.apply_constraints()
        
    def _reset_frames(self, container):
        for child in container.children:
            if isinstance(child, Container):
                self._reset_frames(child)
                
    def _layout_container(self, container):
        # Call specific layout method based on container type
        if hasattr(container, "perform_layout"):
            container.perform_layout()
            
        # Recursively layout children that are containers
        for child in container.children:
            if isinstance(child, Container):
                self._layout_container(child)


# layout/flow.py
class Direction:
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class FlowContainer(Container):
    def __init__(self, id=None, frame=None, direction=Direction.VERTICAL, spacing=0):
        super().__init__(id, frame)
        self.direction = direction
        self.spacing = spacing
        
    def perform_layout(self):
        if not self.children:
            return
            
        current_x = 0
        current_y = 0
        
        for i, child in enumerate(self.children):
            # Add spacing except for first element
            if i > 0:
                if self.direction == Direction.HORIZONTAL:
                    current_x += self.spacing
                else:
                    current_y += self.spacing
            
            # Position the child
            child.set_position(current_x, current_y)
            
            # Update current position for next child
            if self.direction == Direction.HORIZONTAL:
                current_x += child.frame.width
            else:
                current_y += child.frame.height
                
        # Update container size based on children
        if self.direction == Direction.HORIZONTAL:
            width = current_x
            height = max([child.frame.height for child in self.children]) if self.children else 0
        else:  # VERTICAL
            width = max([child.frame.width for child in self.children]) if self.children else 0
            height = current_y
            
        self.set_size(width, height)


# layout/absolute.py
class AbsoluteContainer(Container):
    def __init__(self, id=None, frame=None):
        super().__init__(id, frame)
        
    def perform_layout(self):
        # No automatic layout - all elements are positioned using constraints
        # or by manually setting their position
        pass


# layout/anchor.py
class AnchorContainer(Container):
    def __init__(self, id=None, frame=None):
        super().__init__(id, frame)
        
    def perform_layout(self):
        # Rely on the constraint system for layout
        pass
        
    def anchor_child_to_parent(self, child, edge_pairs, padding=0):
        """
        Helper method to anchor a child's edges to parent's edges
        edge_pairs: list of tuples (child_anchor, parent_anchor)
        """
        for child_anchor, parent_anchor in edge_pairs:
            child.add_constraint(child_anchor, self, parent_anchor, padding)
            
    def center_child(self, child):
        """Helper method to center a child in parent"""
        child.add_constraint(Anchor.CENTER_X, self, Anchor.CENTER_X)
        child.add_constraint(Anchor.CENTER_Y, self, Anchor.CENTER_Y)
# Adding modern layout systems to our UI library

# First, let's create a more modern grid-based layout system

# layout/grid.py
class GridContainer(Container):
    def __init__(self, id=None, frame=None, columns=12, row_height=None, column_gap=10, row_gap=10):
        super().__init__(id, frame)
        self.columns = columns
        self.row_height = row_height  # If None, calculated based on content
        self.column_gap = column_gap
        self.row_gap = row_gap
        self.grid_items = {}  # Maps child elements to their grid positions
        
    def add_child(self, element, column=0, row=0, column_span=1, row_span=1):
        """Add a child with specific grid position"""
        super().add_child(element)
        self.grid_items[element] = {
            'column': column,
            'row': row,
            'column_span': column_span,
            'row_span': row_span
        }
        return element
        
    def perform_layout(self):
        if not self.children:
            return
            
        # Calculate column width
        available_width = self.frame.width - ((self.columns - 1) * self.column_gap)
        column_width = available_width / self.columns
        
        # Find max row if row_height is None
        max_row = 0
        for element, pos in self.grid_items.items():
            row_end = pos['row'] + pos['row_span']
            max_row = max(max_row, row_end)
            
        # Set positions of all children
        for element, pos in self.grid_items.items():
            col, row = pos['column'], pos['row']
            col_span, row_span = pos['column_span'], pos['row_span']
            
            # Calculate element size
            element_width = (column_width * col_span) + (self.column_gap * (col_span - 1))
            
            if self.row_height:
                element_height = (self.row_height * row_span) + (self.row_gap * (row_span - 1))
            else:
                # Use element's intrinsic height
                element_height = element.frame.height
                
            # Calculate position
            x = (col * column_width) + (col * self.column_gap)
            y = (row * (self.row_height or element_height)) + (row * self.row_gap)
            
            # Set element size and position
            element.set_size(element_width, element_height)
            element.set_position(x, y)
            
        # Update container height if needed
        if self.row_height is None:
            total_height = 0
            for row in range(max_row):
                # Find tallest element in each row
                row_elements = [e for e, pos in self.grid_items.items() 
                               if pos['row'] <= row < pos['row'] + pos['row_span']]
                if row_elements:
                    row_height = max([e.frame.height for e in row_elements])
                    total_height += row_height + (self.row_gap if row < max_row - 1 else 0)
            self.frame.size.height = total_height


# layout/flex.py
class FlexContainer(Container):
    """Flexbox-like container implementation"""
    
    # Flex direction constants
    DIRECTION_ROW = "row"
    DIRECTION_COLUMN = "column"
    
    # Alignment constants
    ALIGN_START = "start"
    ALIGN_CENTER = "center"
    ALIGN_END = "end"
    ALIGN_STRETCH = "stretch"
    ALIGN_SPACE_BETWEEN = "space-between"
    ALIGN_SPACE_AROUND = "space-around"
    ALIGN_SPACE_EVENLY = "space-evenly"
    
    def __init__(self, id=None, frame=None, direction=DIRECTION_ROW, 
                 justify_content=ALIGN_START, align_items=ALIGN_START,
                 gap=0, wrap=False):
        super().__init__(id, frame)
        self.direction = direction
        self.justify_content = justify_content
        self.align_items = align_items
        self.gap = gap
        self.wrap = wrap
        self.flex_items = {}  # Maps child elements to their flex properties
        
    def add_child(self, element, flex_grow=0, flex_shrink=1, flex_basis=None, align_self=None):
        """Add a child with specific flex properties"""
        super().add_child(element)
        self.flex_items[element] = {
            'flex_grow': flex_grow,
            'flex_shrink': flex_shrink,
            'flex_basis': flex_basis,
            'align_self': align_self
        }
        return element
        
    def perform_layout(self):
        if not self.children:
            return
            
        is_row = self.direction == self.DIRECTION_ROW
        main_size = self.frame.width if is_row else self.frame.height
        cross_size = self.frame.height if is_row else self.frame.width
        
        # First pass: calculate sizes and total flex grow
        total_flex_grow = 0
        total_main_size_used = 0
        flexing_items = []
        
        for child in self.children:
            flex_props = self.flex_items.get(child, {})
            flex_grow = flex_props.get('flex_grow', 0)
            flex_basis = flex_props.get('flex_basis')
            
            if flex_basis is not None:
                main_size_used = flex_basis
            else:
                main_size_used = child.frame.width if is_row else child.frame.height
                
            # Track items that can grow
            if flex_grow > 0:
                flexing_items.append(child)
                total_flex_grow += flex_grow
            
            total_main_size_used += main_size_used
            
        # Add gap to total space used
        if len(self.children) > 1:
            total_main_size_used += self.gap * (len(self.children) - 1)
            
        # Second pass: distribute remaining space according to flex grow
        remaining_space = max(0, main_size - total_main_size_used)
        
        if total_flex_grow > 0 and remaining_space > 0:
            unit = remaining_space / total_flex_grow
            
            for child in flexing_items:
                flex_grow = self.flex_items[child].get('flex_grow', 0)
                extra_size = flex_grow * unit
                
                if is_row:
                    child.frame.size.width += extra_size
                else:
                    child.frame.size.height += extra_size
        
        # Third pass: position items
        main_pos = 0
        
        # Calculate positions based on justify content
        if self.justify_content in [self.ALIGN_CENTER, self.ALIGN_END, 
                                   self.ALIGN_SPACE_BETWEEN, self.ALIGN_SPACE_AROUND, 
                                   self.ALIGN_SPACE_EVENLY]:
            # Calculate total size after flex distribution
            total_size = sum([child.frame.width if is_row else child.frame.height 
                             for child in self.children])
            
            # Add gaps
            if len(self.children) > 1:
                total_size += self.gap * (len(self.children) - 1)
                
            if self.justify_content == self.ALIGN_END:
                main_pos = main_size - total_size
            elif self.justify_content == self.ALIGN_CENTER:
                main_pos = (main_size - total_size) / 2
            elif self.justify_content == self.ALIGN_SPACE_BETWEEN and len(self.children) > 1:
                extra_space = main_size - total_size + (self.gap * (len(self.children) - 1))
                self.gap += extra_space / (len(self.children) - 1)
            elif self.justify_content == self.ALIGN_SPACE_AROUND and len(self.children) > 0:
                extra_space = main_size - total_size + (self.gap * (len(self.children) - 1))
                space_per_item = extra_space / len(self.children)
                main_pos = space_per_item / 2
                self.gap += space_per_item
            elif self.justify_content == self.ALIGN_SPACE_EVENLY and len(self.children) > 0:
                extra_space = main_size - total_size + (self.gap * (len(self.children) - 1))
                space_per_gap = extra_space / (len(self.children) + 1)
                main_pos = space_per_gap
                self.gap += space_per_gap
        
        # Position each child
        for i, child in enumerate(self.children):
            # Get item size
            main_item_size = child.frame.width if is_row else child.frame.height
            
            # Position in the cross axis (align-items)
            cross_pos = 0
            align = self.flex_items.get(child, {}).get('align_self') or self.align_items
            
            if align == self.ALIGN_CENTER:
                cross_pos = (cross_size - (child.frame.height if is_row else child.frame.width)) / 2
            elif align == self.ALIGN_END:
                cross_pos = cross_size - (child.frame.height if is_row else child.frame.width)
            elif align == self.ALIGN_STRETCH:
                if is_row:
                    child.frame.size.height = cross_size
                else:
                    child.frame.size.width = cross_size
                    
            # Set position
            if is_row:
                child.set_position(main_pos, cross_pos)
            else:
                child.set_position(cross_pos, main_pos)
                
            # Update main position for next item
            main_pos += main_item_size + self.gap


# Example: Building a UI with modern layout systems
def create_modern_ui():
    # Create main window
    window = AbsoluteContainer(id="window")
    window.set_size(800, 600)
    
    # Create a flexbox container for the overall layout
    main_layout = FlexContainer(id="main_layout", direction=FlexContainer.DIRECTION_COLUMN)
    window.add_child(main_layout)
    
    # Set main layout to fill the window
    main_layout.set_size(800, 600)
    
    # Create a header with flexbox
    header = FlexContainer(id="header", direction=FlexContainer.DIRECTION_ROW, 
                          justify_content=FlexContainer.ALIGN_SPACE_BETWEEN,
                          align_items=FlexContainer.ALIGN_CENTER)
    main_layout.add_child(header, flex_grow=0)  # Header doesn't grow
    header.set_size(800, 60)
    
    # Add logo to header
    logo = Element(id="logo")
    logo.set_size(100, 40)
    header.add_child(logo)
    return window
    
    # Add navigation menu to header
    nav = FlexContainer(id="nav", direction=FlexContainer.DIRECTION_ROW, 
                       justify_content=FlexContainer.ALIGN_END,
                       align_items=FlexContainer.ALIGN_CENTER,
                       gap=20)
    nav.set_size(400, 40)
    header.add_child(nav)
    
    # Add nav items
    for i in range(1):
        nav_item = Element(id=f"nav_item_{i}")
        nav_item.set_size(80, 30)
        nav.add_child(nav_item)
    
    # Create the main content area with flex
    content_area = FlexContainer(id="content_area", direction=FlexContainer.DIRECTION_ROW, gap=20)
    main_layout.add_child(content_area, flex_grow=1)  # Content area grows to fill space
    
    # Create a sidebar with flex column layout
    sidebar = FlexContainer(id="sidebar", direction=FlexContainer.DIRECTION_COLUMN, 
                           align_items=FlexContainer.ALIGN_STRETCH, gap=10)
    sidebar.set_size(200, 540)  # Height will be determined by flex
    content_area.add_child(sidebar, flex_grow=0, flex_shrink=0)  # Sidebar has fixed width
    
    # Add sidebar menu items
    for i in range(1):
        menu_item = Element(id=f"menu_item_{i}")
        menu_item.set_size(200, 40)
        sidebar.add_child(menu_item)
    
    # Create main content with grid layout
    main_content = GridContainer(id="main_content", columns=3, column_gap=20, row_gap=20)
    main_content.set_size(580, 540)  # Width and height will adjust with flex
    content_area.add_child(main_content, flex_grow=1)  # Main content grows to fill remaining space
    
    # Add cards to grid
    for i in range(6):
        col = i % 3
        row = i // 3
        card = Element(id=f"card_{i}")
        card.set_size(180, 200)  # Initial size, will be adjusted by grid
        main_content.add_child(card, column=col, row=row)
    
    # Add a footer with flex
    footer = FlexContainer(id="footer", direction=FlexContainer.DIRECTION_ROW,
                         justify_content=FlexContainer.ALIGN_SPACE_BETWEEN,
                         align_items=FlexContainer.ALIGN_CENTER)
    footer.set_size(800, 50)
    main_layout.add_child(footer, flex_grow=0)  # Footer doesn't grow
    
    # Add footer elements
    footer_left = Element(id="footer_left")
    footer_left.set_size(200, 30)
    footer.add_child(footer_left)
    
    footer_right = Element(id="footer_right")
    footer_right.set_size(200, 30)
    footer.add_child(footer_right)
    
    return window

def print_ui_structure(element, depth=0):
    indent = "  " * depth
    print(f"{indent}{element}")
    
    if isinstance(element, Container):
        for child in element.children:
            print_ui_structure(child, depth + 1)
# Example usage
def main():
    # Create the UI using modern layout systems
    window = create_modern_ui()
    
    # Run the layout engine
    engine = LayoutEngine(window)
    engine.layout()
    
    # Print and visualize the layout
    print_ui_structure(window)


Numbers = list[list[int]]
def grid(numbers: Numbers):
    g = Grid()
    for digits in numbers:
        g.add_row(digits)

    g.align(RIGHT)

    for col in g.columns:
        
if __name__ == "__main__":
    main()
