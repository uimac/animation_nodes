'''
Copyright (C) 2017 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


bl_info = {
    "name":        "Animation Nodes",
    "description": "Node based visual scripting system designed for motion graphics in Blender.",
    "author":      "Jacques Lucke, Omar Emara",
    "version":     (2, 2, 2),
    "blender":     (2, 93, 0),
    "location":    "Animation Nodes Editor",
    "category":    "Node",
    "warning":     "This version is still in development."
}



# Test Environment
##################################

import os
import sys
import traceback
import bpy
from bpy.app.handlers import persistent
from os.path import dirname, join, abspath, basename
currentDirectory = dirname(abspath(__file__))
addonsDirectory = dirname(currentDirectory)
compilationInfoPath = join(currentDirectory, "compilation_info.json")
addonName = basename(currentDirectory)


if addonName != "animation_nodes":
    message = ("\n\n"
        "The name of the folder containing this addon has to be 'animation_nodes'.\n"
        "Please rename it.")
    raise Exception(message)


counter = 0
for name in os.listdir(addonsDirectory):
    name = name.lower()
    if "animation" in name and "nodes" in name and not "test" in name:
        counter += 1

if counter > 1:
    message = ("\n\n"
        "There are multiple versions of the Animation Nodes addon installed.\n"
        "Please uninstall/remove all older versions of the addon.\n\n"
        "Animation Nodes has been found more than once in this folder:\n"
        "  {}").format(addonsDirectory)
    raise Exception(message)


try: from . import auto_load
except: pass

if "auto_load" not in globals():
    message = ("\n\n"
        "The Animation Nodes addon cannot be registered correctly.\n"
        "Please try to remove and install it again.\n"
        "If it still does not work, report it.\n")
    raise Exception(message)


try: import numpy
except: pass

if "numpy" not in globals():
    message = ("\n\n"
        "The Animation Nodes addon depends on the numpy library.\n"
        "Unfortunately the Blender built you are using does not have this library.\n"
        "You can either install numpy manually or use another Blender version\n"
        "that comes with numpy (e.g. the newest official Blender release).")
    raise Exception(message)


from . preferences import getBlenderVersion
if getBlenderVersion() < (2, 93, 0):
    message = ("\n\n"
        "The Animation Nodes addon requires at least Blender 2.93.\n"
        "Your are using an older version.\n"
        "Please download the latest official release.")
    raise Exception(message)


if not os.path.isfile(compilationInfoPath):
    message = ("\n\n"
        "This is just the source code of Animation Nodes, not a compiled build.\n"
        "Please download a build for your operating system instead.\n"
        "Don't forget to remove this version at first.")
    raise Exception(message)

import json
with open(compilationInfoPath) as f:
    compilation_info = json.load(f)

if compilation_info["sys.platform"] != sys.platform:
    message = ("\n\n"
        "This Animation Nodes build is for another OS.\n\n"
        "You are using: {}\n"
        "This build is for: {}\n\n"
        "Please download a build for your operating system."
        ).format(sys.platform, compilation_info["sys.platform"])
    raise Exception(message)

currentPythonVersion = tuple(sys.version_info[:3])
addonPythonVersion = tuple(compilation_info["sys.version_info"][:3])

if currentPythonVersion[:2] != addonPythonVersion[:2]:
    message = ("\n\n"
        "There is a Python version mismatch.\n\n"
        "Your Blender build uses: {}\n"
        "Animation Nodes has been compiled for: {}\n\n"
        "You have three options:\n"
        "  1. Try to make Blender use another Python version.\n"
        "     (Blender 2.93 officially uses Python 3.9.x)\n"
        "  2. Compile Animation Nodes yourself using the correct Python version.\n"
        "     (Look in the developer manual for more information)\n"
        "  3. Create an issue on Github and ask if someone can create a build for you."
        ).format(currentPythonVersion, addonPythonVersion)
    raise Exception(message)


try: from . import test_compile
except: traceback.print_exc()

if "test_compile" not in globals():
    message = ("\n\n"
        "This build does not work at the moment.\n"
        "  1. Check if the build you downloaded has been compiled for the OS\n"
        "     you are using. If not, download another one.\n"
        "  2. If you are on windows you can try to install a library called\n"
        "     'vc_redist.x64'. Should be easy to find using your search engine\n"
        "     of choice.\n"
        "  3. Try to use an official Blender release downloaded from blender.org.\n"
        "  4. It is possible that you have a build for the correct platform\n"
        "     but it still does not work. We experienced this mainly on linux.\n"
        "     Try to find another build for your platform.\n"
        "     If it still does not work, you have to compile AN yourself.\n"
        "  5. Make a bug report on Github and give as much information\n"
        "     as you can. Specifically the full error message, your OS, version, ...")
    raise Exception(message)



# register
##################################

def eval_curves(tree, curves):
    from bpy.app import driver_namespace
    for x in driver_namespace:
        locals()[x] = driver_namespace[x]

    for curve in curves:
        if curve.data_path.endswith(".value"):
            socket = curve.data_path.removesuffix(".value")

            if curve.driver != None:
                frame = bpy.context.scene.frame_current
                v = eval(curve.driver.expression)
            else:
                # evaluate fcurve at current frame
                v = curve.evaluate(bpy.context.scene.frame_current)
            data = eval("tree." + curve.data_path)
            # overwrite if changed
            if hasattr(data, "__getitem__"):
                if data[curve.array_index] != v:
                    data[curve.array_index] = v
            else:
                soc = eval("tree." + socket)
                if soc.value != v:
                    soc.value = v

@persistent
def animation_handler(scene):
    for tree in bpy.data.node_groups:
        if tree.bl_idname == "an_AnimationNodeTree":
            if (tree.animation_data != None):
                if tree.animation_data.action != None:
                    eval_curves(tree, tree.animation_data.action.fcurves)
                if tree.animation_data.drivers != None:
                    eval_curves(tree, tree.animation_data.drivers)

@persistent
def load_handler(dummy):
    if animation_handler not in bpy.app.handlers.frame_change_pre:
        print("add animation_handler")
        bpy.app.handlers.frame_change_pre.append(animation_handler)

##################################

from . import auto_load
auto_load.init()

from . sockets.info import updateSocketInfo
updateSocketInfo()

def register():
    auto_load.register()

    if not hasattr(bpy.data, "node_groups"):
        bpy.app.handlers.load_post.append(load_handler)

    print("Registered Animation Nodes")

def unregister():
    auto_load.unregister()

    if load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_handler)

    if animation_handler in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(animation_handler)

    print("Unregistered Animation Nodes")
