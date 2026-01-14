from pathlib import Path

def readFiles(path):
    for file in path.iterdir():
        # print(file.name)

        if file.name.endswith(".py") or file.name.endswith(".ts") or file.name.endswith(".java"):
            print(file.name)
            content = file.read_text()
            print(content)

        isFolder = file.is_dir()
        # print(file.name+" is a folder "+ str(isFolder))
        if isFolder:
            readFiles(Path(str(path)+"/"+file.name))


pathname = input("Enter path name")
x = Path(pathname)
readFiles(x)