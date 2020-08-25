#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import subprocess
from process import getDependencies


# 从两个 dict 生成一个字符串列表表示从 dict1 -> dict2 中每个项的变动
# 返回一个表示变化的字符串列表
# 输出的格式为 ：
# 改动 ： name version1 -> version2 , M
# 新增 ： name version2 , A
# 减少 ： name version1 , D
def buildOutput(dict1, dict2):
    strList = []
    while len(dict1) > 0:
        (name1, value1) = dict1.popitem()
        foundInDict2 = False
        for name2 in dict2:
            if name1 == name2:
                # same dependency name , but different versions
                if value1 != dict2[name2]:
                    strList.append(name1 + " " + value1 + " -> " + dict2[name2] + " , M")
                dict2.pop(name2)
                foundInDict2 = True
                break
        if not foundInDict2:
            strList.append(name1 + " " + value1 + " , D")
    # add left entries in dict2, these are new added
    for name2 in dict2:
        strList.append(name2 + " " + dict2[name2] + " , A")
    return strList


# gitDir : 一个 git 仓库目录, 会在该仓库的前一个 commit 和当前 commit 的 dependency 之间做 diff
# gradleCmd : string; gradle 语句,应该输出 dependency 信息(如 `./gradlew :app:dependencies`);
#               之所以这样设计, 是因为 gradle 命令的目录位置与 gitDir 的不确定, 要列出的 module 也不同.所以采用外部传递的方式
def getDiffDependencyList(gitDir, gradleCmd):
    PROJECT_DIR = gitDir
    print(f"\ngitDir : \"${gitDir}\"\ngradleCmd : \"${gradleCmd}\"")
    gradleCmdList = gradleCmd.split(" ")
    os.chdir(PROJECT_DIR)
    currentRevision = subprocess.check_output(
        "git rev-parse HEAD".split(" ")).decode('utf-8').splitlines()[0]
    print("\nretrieving old dependencies ...\n")
    subprocess.check_output(("git reset --hard " + currentRevision + "^").split(" "))
    oldDepOutput = subprocess.check_output(gradleCmdList).decode('utf-8').splitlines()
    oldDepDict = getDependencies(oldDepOutput)
    print(oldDepDict)
    print("\nretrieving new dependencies ...\n")
    subprocess.check_output(("git reset --hard " + currentRevision).split(" "))
    newDepOutput = subprocess.check_output(gradleCmdList).decode('utf-8').splitlines()
    newDepDict = getDependencies(newDepOutput)
    print(newDepDict)
    output = buildOutput(oldDepDict, newDepDict)
    print("\n\nChanges:")
    for s in output:
        print(s)
        print()
    return output

