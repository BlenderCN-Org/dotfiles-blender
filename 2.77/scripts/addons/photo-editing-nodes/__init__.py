# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Photo Editing Nodes",
    "author": "Akash Hamirwasia",
    "version": (3, 2),
    "blender": (2, 77, 0),
    "location": "NodeEditor > Compositor Node Tree",
    "description": "Get the most out of Blender's compositor with Photo Editing Designed nodes!",
    "warning": "",
    "wiki_url": "http://www.blenderskool.cf",
    "tracker_url": "",
    "category": "Node"}

import bpy
import os
from bpy.app.handlers import persistent

@persistent
def load_nodes(self):
    bpy.app.handlers.scene_update_pre.remove(load_nodes)
    opath = "//Photo_Editing_Nodes.blend\\NodeTree\\"
    nodname1 = "Film Grain"
    nodname2 = "Quick Fix"
    nodname3 = "Quick Pixelate"
    nodname4 = "Bloom"
    nodname5 = "Vignette"
    nodname6 = "Focus"
    nodname7 = "Temperature"
    nodname8 = "Photo Frame"
    nodname9 = "Quick Tint"
    nodname10 = "Change Colors"
    nodname11 = "Collage"
    nodname12 = "Sketch"
    nodname13 = "Dirty Lens"
    nodname14 = "Bar Blur"
    dpath = os.path.join(os.path.dirname(__file__), "blend")+"\\Photo_Editing_Nodes.blend\\NodeTree\\"
    bpy.ops.wm.append(filepath=opath,filename=nodname2,directory=dpath,link=False,autoselect=False, set_fake=False)
    bpy.ops.wm.append(filepath=opath,filename=nodname1,directory=dpath,link=False,autoselect=False, set_fake=False)
    bpy.ops.wm.append(filepath=opath,filename=nodname3,directory=dpath,link=False,autoselect=False, set_fake=False)
    bpy.ops.wm.append(filepath=opath,filename=nodname4,directory=dpath,link=False,autoselect=False, set_fake=False)
    #bpy.ops.wm.link(filepath=opath,filename=nodname5,directory=dpath,link=False,autoselect=False, set_fake=False)
    bpy.ops.wm.append(filepath=opath,filename=nodname6,directory=dpath,link=False,autoselect=False, set_fake=False)
    bpy.ops.wm.append(filepath=opath,filename=nodname7,directory=dpath,link=False,autoselect=False, set_fake=False)
    bpy.ops.wm.append(filepath=opath,filename=nodname8,directory=dpath,link=False,autoselect=False, set_fake=False)
    bpy.ops.wm.append(filepath=opath,filename=nodname9,directory=dpath,link=False,autoselect=False, set_fake=False)
    bpy.ops.wm.append(filepath=opath,filename=nodname10,directory=dpath,link=False,autoselect=False, set_fake=False)
    bpy.ops.wm.append(filepath=opath,filename=nodname11,directory=dpath,link=False,autoselect=False, set_fake=False)
    bpy.ops.wm.append(filepath=opath,filename=nodname12,directory=dpath,link=False,autoselect=False, set_fake=False)
    bpy.ops.wm.append(filepath=opath,filename=nodname13,directory=dpath,link=False,autoselect=False, set_fake=False)
    bpy.ops.wm.append(filepath=opath,filename=nodname14,directory=dpath,link=False,autoselect=False, set_fake=False)

def register():
    bpy.app.handlers.scene_update_pre.append(load_nodes)

def unregister():
    pass

if __name__ == "__main__":
    register()
