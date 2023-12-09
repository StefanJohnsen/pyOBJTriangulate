
import os
import sys
import numpy as np
import Triangulate

vector = np.array
point = Triangulate.Point

def listIndex(index, indexToList):
    if index > 0: return index - 1
    return index + len(indexToList)

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

    vertex = []

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
                
                    elif command == 'f':
                        
                        polygon = []
                        index_word = {}       
                                         
                        for i in range(len(data)):
                            word = data[i]
                            indices = word.split('/')
                            if len(indices) > 0:
                                index = int(indices[0])
                                index = listIndex(index, vertex)
                          
                                if index not in index_word:
                                    index_word[index] = word

                                v = vertex[index]
                                p = point(v[0], v[1], v[2], index)
                                polygon.append(p)
                        
                        if len(polygon) == 0:
                            continue
                        
                        triangles, _ = Triangulate.triangulate(polygon)

                        if len(triangles) == 0:
                            continue
                        
                        for triangle in triangles:
                            line = "f "
                            line += index_word[triangle.p0.i] + ' '
                            line += index_word[triangle.p1.i] + ' '
                            line += index_word[triangle.p2.i]
                            targetFile.write(line + '\n')

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
    source_file = "c:\\temp\\trumpet.obj"
    target_file = "c:\\temp\\trumpet2.obj"

    copy(source_file, target_file)