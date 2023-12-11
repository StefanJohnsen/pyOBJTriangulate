# pyOBJTriangulate
Wavefront OBJ files typically consist of triangles, but they can also include quads and polygons. This script aims to convert all quads and polygons found in an OBJ file and create a new OBJ file containing only triangles.<br><br>
This script is using the python script in the repository [pyTriangulate](https://github.com/StefanJohnsen/pyTriangulate).

# Example
The trumpet.obj file contains quads and polygons. Just run the script as follows 
```
python main.py .\objFiles\trumpet.obj .\objFiles\trumpet.triangulate.obj
```

![Trumpet](https://github.com/StefanJohnsen/pyOBJTriangulate/blob/main/pictures/trumpet.png)
*result trumpet.triangulate.obj*

# License
This software is released under the MIT License terms.
