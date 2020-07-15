import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_from(self, other):
        distance = math.sqrt(((self.x-other.x)**2) + ((self.y-other.y)**2))
        return distance

class Circle:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def is_inside(self, point):
        if point.distance_from(self.center) < self.radius:
            return True
        else:
            return False
