# this file is called geometry


from __future__ import annotations
from typing import List, Self
import math


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


class Frame:
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

    def get(self, angle):

        angle = angle % 360
        rad = math.radians(angle)
        # Start from center
        x = self.center.x
        y = self.center.y

        dx = math.cos(rad)
        dy = -math.sin(rad)  # Negative because y increases downward

        tx1 = (self.frame.left - x) / dx
        tx2 = (self.frame.right - x) / dx
        tx = max(tx1, tx2) if dx < 0 else min(tx1, tx2)

        ty1 = (self.frame.top - y) / dy
        ty2 = (self.frame.bottom - y) / dy
        ty = max(ty1, ty2) if dy < 0 else min(ty1, ty2)

        t = min(tx, ty) if tx > 0 or ty > 0 else 0

        x += dx * t
        y += dy * t

        return Point(x, y)

    @property
    def northwest(self):
        return self.get(135deg)


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
