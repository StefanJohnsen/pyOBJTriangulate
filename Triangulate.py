
# Triangulate.py - Python script for triangulating polygons
#
# This script specializes in triangulating polygons using two techniques:
# - Fan method for convex polygons
# - Earcut technique for concave polygons
#
# Copyright (c) 2023 by FalconCoding
# Author: Stefan Johnsen
# Email: stefan.johnsen@outlook.com
#
# This software is released under the MIT License.

import numpy as np
from enum import Enum

epsilon = 1e-6

class TurnDirection(Enum):
    Right = 1
    Left = -1
    NoTurn = 0

class Point:
           
    def __init__(self, p, i=None):
        self.p = p.copy()
        self.i = i

    def __getitem__(self, index):
        return self.p[index]

    def __setitem__(self, index, value):
        self.p[index] = value
                            
    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.p + other.p)
        else:
            raise ValueError("Addition is only supported between Point objects.")

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.p - other.p)
        else:
            raise ValueError("Subtraction is only supported between Point objects.")

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Point(self.p * scalar)
        else:
            raise ValueError("Multiplication is only supported with scalar values.")

    def __truediv__(self, scalar):
        if isinstance(scalar, (int, float)):
            if scalar != 0:
                return Point(self.p / scalar)
            else:
                raise ValueError("Division by zero is not allowed.")
        else:
            raise ValueError("Division is only supported with scalar values.")

    def __eq__(self, other):
        if other is None: return False
        if np.abs(self.p[0] - other.p[0]) > epsilon: return False
        if np.abs(self.p[1] - other.p[1]) > epsilon: return False
        if np.abs(self.p[2] - other.p[2]) > epsilon: return False
        return True
        
    def copy(self):
        return Point(self.p, self.i)
            
    @classmethod
    def zero(cls):
        return cls([0, 0, 0])
    
def dot(u, v):
    return np.dot(u.p, v.p)

def cross(u, v):
    return Point(np.cross(u.p, v.p))

def magnitude(u):
    return np.linalg.norm(u.p)
    
class Triangle:
    def __init__(self, p0=Point.zero(), p1=Point.zero(), p2=Point.zero()):
        self.p0 = p0.copy()
        self.p1 = p1.copy()
        self.p2 = p2.copy()
        
    def normal(self):
        u = self.p1 - self.p0
        v = self.p2 - self.p1
        return cross(v, u)

def turn(p, u, n, q):
    d = dot(cross(q - p, u), n)

    if d > 0.0:
        return TurnDirection.Right
    elif d < 0.0:
        return TurnDirection.Left
    else:
        return TurnDirection.NoTurn

def triangleAreaSquared(a, b, c):
    c = cross(b - a, c - a)
    return magnitude(c)**2 / 4.0

def normalize(v):
    m = magnitude(v)
    return v/m if m != 0 else Point.zero()

def normal(polygon):
    n = len(polygon)
    v = Point.zero()

    if n < 3: return v

    for index in range(n):
        item = polygon[index % n]
        next = polygon[(index + 1) % n]

        v[0] += (next[1] - item[1]) * (next[2] + item[2])
        v[1] += (next[2] - item[2]) * (next[0] + item[0])
        v[2] += (next[0] - item[0]) * (next[1] + item[1])

    return normalize(v)

def getBarycentricTriangleCoordinates(a, b, c, p):
    alpha = beta = gamma = -2 * epsilon

    v0 = c - a
    v1 = b - a
    v2 = p - a

    dot00 = dot(v0, v0)
    dot01 = dot(v0, v1)
    dot02 = dot(v0, v2)
    dot11 = dot(v1, v1)
    dot12 = dot(v1, v2)

    denom = dot00 * dot11 - dot01 * dot01

    if abs(denom) < epsilon:
        return alpha, beta, gamma

    alpha = (dot11 * dot02 - dot01 * dot12) / denom
    beta = (dot00 * dot12 - dot01 * dot02) / denom
    gamma = 1.0 - alpha - beta

    return alpha, beta, gamma

