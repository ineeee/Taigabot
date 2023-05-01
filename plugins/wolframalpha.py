import random
import re
from xml.dom import minidom

from utilities import request
from util import hook

API_URL = 'http://api.wolframalpha.com/v2/query.jsp'

# sorry bro i modified ur stuff to make it work with this bot in python 3.10
#
# Copyright 2009 Derik Pereira. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''A library that provides a python interface to the Wolfram|Alpha API'''

__author__ = 'derik66@gmail.com'
__version__ = '1.1-devel'


class WolframAlphaQueryResult:
    def __init__(self, result=''):
        self.XmlResult = result
        self.dom = minidom.parseString(result)  # TODO fix
        self.tree = runtree(self.dom.documentElement)

    def JsonResult(self):
        return ''  # json.dumps(self.tree)

    def IsSuccess(self):
        return scanbranches(self.tree, 'success')

    def IsError(self):
        try:
            return [scanbranches(self.tree, 'error')[0]]
        except:
            return scanbranches(self.tree, 'error')

    def NumPods(self):
        return scanbranches(self.tree, 'numpods')

    def DataTypes(self):
        return scanbranches(self.tree, 'datatypes')

    def TimedoutScanners(self):
        return scanbranches(self.tree, 'timedout')

    def Timing(self):
        return scanbranches(self.tree, 'timing')

    def ParseTiming(self):
        return scanbranches(self.tree, 'parsetiming')

    def Error(self):
        try:
            return scanbranches(self.tree, 'error')[1]
        except:
            return []

    def ErrorCode(self):
        try:
            return [scanbranches(self.Error(), 'code')[0]]
        except:
            return []

    def ErrorMessage(self):
        try:
            return [scanbranches(self.Error(), 'msg')[0]]
        except:
            return []

    def Pods(self):
        return scanbranches(self.tree, 'pod')

    def XMLPods(self):
        return asxml(self.dom, 'pod')

    def Assumptions(self):
        assumptions = scanbranches(self.tree, 'assumptions')
        try:
            return scanbranches(assumptions[0], 'assumption')
        except:
            return []

    def Warnings(self):
        return scanbranches(self.tree, 'warnings')

    def Sources(self):
        return scanbranches(self.tree, 'sources')


class Pod:
    def __init__(self, pod=''):
        self.pod = pod
        return

    def IsError(self):
        return scanbranches(self.pod, 'error')

    def NumSubpods(self):
        return scanbranches(self.pod, 'numsubpods')

    def Title(self):
        return scanbranches(self.pod, 'title')

    def Scanner(self):
        return scanbranches(self.pod, 'scanner')

    def Position(self):
        return scanbranches(self.pod, 'position')

    def AsynchURL(self):
        return scanbranches(self.pod, 'asynchurl')

    def Subpods(self):
        return scanbranches(self.pod, 'subpod')

    def PodStates(self):
        return scanbranches(self.pod, 'states')

    def Infos(self):
        return scanbranches(self.pod, 'infos')

    def AsXML(self):
        return self.pod


class Subpod:
    def __init__(self, subpod=''):
        self.subpod = subpod
        return

    def Title(self):
        return scanbranches(self.subpod, 'title')

    def Plaintext(self):
        return scanbranches(self.subpod, 'plaintext')

    def Img(self):
        return scanbranches(self.subpod, 'img')


class Assumption:
    def __init__(self, assumption=''):
        self.assumption = assumption
        return

    def Type(self):
        return scanbranches(self.assumption, 'type')

    def Word(self):
        return scanbranches(self.assumption, 'word')

    def Count(self):
        return scanbranches(self.assumption, 'count')

    def Value(self):
        return scanbranches(self.assumption, 'value')


def runtree(node):
    tree = []
    if node.nodeType != node.TEXT_NODE:
        tree = [node.nodeName]
        for index in range(node.attributes.length):
            attr = node.attributes.item(index)
            tree = tree + [(attr.nodeName, attr.nodeValue)]
    for child in node.childNodes:
        if child.nodeType != child.TEXT_NODE:
            tree = tree + [runtree(child)]
        else:
            if child.data[0] != '\n':
                tree = child.parentNode.nodeName, child.data
    return tree


def scanbranches(tree, name):
    branches = []
    for branch in tree:
        if branch[0] == name:
            if type(branch) == type(('', '')):
                branches = branches + [branch[1]]
            else:
                branches = branches + [branch[1:]]
    return branches


def asxml(dom, name):
    xml = []
    for child in dom.documentElement.childNodes:
        if child.nodeName == name:
            xml = xml + [child.toxml()]
    return xml


errors = [
    "I don't know.",
    'Try again later.',
    'I have no idea.',
    "You're better off asking someone else.",
]


@hook.command('convert')
@hook.command('wa')
@hook.command
def wolframalpha(inp, bot):
    """wa <query> -- Computes <query> using Wolfram Alpha."""
    api_key = bot.get_api_key('wolframalpha')

    if not api_key:
        return '[WolframAlpha] Error: missing API key'

    query_params = {
        'scantimeout': '3.0',
        'podtimeout': '4.0',
        'formattimeout': '8.0',
        'parsetimeout': '5.0',
        'totaltimeout': '20.0',
        'async': 'true',

        'format': 'plaintext',
        'output': 'xml',
        'appid': api_key,
        'input': inp
    }

    req = request.post(API_URL, data=query_params)

    try:
        waeqr = WolframAlphaQueryResult(req)
    except Exception:
        return '[WolframAlpha] Error while parsing response'

    results = []
    pods = waeqr.Pods()
    for pod in pods:
        waep = Pod(pod)
        subpods = waep.Subpods()
        for subpod in subpods:
            waesp = Subpod(subpod)
            plaintext = waesp.Plaintext()
            results.append(plaintext)

    try:
        # TODO clean this
        waquery = re.sub(r' (?:\||) +', ' ', ' '.join(results[0][0].splitlines())).strip().replace(u'\xc2 ', '')
        if results[1][0] == [] or 'irreducible' in results[1][0]:
            waresult = ' '.join(results[2][0].splitlines()).replace(u'\xc2 ', '')
        else:
            waresult = ' '.join(results[1][0].splitlines()).replace(u'\xc2 ', '')
        return f'[WolframAlpha] {waquery} = {waresult}'
    except Exception:
        return f'[WolframAlpha] {random.choice(errors)}'
