from __future__ import annotations
from typing import List, Self


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)


class Rect:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def left(self):
        return self.x

    @property
    def top(self):
        return self.y

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y + self.height

    @property
    def center(self):
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    def contains(self, x, y):
        return self.left <= x <= self.right and self.top <= y <= self.bottom

    def intersects(self, other):
        return not (
            self.right < other.left
            or self.left > other.right
            or self.bottom < other.top
            or self.top > other.bottom
        )

    def __repr__(self):
        return f"Rect({self.x}, {self.y}, {self.width}, {self.height})"


class Compass:
    def __init__(self, rect: Rect):
        self.rect = rect

    def get(self, angle, offset=0):
        angle = angle % 360

        # Calculate base position
        if angle == 0:  # East
            x = self.rect.right
            y = self.rect.center.y
        elif angle == 45:  # Northeast
            x = self.rect.right
            y = self.rect.top
        elif angle == 90:  # North
            x = self.rect.center.x
            y = self.rect.top
        elif angle == 135:  # Northwest
            x = self.rect.left
            y = self.rect.top
        elif angle == 180:  # West
            x = self.rect.left
            y = self.rect.center.x
        elif angle == 225:  # Southwest
            x = self.rect.left
            y = self.rect.bottom
        elif angle == 270:  # South
            x = self.rect.center.y
            y = self.rect.bottom
        elif angle == 315:  # Southeast
            x = self.rect.right
            y = self.rect.bottom
        else:
            # For angles in between, interpolate
            import math

            rad = math.radians(angle)
            # Start from center
            x = self.rect.center.x
            y = self.rect.center.y

            # Calculate direction vector
            dx = math.cos(rad)
            dy = -math.sin(rad)  # Negative because y increases downward

            # Calculate distance to edge of rectangle from center
            if abs(dx) > 1e-10:  # Avoid division by zero
                tx1 = (self.rect.left - x) / dx
                tx2 = (self.rect.right - x) / dx
                tx = max(tx1, tx2) if dx < 0 else min(tx1, tx2)
            else:
                tx = float("inf")

            if abs(dy) > 1e-10:  # Avoid division by zero
                ty1 = (self.rect.top - y) / dy
                ty2 = (self.rect.bottom - y) / dy
                ty = max(ty1, ty2) if dy < 0 else min(ty1, ty2)
            else:
                ty = float("inf")

            t = min(tx, ty) if tx > 0 or ty > 0 else 0

            x += dx * t
            y += dy * t

        # Apply offset in the direction of the angle
        if offset != 0:
            import math

            rad = math.radians(angle)
            x += math.cos(rad) * offset
            y -= math.sin(rad) * offset  # Subtract because y increases downward

        return Point(x, y)


class Element:
    id_counter = 0

    @classmethod
    def generate_id(cls):
        cls.id_counter += 1
        return cls.id_counter

    @property
    def compass(self):
        return Compass(self.frame)

    def __init__(self, id=None):
        self.id = id
        self.uid = self.generate_id()
        self.frame = Rect()

        self.parent = None
        self.children: List[Element] = []

    def add(self, *elements: Element) -> Self:
        for element in elements:
            self.children.append(element)
            element.parent = self

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id or self.uid}, frame={self.frame})"