def pointInsideOrEdgeTriangle(a, b, c, p):
    alpha, beta, gamma = getBarycentricTriangleCoordinates(a, b, c, p)
    return alpha >= -epsilon and beta >= -epsilon and gamma >= -epsilon

def isEar(index, polygon, normal):
    n = len(polygon)

    if n < 3:
        return False

    if n == 3:
        return True

    prevIndex = (index - 1 + n) % n
    itemIndex = index % n
    nextIndex = (index + 1) % n

    prev = polygon[prevIndex]
    item = polygon[itemIndex]
    next = polygon[nextIndex]

    u = normalize(item - prev)

    if turn(prev, u, normal, next) != TurnDirection.Right:
        return False

    for i in range(n):
        if i in (prevIndex, itemIndex, nextIndex):
            continue

        p = polygon[i]
        if pointInsideOrEdgeTriangle(prev, item, next, p):
            return False

    return True

def getBiggestEar(polygon, normal):
    n = len(polygon)

    if n == 3:
        return 0

    if n == 0:
        return -1

    maxIndex = -1
    maxArea = float("-inf")

    for index in range(n):
        if isEar(index, polygon, normal):
            prev = polygon[(index - 1 + n) % n]
            item = polygon[index % n]
            next = polygon[(index + 1) % n]

            area = triangleAreaSquared(prev, item, next)

            if area > maxArea:
                maxIndex = index
                maxArea = area

    return maxIndex

def convex(polygon, normal):
    n = len(polygon)

    if n < 3:
        return False

    if n == 3:
        return True

    polygonTurn = TurnDirection.NoTurn

    for index in range(n):
        prev = polygon[(index - 1 + n) % n]
        item = polygon[index % n]
        next = polygon[(index + 1) % n]

        u = normalize(item - prev)
        item_turn = turn(prev, u, normal, next)

        if item_turn == TurnDirection.NoTurn:
            continue

        if polygonTurn == TurnDirection.NoTurn:
            polygonTurn = item_turn

        if polygonTurn != item_turn:
            return False

    return True

def clockwiseOriented(polygon, normal):
    n = len(polygon)

    if n < 3:
        return False

    orientationSum = 0.0

    for index in range(n):
        prev = polygon[(index - 1 + n) % n]
        item = polygon[index % n]
        next = polygon[(index + 1) % n]

        edge = item - prev
        toNextPoint = next - item

        v = cross(edge, toNextPoint)
        orientationSum += dot(v, normal)

    return orientationSum < 0.0

def makeClockwiseOrientation(polygon, normal):
    if len(polygon) < 3:
        return

    if not clockwiseOriented(polygon, normal):
        polygon.reverse()

def fanTriangulation(polygon):
    triangles = []
    for index in range(1, len(polygon) - 1):
        triangles.append(Triangle(polygon[0], polygon[index], polygon[index + 1]))
    return triangles

def cutTriangulation(polygon, normal):
    
    triangles = []
    
    makeClockwiseOrientation(polygon, normal)

    while polygon:
        index = getBiggestEar(polygon, normal)

        if index == -1: return []

        n = len(polygon)

        prev = polygon[(index - 1 + n) % n]
        item = polygon[index % n]
        next = polygon[(index + 1) % n]

        triangles.append(Triangle(prev, item, next))

        del polygon[index]

        if len(polygon) < 3: break

    return triangles if len(polygon) < 3 else []

def removeConsecutiveEqualPoints(polygon):
    uniquePolygon = []
    last_point = None

    for point in polygon:
        if point != last_point:
            uniquePolygon.append(point)
            last_point = point

    return uniquePolygon

def triangulate(polygon):
    
    polygon = removeConsecutiveEqualPoints(polygon)
    
    if len(polygon) < 3:
        return [], Point.zero()

    if len(polygon) == 3:
        t = Triangle()
        t.p0 = polygon[0].copy()
        t.p1 = polygon[1].copy()
        t.p2 = polygon[2].copy()
        return [t], t.normal()
    
    n = normal(polygon)

    if convex(polygon, n):
        return fanTriangulation(polygon), n

    return cutTriangulation(polygon, n), n