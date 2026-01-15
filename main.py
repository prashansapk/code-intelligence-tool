from pathlib import Path

def getAllLines(allCode):
    lines = allCode.split("\n")
    return lines

def readFiles(path):
    for file in path.iterdir():
        # print(file.name)

        if file.name.endswith(".py") or file.name.endswith(".ts") or file.name.endswith(".java"):
            # print(file.name)
            content = file.read_text()
            
            linesList = getAllLines(content)
            for line in linesList:
                x = line.strip()
                if x.startswith("def "):
                    # print(line)
                    x=line.find("(")
                    # There is a corner case, if there is multiline string and If a line starts with def then it will also count. 
                    # print(x)
                    y=line[4:x]
                    z=y.strip()
                    print(z)
            linesList = getAllLines(content)
            for line in linesList:
                x = line.strip()
                if x.startswith("Class"):
                    # print(line)
                    x=line.find("(")
                    # print(x)
                    y=line[4:x]
                    z=y.strip()
                    print(z)
                    
                    

        isFolder = file.is_dir()
        # print(file.name+" is a folder "+ str(isFolder))
        if isFolder:
            readFiles(Path(str(path)+"/"+file.name))


pathname = input("Enter path name")
x = Path(pathname)
readFiles(x)