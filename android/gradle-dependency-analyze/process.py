#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re

# match
reStr = "[\W]*"
# match dependency name, re.group(1)
reStr += "([\-\.\w]+:[\-\.\w]+:)"
# match decalared version. re.group(3). including format `:{strictly 1.1.0.Final} -> 1.1.0.Final (c)`
reStr += "({strictly )?([\-\.\w]+)}?"
# match selected version, re.group(4)
reStr += "( -> ([\-\.\w]+))?"
RE_PATTERN = reStr


# 从 `gradle dependencies` 打印的结果里返回 release 版本的依赖部分
# 输入 ： `gradle dependencies` 打印的结果，使用 readLines 读取的文本列表。
# 输出 ： 其中 `releaseCompileClasspath` 部分的数据
def full2ReleaseDependencies(fullStr):
    begin = -1
    end = -1
    for index in range(len(fullStr)):
        s = fullStr[index]
        if s.strip().startswith("releaseCompileClasspath - "):
            begin = index + 1
            continue
        if begin != -1 and s.strip() == "":
            end = index
            break
    return fullStr[begin:end]


# 从 `gradle dependencies` 打印的结果构建一个 map, key 为 依赖名, value 为 版本号
# 会忽略 aar 依赖以及 project 依赖,因为这两类是没有确切的版本号的.
def dependenciesStr2List(ds):
    dict = {}
    pattern = RE_PATTERN
    for d in ds:
        stripped = d.strip()
        print(stripped)
        if (stripped.endswith("(*)")):
            continue
        r = re.search(pattern, stripped)
        if r is not None:
            dependencyName = r.group(1)
            dependencyVersion = r.group(3)
            if (r.group(4)):
                dependencyVersion = r.group(4)
            dict[dependencyName] = dependencyVersion
    return dict


# 将 `gradle dependencies` 的结果，转成 map ,key 为 依赖名, value 为 版本号
# 输入 ：列表。  `gradle dependencies` 的输出,按换行切分元素。
# 输出 ： 一个 map， key 为依赖名， value 为版本号
def getDependencies(fullStr):
    m = full2ReleaseDependencies(fullStr)
    return dependenciesStr2List(m)

"下面的是暂时保存，方便改进成 树状差异 的输出"
"""

class Node:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.children = []
    children = []
    parent = None
    name = ""
    version = ""


def indexOfFirstCharInStr(str):
    r = re.search(r"(\W*)(\w).*", str)
    return len(r.group(1))


def dependencyNameAndVersionOf(str):
    r = re.search(RE_PATTERN, str)
    name = r.group(1)
    version = r.group(2)
    if(r.group(4)):
        version = r.group(4)
    return [name, version]


# 从 `gradle dependencies` 中某一块（即 full2ReleaseDependencies 方法返回的格式）打印的结果构建一个树
def dependenciesStr2Tree(ds):
    # 少， 不处理。
    if(len(ds) < 1):
        exit(1, "Error, too few dependencies")
    root = Node("g", "g")
    # 当前行的上一行， 从 root 到其的路径，最后一个为其。
    lastLineRoutes = [root]
    # indent 单元一第一个为目标
    indentUnit = indexOfFirstCharInStr(ds[0].strip())
    # 为 0 的话，本处理算法会出问题。暂不处理为 0 情况
    if(indentUnit == 0):
        exit(1, "Error , indent unit should not be 0")
    # 处理第一行
    lastLineIndent = 0
    for i in range(0, len(ds)):
        s = ds[i]
        t = indexOfFirstCharInStr(s.strip())
        cIndent = t / indentUnit
        nameAndVersion = dependencyNameAndVersionOf(s)
        currentLineNode = Node(nameAndVersion[0], nameAndVersion[1])
        if(cIndent > lastLineIndent):
            if(cIndent != lastLineIndent + 1):
                exit(1, "Error, can not have more than 1 indent unit in next line")
        else:
            diff = lastLineIndent - cIndent
            for j in range(diff+1):
                lastLineRoutes.pop()
        parentNode = lastLineRoutes[-1]
        parentNode.children.append(currentLineNode)
        currentLineNode.parent = parentNode
        # print "for ["+currentLineNode.name+currentLineNode.version + \
        #     "], parent is ["+currentLineNode.parent.name + \
        #     currentLineNode.parent.version+"]"
        # s1 = ""
        # for c in currentLineNode.parent.children:
        #     s1 += " "+c.name+c.version
        # print "siblings are : "+s1
        lastLineRoutes.append(currentLineNode)
        lastLineIndent = cIndent
    return root


# 找出两个 tree 里的区别 tree
def findDiffCommonSubTree(root1, root2):
    # todo 暂时不实现输出差异树的功能，看之后的
    return


def verifyPrint(node, spaceNum):
    str = ""
    for i in range(spaceNum):
        str += " "
    print str+node.name+" "+node.version
    for c in node.children:
        verifyPrint(c, spaceNum+4)
    return

"""

