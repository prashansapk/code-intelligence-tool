from pathlib import Path
import aiohttp
import asyncio
import json
import matplotlib.pyplot as plt

def fileCounter(path):
    if path.endswith(".py"):
        codeCounts["pythonCount"] += 1
    if path.endswith(".ts"):
        codeCounts["tsCount"] += 1
    elif path.endswith(".js"):
        codeCounts["jsCount"] += 1
    elif path.endswith(".html"):
        codeCounts["htmlCount"] += 1


def getAllLines(allCode):  
    lines = allCode.split("\n")
    return lines

def printMethodsAndClasses(code,fileName):
    print("_______________________________")
    print(f"Methods and classes in {fileName}-")
    for line in code:
        x = line.strip()
        if x.startswith("def "):
            x=line.find("(")
            # There is a corner case, if there is multiline string and If a line starts with def then it will also count.
            y=line[4:x]
            z=y.strip()
            print("method: ",z)
        elif x.startswith("async def "):
            # There is a corner case, if there are multiline spaces between async and def, that is not handled
            x=line.find("(")
            y=line[10:x]
            z=y.strip()
            print("method: ",z)
        elif x.startswith("Class"):
            x=line.find("(")
            y=line[5:x]
            z=y.strip()
            print("class: ",z)
    
    print("_______________________________")
    print("")
    print("")

async def crawlPage(session, baseUrl, relPath, branch):
    # global pythonCount, tsCount, jsCount, htmlCount
    path = baseUrl + relPath

    async with session.get(path) as response:
        content = await response.text()

    branchIndex = content.find("\"defaultBranch\":")

    if branchIndex == -1:
        return
    if branch == '':
        substring = content[branchIndex + 17 : branchIndex + 57] # considering max length of branch name to be 40
        nextCommaIndex = substring.find(",") # this(nextCommaIndex) is actually the length of the branch name
        if nextCommaIndex == -1:
            return
        branch = content[branchIndex + 17 : branchIndex + 17 + nextCommaIndex - 1]

    index = content.find("\"tree\":{\"items\":")
    if index == -1:
        return

    filesStr = content[index + len("\"tree\":{\"items\":"):]
    indexOfEnd = filesStr.find("]")
    filesArrayStr = filesStr[:indexOfEnd + 1]

    filesArray = json.loads(filesArrayStr)

    for item in filesArray:
        name = item.get("name")
        contentType = item.get("contentType")
        if contentType:
            if contentType == "directory":
                if relPath == "":
                    newRelPath = f"/tree/{branch}/" + name
                else:
                    newRelPath = relPath + "/" + name

                await crawlPage(session, baseUrl, newRelPath, branch)
            else:
                path = baseUrl +f"/blob/{branch}"+ relPath + "/" + name
                if len(relPath)>0:
                    print(relPath + "/" + name)
                else:
                    print(name)
                async with session.get(path) as response:
                    content = await response.text()

                fileCounter(path)
                if path.endswith(".py"):
                    delimiter = "data-target=\"react-app.embeddedData\">"
                    startIndex = content.find(delimiter) + len(delimiter)
                    codeStr = content[startIndex:-1]
                    endIndex = codeStr.find("</script>")
                    codeStr = codeStr[0:endIndex]
                    codeObj = json.loads(codeStr)
                    payload = codeObj.get("payload")
                    if payload:
                        blob = payload.get("blob")
                        if blob:
                            code = blob.get("rawLines")
                            printMethodsAndClasses(code,name)

codeCounts = {
    "pythonCount":0,
    "tsCount":0,
    "jsCount":0,
    "htmlCount":0
}

async def crawlGit(baseUrl):
    if(baseUrl.endswith("/")):
        baseUrl = baseUrl[0:-1]
    branch = ''
    async with aiohttp.ClientSession() as session:
        await crawlPage(session, baseUrl, "", branch)

def readFiles(path):
    try:
        for file in path.iterdir():
            
            isFolder = file.is_dir()
            # print(file.name+" is a folder "+ str(isFolder))
            if isFolder:
                if file.name != '.git':
                    readFiles(Path(str(path)+"/"+file.name))
            else:
                print(str(file.name))
                fileCounter(str(file.name))
                content = file.read_text()
                linesList = getAllLines(content)
                printMethodsAndClasses(linesList,str(file.name))
    except Exception:
        print("Something went wrong while reading local files")
                


async def main():
    inputPath = input("Enter your local repo path or Git url: ").strip()
    
    if inputPath.startswith("http") or inputPath.startswith("www"):
        await crawlGit(inputPath)
    else:
        readFiles(Path(inputPath))


    print(codeCounts)

    labels = codeCounts.keys()
    values = codeCounts.values()
    plt.bar(labels,values)
    plt.show()

asyncio.run(main())