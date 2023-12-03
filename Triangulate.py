
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

class Triangle:
    def __init__(self, p0, p1, p2):
        self.p0 = np.array(p0)
        self.p1 = np.array(p1)
        self.p2 = np.array(p2)

def turn(p, u, n, q):
    d = np.dot(np.cross(q - p, u), n)

    if d > 0.0:
        return TurnDirection.Right
    elif d < 0.0:
        return TurnDirection.Left
    else:
        return TurnDirection.NoTurn

def triangleAreaSquared(a, b, c):
    c = np.cross(b - a, c - a)
    return np.linalg.norm(c)**2 / 4.0

def normalize(v):
    m = np.linalg.norm(v)
    return v / m if m != 0 else np.array([0, 0, 0])

def normal(polygon):
    n = len(polygon)
    v = np.array([0, 0, 0])

    if n < 3:
        return v

    for index in range(n):
        item = np.array(polygon[index % n])
        next_item = np.array(polygon[(index + 1) % n])

        v[0] += (next_item[1] - item[1]) * (next_item[2] + item[2])
        v[1] += (next_item[2] - item[2]) * (next_item[0] + item[0])
        v[2] += (next_item[0] - item[0]) * (next_item[1] + item[1])

    return normalize(v)

def getBarycentricTriangleCoordinates(a, b, c, p):
    alpha = beta = gamma = -2 * epsilon

    v0 = c - a
    v1 = b - a
    v2 = p - a

    dot00 = np.dot(v0, v0)
    dot01 = np.dot(v0, v1)
    dot02 = np.dot(v0, v2)
    dot11 = np.dot(v1, v1)
    dot12 = np.dot(v1, v2)

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

    prev = np.array(polygon[prevIndex])
    item = np.array(polygon[itemIndex])
    next_item = np.array(polygon[nextIndex])

    u = normalize(item - prev)

    if turn(prev, u, normal, next_item) != TurnDirection.Right:
        return False

    for i in range(n):
        if i in (prevIndex, itemIndex, nextIndex):
            continue

        p = np.array(polygon[i])
        if pointInsideOrEdgeTriangle(prev, item, next_item, p):
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
            prev = np.array(polygon[(index - 1 + n) % n])
            item = np.array(polygon[index % n])
            next_item = np.array(polygon[(index + 1) % n])

            area = triangleAreaSquared(prev, item, next_item)

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
        prev = np.array(polygon[(index - 1 + n) % n])
        item = np.array(polygon[index % n])
        next_item = np.array(polygon[(index + 1) % n])

        u = normalize(item - prev)
        item_turn = turn(prev, u, normal, next_item)

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
        prev = np.array(polygon[(index - 1 + n) % n])
        item = np.array(polygon[index % n])
        next_item = np.array(polygon[(index + 1) % n])

        edge = item - prev
        toNextPoint = next_item - item

        v = np.cross(edge, toNextPoint)
        orientationSum += np.dot(v, normal)

    return orientationSum < 0.0

def makeClockwiseOrientation(polygon, normal):
    if len(polygon) < 3:
        return

    if not clockwiseOriented(polygon, normal):
        polygon.reverse()

def fanTriangulation(polygon):
    triangles = []
    for index in range(1, len(polygon) - 1):
        triangles.append(Triangle(np.array(polygon[0]), np.array(polygon[index]), np.array(polygon[index + 1])))
    return triangles

def cutTriangulation(polygon, normal):
    triangles = []
    makeClockwiseOrientation(polygon, normal)

    while polygon:
        index = getBiggestEar(polygon, normal)

        if index == -1:
            return []

        n = len(polygon)

        prev = np.array(polygon[(index - 1 + n) % n])
        item = np.array(polygon[index % n])
        next_item = np.array(polygon[(index + 1) % n])

        triangles.append(Triangle(prev, item, next_item))

        del polygon[index]

        if len(polygon) < 3:
            break

    return triangles if len(polygon) == 2 else []

def triangulate(polygon):
    if len(polygon) < 3:
        return []

    if len(polygon) == 3:
        return [Triangle(np.array(polygon[0]), np.array(polygon[1]), np.array(polygon[2]))]

    n = normal(polygon)

    if convex(polygon, n):
        return fanTriangulation(polygon), n

    return cutTriangulation(polygon, n), n