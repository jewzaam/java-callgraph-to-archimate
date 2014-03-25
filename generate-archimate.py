#!/usr/bin/python

# Copyright (C) 2014 Naveen Malik
#
# java-callback-to-archimate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# java-callback-to-archimate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with java-callback-to-archimate.  If not, see <http://www.gnu.org/licenses/>.

import json
import sys
import hashlib

# VERY much a work in progress

f=open('analysis.json', 'r')
obj=json.load(f)

packages=[]
functions={}
services={}
components={}
realizes={}
usedby={}
        
for x in range(0, len(obj)):
    if "class" in obj[x] and "method" in obj[x]:
        # assign some hashes in one place
        obj[x]["name"]=(obj[x]["class"]+"#"+obj[x]["method"]+"("+obj[x]["args"]+")").replace("<","&lt;").replace(">","&gt;")
        m=hashlib.md5()
        m.update(obj[x]["package"]+"."+obj[x]["name"])
        obj[x]["id"]=m.hexdigest()

        packages.append(obj[x]["package"])

        # service (source) id is from package.class
        m=hashlib.md5()
        m.update(obj[x]["package"]+"."+obj[x]["class"])
        source=m.hexdigest()
        # handle interface (class with no invoke)
        if "invoke" not in obj[x]:
            services.update({source:obj[x]})
            # function (target) id is id on object
            target=obj[x]["id"]
            functions.update({target:obj[x]})
            # realizes id is from sourceId[service]#targetId[function]
            m=hashlib.md5()
            m.update(source+"#"+target)
            rId=m.hexdigest()
            realizes.update({rId:dict(source=source,target=target,type="service")})

        # handle invoke
        if "invoke" in obj[x]:
            components.update({source:obj[x]})
            obj[x]["invoke"]["name"]=(obj[x]["invoke"]["class"]+"#"+obj[x]["invoke"]["method"]+"("+obj[x]["invoke"]["args"]+")").replace("<","&lt;").replace(">","&gt;")
            m=hashlib.md5()
            m.update(obj[x]["invoke"]["name"])
            obj[x]["invoke"]["id"]=m.hexdigest()
            # component (source) id is from package.class
            m=hashlib.md5()
            # TODO need to break this out as a python function, add a package/class/method/args to the data set.. am not setting up functions correctly here!
            m.update(obj[x]["invoke"]["package"]+"."+obj[x]["invoke"]["class"])
            source=m.hexdigest()
            packages.append(obj[x]["invoke"]["package"])
            components.update({source:obj[x]["invoke"]})
            # function (target) id is id on object
            target=obj[x]["invoke"]["id"]
            functions.update({target:obj[x]["invoke"]})
            # realizes id is from sourceId[component]#targetId[function]
            m=hashlib.md5()
            m.update(source+"#"+target)
            rId=m.hexdigest()
            realizes.update({rId:dict(source=source,target=target,type="component")})
            # usedby id is from function[target]#objectId[non-invoke]
            m=hashlib.md5()
            m.update(target+"#"+obj[x]["id"])
            uId=m.hexdigest()
            usedby.update({uId:dict(source=target,target=obj[x]["id"])})

print '<?xml version="1.0" encoding="UTF-8"?>'
print '<archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:archimate="http://www.archimatetool.com/archimate" name="legacy" id="8c1ddd6a" version="2.6.0">'
print '  <folder name="Business" id="a195f621" type="business"/>'
print '  <folder name="Web Applications" id="a195f621x" type="application"/>'
print '  <folder name="Legacy Services" id="70cd34b2" type="application">'

# make things sets that need to be distinct
packages=list(set(packages))
serviceIds=list(set(services.keys()))
componentIds=list(set(components.keys()))
functionIds=list(set(functions.keys()))
realizeIds=list(set(realizes.keys()))
usedbyIds=list(set(usedby.keys()))

for p in range(0, len(packages)):
    print '    <folder name="' + packages[p] + '">'
    for id in serviceIds:
        service=services[id]
        if packages[p] == service["package"]:
            print '    <element xsi:type="archimate:ApplicationService" id="' + id + '" name="' + service["class"] + '"/>'

    for id in componentIds:
        component=components[id]
        if packages[p] == component["package"]:
            print '    <element xsi:type="archimate:ApplicationComponent" id="' + id + '" name="' + component["class"] + '"/>'

    for id in functionIds:
        function=functions[id]
        if packages[p] == function["package"]:
            print '    <element xsi:type="archimate:ApplicationFunction" id="' + id + '" name="' + function["name"] + '"/>'

    print '    </folder>'

print '  </folder>'
print '  <folder name="Technology" id="2b2d58f2" type="technology"/>'
print '  <folder name="Motivation" id="677d1802" type="motivation"/>'
print '  <folder name="Implementation &amp; Migration" id="16a92d2a" type="implementation_migration"/>'
print '  <folder name="Connectors" id="ecc563b9" type="connectors"/>'
print '  <folder name="Relations" id="18335b5f" type="relations">'

for id in realizeIds:
    realize=realizes[id]
    print '      <element xsi:type="archimate:RealisationRelationship" id="' + id + '" source="' + realize["source"] + '" target="' + realize["target"] + '"/>'

for id in usedbyIds:
    ub=usedby[id]
    print '      <element xsi:type="archimate:UsedByRelationship" id="' + id + '" source="' + ub["source"] + '" target="' + ub["target"] + '"/>'

print '  </folder>'
print '  <folder name="Views" id="4d9950a3" type="diagrams"/>'
print '</archimate:model>'
