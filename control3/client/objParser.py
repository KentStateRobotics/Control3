#Colin Green 
#Rev 1.0

def objParser(file):
    """
        This function opens and parses .obj files and their attached material libraries and returns: 
        a list of face coordinates that holds (material, a, ,b ,c. object) in each indice
        with a, b, and c being locations of a vertex in the vertex list,
        a list of verticies that holds (x,y,z,w) information in each indice,
        and a material list that holds (r,g,b) information in each indice
    """
    objFile = open(str(file), "r")
    matFile = []
    vertList = []
    faceList = []
    matList = []  

    for line in objFile: #start reading obj file
        line = line.strip()
        if line.startswith("mtllib"): #find material library
            elements = line.split(" ")
            matFile = open(str(elements[1]), "r") 
            for line in  matFile: #Start reading material library 
                line = line.strip()
                if line.startswith("newmtl"): #Find material name
                    elements = line.split(" ")
                    mName = elements[1]

                if line.startswith("Kd"): #Get colors and populate matList with material name and color
                    elements = line.split(" ")
                    a = float(elements[1])
                    b = float(elements[2])
                    c = float(elements[3])
                    matList.append([mName, (a*255, b*255, c*255)])

        if line.startswith("v"): #If line is a vector make new indice in vertList with coodinates
            elements = line.split(" ")
            x = float(elements[1])
            y = float(elements[2])
            z = float(elements[3])
            w = 1
            vertList.append([x, y, z, w])

        if line.startswith("usemtl"): #Find material associated with faces 
            elements = line.split(" ")
            material = elements[1]

        if line.startswith("g"): #Find object name associated with faces
            elements = line.split(" ")
            objName = elements[1]

        if line.startswith("f"): #If line is a face then get verticies and generate indice with material name object name and verticies for each corner
            elements = line.split(" ")
            a = int(elements[1])-1
            b = int(elements[2])-1
            c = int(elements[3])-1
            faceList.append([material, a, b, c, objName])

    return (faceList, vertList, matList) 

file = "sceneReal.obj"
output = objParser(file)
print(output[2])