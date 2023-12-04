
import os
import sys
import numpy as np
import Triangulate

vector = np.array
point = Triangulate.Point

def listIndex(index, indexToList):
    i = int(index)
    if i > 0: return i - 1
    return i + len(indexToList)

def copy(source, target):
    if source is None or target is None:
        return

    if not os.path.exists(source):
        print(f"File not found: {source}")
        return

    if os.path.exists(target):
        os.remove(target)
        #print(f"File already exists: {target}")
        #return

    vertex   = []

    with open(target, 'w') as targetFile:
        with open(source, 'r') as sourceFile:
            for line in sourceFile:
                
                line = line.strip()
                
                if line != '':
                    words = line.split()
                    command = words[0]
                    data = words[1:]
                    
                    if command == 'v':
                        x, y, z = map(float, data[:3])
                        vertex.append(vector([x, y, z]))
                
                    elif command == 'f' and len(data) > 3:
                        polygon = []
                        for i in range(len(data)):
                            word = data[i]
                            indices = word.split('/')
                            if len(indices) > 0:
                                index = indices[0]
                                v = vertex[listIndex(index, vertex)]
                                p = point(v, i)
                                polygon.append(p)
                        
                        if len(polygon) > 0:
                            triangles, _ = Triangulate.triangulate(polygon)
                            if len(triangles) > 0:
                                for triangle in triangles:
                                    line = "f "
                                    line += data[triangle.p0.i] + ' '
                                    line += data[triangle.p1.i] + ' '
                                    line += data[triangle.p2.i] + '\n'
                                    targetFile.write(line)
                                continue
                    
                targetFile.write(line + '\n')
              
    targetFile.close()
    sourceFile.close()
    
    print(f"File copied from {source} to {target}")       
        
if __name__ == "__main__":
    
    #if len(sys.argv) != 3:
    #    print("Usage: python main.py <source_file> <target_file>")
    #    sys.exit(1)

    #source_file = sys.argv[1]
    #target_file = sys.argv[2]
    source_file = "lego.obj"
    target_file = "lego2.obj"

    copy(source_file, target_file)