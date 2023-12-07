
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

import math
import numpy as np
from enum import Enum

epsilon = 1e-6

class TurnDirection(Enum):
    Right = 1
    Left = -1
    NoTurn = 0

class Point:
           
    def __init__(self, p, i=None):
        
        if not isinstance(p, np.ndarray):
            raise ValueError("Point only supports ndarray")
                    
        self.p = p
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
        if isinstance(scalar, (float)):
            self.p *= scalar
            return self.p
        else:
            raise ValueError("Multiplication is only supported with scalar values.")

    def __truediv__(self, scalar):
        if isinstance(scalar, (float)):
            if scalar == 0.0:
                return Point.zero()
            self.p /= scalar
            return self.p
        else:
            raise ValueError("Division is only supported with scalar values.")

    def __eq__(self, other):
        if other is None: return False
        if np.abs(self.p[0] - other.p[0]) > epsilon: return False
        if np.abs(self.p[1] - other.p[1]) > epsilon: return False
        if np.abs(self.p[2] - other.p[2]) > epsilon: return False
        return True
         
    def copy(self):
        return Point(self.p.copy(), self.i)
            
    @classmethod
    def zero(cls):
        return cls(np.array([0.0, 0.0, 0.0]))
    
def dot(u, v):
    dx = u[0] * v[0]
    dy = u[1] * v[1]
    dz = u[2] * v[2]
    return dx + dy + dz

def cross(u, v):
    x = u[1] * v[2] - u[2] * v[1]
    y = u[2] * v[0] - u[0] * v[2]
    z = u[0] * v[1] - u[1] * v[0]
    return Point(np.array([x, y, z]))

def length(u):
    sx = u[0] * u[0]
    sy = u[1] * u[1]
    sz = u[2] * u[2]
    return math.sqrt(sx + sy + sz)
    
class Triangle:
    def __init__(self, p0, p1, p2):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2

def turn(p, u, n, q):
   
    v = cross(q.p - p.p, u)
     
    d = dot(v, n)

    if d > +0.001: return TurnDirection.Right
    if d < -0.001: return TurnDirection.Left

    return TurnDirection.NoTurn

def triangleAreaSquared(a, b, c):
    c = cross(b.p - a.p, c.p - a.p)
    return length(c)**2.0 / 4.0

def normalize(v):
    return v/length(v)

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

    if np.abs(v[0]) < epsilon: v[0] = 0.0
    if np.abs(v[1]) < epsilon: v[1] = 0.0
    if np.abs(v[2]) < epsilon: v[2] = 0.0

    return normalize(v)

def getBarycentricTriangleCoordinates(a, b, c, p):
    alpha = beta = gamma = -2.0 * epsilon

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

    if n <  3: return False
    if n == 3: return True

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

    if n == 3: return 0
    if n == 0: return -1

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

    if n <  3: return False
    if n == 3: return True

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

    if n < 3: return False

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
    n = len(polygon)
    for index in range(n):
        item = polygon[index % n]
        next = polygon[(index + 1) % n]
        if item.i == next.i: continue
        uniquePolygon.append(item)
    return uniquePolygon

def triangulate(polygon):
    
    polygon = removeConsecutiveEqualPoints(polygon)
    
    n = normal(polygon)
    
    if len(polygon) < 3:
        return [], n

    if len(polygon) == 3:
        t = Triangle(polygon[0], polygon[1], polygon[2])
        return [t], n

    if convex(polygon, n):
        return fanTriangulation(polygon), n

    return cutTriangulation(polygon, n), n