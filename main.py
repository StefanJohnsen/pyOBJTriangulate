
import os
import sys
import numpy as np
import Triangulate

vector = np.array

class Face:
    def __init__(self):
        self.vertex  = []
        self.texture = []
        self.normal  = []
        
def index(objIndex, indexToList):
    i = int(objIndex)
    if i > 0: return i - 1
    return i + len(indexToList)

def faceIndex(point, face, vertex):
    size = len(face.vertex)
    for n in range(size):
        i = face.vertex[n]
        p = vertex[index(i, vertex)]
        if p == point:
            return n
    return None    

def faceTriangleIndex(index, face):
    line = " "
    vertex = face.vertex
    texture = face.texture
    normal = face.normal
    if len(vertex) == len(normal) and len(vertex) == len(vertex):
        line += vertex[index]
        line += "/"
        line += texture[index]
        line += "/"
        line += normal[index]
    elif len(vertex) == len(normal):
        line += vertex[index]
        line += "//"
        line += normal[index]
        return line
    else:
        line += vertex[index]
    return line

def faceTriangle(triangle, face, vertex):
    index0 = faceIndex(triangle.p0, face, vertex)
    if index0 is None: return None
    index1 = faceIndex(triangle.p0, face, vertex)
    if index1 is None: return None
    index2 = faceIndex(triangle.p0, face, vertex)
    if index2 is None: return None
    line = "f"
    line += faceTriangleIndex(index0, face) 
    line += faceTriangleIndex(index1, face) 
    line += faceTriangleIndex(index2, face) 
    return line

def copy(source, target):
    if source is None or target is None:
        return

    if not os.path.exists(source):
        print(f"File not found: {source}")
        return

    if os.path.exists(target):
        print(f"File already exists: {target}")
        return

    vertex   = []
    texture  = []
    normal   = []

    with open(target, 'w') as targetFile:
        with open(source, 'r') as sourceFile:
            for line in sourceFile:
                line = line.strip()
                
                if not line: continue

                words = line.split()
                command = words[0]
                data = words[1:]
                
                if command == 'v':  # Vertex
                    x, y, z = map(float, data[:3])
                    vertex.append(vector([x, y, z]))

                elif command == 'vt':  # Texture
                    x, y = map(float, data[:2])
                    texture.append(vector([x, y, 0]))

                elif command == 'vn':  # Normal
                    x, y, z = map(float, data[:3])
                    normal.append(vector([x, y, z]))
                
                elif command == 'f':  # Face
                    face = Face()
                    for group in data:
                        indices = group.split('/')
                        if len(indices) == 0:
                            continue
                        if len(indices) > 0 and indices[0]:
                            face.vertex.append(indices[0])
                        if len(indices) > 1 and indices[1]:
                            face.texture.append(indices[1])
                        if len(indices) > 2 and indices[2]:
                            face.normal.append(indices[2])
                            
                    if len(face.vertex) == 0:
                        continue
                    
                    polygon = []
                    for i in face.vertex:
                        v = vertex[index(i, vertex)]
                        polygon.append(v)
                    
                    if len(polygon) == 0:
                        continue
                                        
                    triangles, _ = Triangulate.triangulate(polygon)
                    
                    if len(triangles) == 0:
                        continue
                    
                    lines = ""
                    
                    for triangle in triangles:
                        text = faceTriangle(triangle, face, vertex)
                        if text is None:
                            lines = ""
                            break
                        if lines == "":
                            lines = text
                        else:
                            lines += '\n'
                    
                    if lines is not "":
                        line = lines
                    
                targetFile.write(line + '\n')
              
    targetFile.close()
    sourceFile.close()
    
    print(f"File copied from {source} to {target}")       
        
if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print("Usage: python main.py <source_file> <target_file>")
        sys.exit(1)

    source_file = sys.argv[1]
    target_file = sys.argv[2]

    copy(source_file, target_file)