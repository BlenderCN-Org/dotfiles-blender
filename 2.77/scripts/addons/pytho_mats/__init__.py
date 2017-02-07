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
    "name": "Pytho Mats - Fog Material",
    "author": "Akash Hamirwasia",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "Properties > Materials > Fog Material Panel",
    "description": "Creates a Fog Material in Cycles which is easily customizable",
    "warning": "",
    "wiki_url": "http://www.blenderskool.cf/contact",
    "tracker_url": "http://www.blenderskool.cf/contact",
    "category": "Material"}

import bpy
import os
from bpy.props import IntProperty, FloatProperty, FloatVectorProperty, EnumProperty, StringProperty, PointerProperty

class PythoMatsPanel(bpy.types.Panel):   #Fog Material Panel
    """FogMaterialPanel"""
    bl_idname = "MATERIAL_PT_fog_material"
    bl_label = "Fog Material Panel"

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    def draw(self, context):
        pytho_mats = bpy.context.object
        try:
            pytho_mats = bpy.context.object.active_material.pytho_mats
        except:
            pytho_mats = bpy.context.object
        layout = self.layout
        inde = 0
        try:
            for node in bpy.context.object.active_material.node_tree.nodes:
                if node.name == "Fog_Material":
                    inde = 1
        except:
            inde=0
        if bpy.context.object.active_material_index != None:  #Check the active object's material Slots
            if bpy.context.object.active_material != None: #If the Material slot has some material
                if inde==1:  #Check the name of node of the Material in the Material Slot
                    box1 = layout.box()
                    col = box1.column(align=True)
                    col.label("Basic Settings", icon="SMOOTH")  #Basic Settings Box
                    col.label()
                    row = col.row()
                    row.label("Glass Color:")  #Glass Color
                    row.prop(pytho_mats, "shader_color", text="")
                    row1 = col.row()
                    row1.label("Image to Cut:")   #Image To Cut
                    row1.prop_search(pytho_mats, "image_string", bpy.data,"images", text="",icon='FORCE_TEXTURE')
                    col.prop(pytho_mats, "CoordinatesType", text="Coordinates")  #Coordinates Menu
                    col.prop(pytho_mats, "ShaderType", text="Shader")   #ShaderType Menu
                    col1_1 = box1.column()   #Particle Settings Interface
                    if pytho_mats.particle_bool == 0:
                        col1_1.operator(AddDroplets.bl_idname, text="Create Droplets", icon="MOD_PARTICLES")
                    elif pytho_mats.particle_bool == 1:
                        col1_1.operator(UnHideDroplets.bl_idname, text="Show Droplets", icon="RESTRICT_RENDER_OFF")
                    elif pytho_mats.particle_bool == 2:
                        row1_1 = col1_1.row(align=True)
                        row1_1.operator(HideDroplets.bl_idname, text="Hide Droplets", icon="RESTRICT_RENDER_ON")
                        row1_1.operator(LoadParticleScreen.bl_idname, text="", icon="UI")

                    box2 = layout.box()
                    col2 = box2.column(align=True)
                    col2.label("Fog Settings", icon="MOD_FLUIDSIM")   #Fog Settings
                    col2.label()
                    col2.prop(pytho_mats, "texture_stre", text="Condensation Strength", slider=True)  #Condensation Settings
                    col2.prop(pytho_mats, "disp_stre", text="Displacement")   #Displacement Settings
                    if pytho_mats.ShaderType == "1":
                        col2.prop(pytho_mats, "glass_ior", text="IOR Value")   #Glass IOR Value
                else:
                    col = layout.column()
                    col.operator(NodeAppend.bl_idname, text="Create Fog Material")
            else:
                col = layout.column()
                col.operator(NodeAppend.bl_idname, text="Create Fog Material")
        else:
            col = layout.column()
            col.operator(NodeAppend.bl_idname, text="Create Fog Material")
        cols = layout.column()
        split = cols.split(percentage=0.75)
        cols1 = split.column(align=True)
        cols1.label("Created by Akash Hamirwasia")   #Credits
        cols2 = split.column()
        cols2.operator('wm.url_open',text="Donate", icon ='SOLO_ON').url = 'https://gum.co/quRPN'

class PythoMatsProp(bpy.types.PropertyGroup):
    def set_glass_ior(self, context):    #Update Glass IOR
        pytho_mats = bpy.context.object.active_material.pytho_mats
        for node in bpy.context.object.active_material.node_tree.nodes:
            if node.name == "Fog_Material":
                node.inputs[3].default_value = pytho_mats.glass_ior
        return None
    def set_displace(self, context):    #Update Displacement Strength
        pytho_mats = bpy.context.object.active_material.pytho_mats
        for node in bpy.context.object.active_material.node_tree.nodes:
            if node.name == "Fog_Material":
                node.inputs[6].default_value = pytho_mats.disp_stre
        return None
    def tex_stre(self, context):     #Update Texture Strength
        pytho_mats = bpy.context.object.active_material.pytho_mats
        for node in bpy.context.object.active_material.node_tree.nodes:
            if node.name == "Fog_Material":
                node.inputs[2].default_value = pytho_mats.texture_stre
        return None
    def set_shader_color(self, context):   #Update Glass Color
        pytho_mats = bpy.context.object.active_material.pytho_mats
        for node in bpy.context.object.active_material.node_tree.nodes:
            if node.name == "Fog_Material":
                node.inputs[0].default_value = pytho_mats.shader_color
        return None
    def set_image(self, context):    #Update Image to Cut out
        pytho_mats = bpy.context.object.active_material.pytho_mats
        node_check=0
        for node in bpy.context.object.active_material.node_tree.nodes:
            if node.name != "Image Texture":
                node_check=0
            else:
                node_check=1
        if node_check == 0:
            fog_node = 0
            for node in bpy.context.object.active_material.node_tree.nodes:
                if node.name == "Fog_Material":
                    fog_node = 1
            img = bpy.context.object.active_material.node_tree.nodes.new(type="ShaderNodeTexImage")
            img.name = "Image Texture"
            img.location = -296.337, 300.333
            if fog_node == 1:
                bpy.context.object.active_material.node_tree.links.new(bpy.context.object.active_material.node_tree.nodes['Fog_Material'].inputs[1], img.outputs[0])
        for node in bpy.context.object.active_material.node_tree.nodes:
            if node.name == "Image Texture":
                if pytho_mats.image_string=="":  #If Image is None
                    bpy.context.object.active_material.node_tree.nodes['Image Texture'].image = None

                else:
                    if "\\" in pytho_mats.image_string:  #If image is loaded externally
                        sl = "\\";
                        ch = pytho_mats.image_string.rfind(sl)
                        img = pytho_mats.image_string[ch:]
                        path = pytho_mats.image_string
                        pytho_mats.image_string = img[1:] # File name is extracted out from the File path
                        if pytho_mats.image_string in bpy.data.images: #Checks if the Image is already loaded in Blender
                            bpy.context.object.active_material.node_tree.nodes['Image Texture'].image = bpy.data.images[pytho_mats.image_string]
                             #If image is already there in Blender, set that image, and dont load the same image
                        else: # If Image is not loaded in Blender, Load the Image from the Path provided
                            bpy.context.object.active_material.node_tree.nodes['Image Texture'].image = bpy.data.images.load(path)
                    else:
                        if pytho_mats.image_string in bpy.data.images:
                            bpy.context.object.active_material.node_tree.nodes['Image Texture'].image = bpy.data.images[pytho_mats.image_string]
                             #If image is already there in Blender, set that image, and dont load the same image
        return None
    def set_coords(self, context):    #Update Coordinates Type
        pytho_mats = bpy.context.object.active_material.pytho_mats
        for node in bpy.context.object.active_material.node_tree.nodes:
            if node.name == "Fog_Material":
                if pytho_mats.CoordinatesType == "0":
                    node.inputs[4].default_value = 0
                else:
                    node.inputs[4].default_value = 1
        return None
    def set_shader(self, context):     #Update Shader Type
        pytho_mats = bpy.context.object.active_material.pytho_mats
        for node in bpy.context.object.active_material.node_tree.nodes:
            if node.name == "Fog_Material":
                if pytho_mats.ShaderType == "0":
                    node.inputs[5].default_value = 0
                else:
                    node.inputs[5].default_value = 1
        return None

    #Properties
    particle_bool = IntProperty(name="Check Particles", description="", default=0)
    glass_ior = FloatProperty(name="Glass IOR", description="Control the IOR of the Glass Shader", default=1.45, min=0.0, max=1000.0, update=set_glass_ior)
    disp_stre = FloatProperty(name="Displacement Strength", description="Control the Strength of the Displacement of Fog", default=0.005, min=0.0, max=1000.0, update=set_displace)
    texture_stre = FloatProperty(name="Texture Strength", description="Control the Strength of Roughness from the Textures", default=1.3, min=0.0, max=10.0, update=tex_stre)
    shader_color = FloatVectorProperty(name="Shader Color", description="Change the color of the Shader", subtype="COLOR", size=4, min=0.0, max=1.0, default=(1.0, 1.0, 1.0, 1.0), update=set_shader_color)
    image_string = StringProperty(name="Cut Image", description="Choose the image to cut it from fog", default="", subtype='FILE_PATH', update=set_image)
    CoordinatesType = EnumProperty(items = [('0', 'UV', 'Use UV Coordinates'),
                                            ('1', 'Generated', 'Use Generated Coordinates')],
                               name="Choose Coordinates",
                               description="Set the Coordinates to use for the material",
                               default="0", update=set_coords)
    ShaderType = EnumProperty(items = [('0', 'Glossy BSDF', 'Use Glossy Shader'),
                                       ('1', 'Glass BSDF', 'Use Glass Shader')],
                               name="Choose Shader",
                               description="Set the Shader to use for the material",
                               default="0", update=set_shader)

class NodeAppend(bpy.types.Operator):   #Create the Material
    """Create the Fog Material for current object"""
    bl_idname="pytho_mats.gen"
    bl_label="Node Generator"

    def execute(self, context):
        if bpy.context.scene.render.engine != 'CYCLES':
            bpy.context.scene.render.engine = 'CYCLES'
        mate =  bpy.data.materials.new('Fog_Material_'+bpy.context.active_object.name) #Name of Material Set
        mate.use_nodes = True
        bpy.context.object.active_material = mate
        obj_check = 0
        for obj in bpy.context.scene.objects:
            if obj.name == "Fog Material Text":     #Not to append the Group again if it is alreay loaded
                obj_check = 1
        if obj_check == 0:
            name = "APPEND - Fog Material" #Append the Fog Material Node
            opath = "/Fog_Material.blend\\Group\\"
            dpath = os.path.join(os.path.dirname(__file__), "blend")+"/Fog_Material.blend\\Group"
            bpy.ops.wm.link(filepath=opath,filename=name,directory=dpath,filemode=1,link=False,autoselect=False,active_layer=False,instance_groups=False,relative_path=True)
        fog = bpy.context.object.active_material.node_tree.nodes.new("ShaderNodeGroup")
        fog.node_tree = bpy.data.node_groups['Fog_Material']
        fog.name = "Fog_Material"
        fog.location = bpy.context.object.active_material.node_tree.nodes['Diffuse BSDF'].location
        for node in bpy.context.object.active_material.node_tree.nodes:
            if node.name == "Diffuse BSDF":
                bpy.context.object.active_material.node_tree.nodes.remove(node)
        bpy.context.object.active_material.node_tree.links.new(bpy.context.object.active_material.node_tree.nodes['Material Output'].inputs[0], fog.outputs[0])
        bpy.context.object.active_material.node_tree.links.new(bpy.context.object.active_material.node_tree.nodes['Material Output'].inputs[2], fog.outputs[1])
        return {'FINISHED'}

class AddDroplets(bpy.types.Operator):    #Create Droplets Particle System
    """Create a Particle System with Droplets"""
    bl_idname="pytho_mats.add_droplets"
    bl_label="Add Droplets"

    def execute(self, context):
        pytho_mats = bpy.context.object.active_material.pytho_mats
        if "Droplets" in bpy.data.particles:
            obj = bpy.context.active_object #get object
            part = bpy.context.active_object.modifiers.new("Droplets", "PARTICLE_SYSTEM")
            obj.particle_systems[-1].settings = bpy.data.particles['Droplets']
            obj.particle_systems[-1].name = "Droplets"
            pytho_mats.particle_bool = 2
        return {'FINISHED'}

class HideDroplets(bpy.types.Operator):    #Hide Droplets
    """Hide the Particle Settings with Droplets"""
    bl_idname="pytho_mats.remove_droplets"
    bl_label = "Hide Droplets"

    def execute(self, context):
        pytho_mats = bpy.context.object.active_material.pytho_mats
        if "Droplets" in bpy.context.active_object.particle_systems:
            bpy.context.active_object.modifiers['Droplets'].show_viewport = False
            bpy.context.active_object.modifiers['Droplets'].show_render = False
            pytho_mats.particle_bool = 1
        return {'FINISHED'}

class UnHideDroplets(bpy.types.Operator):    #UnHide Droplets
    """Show the Droplets Particle System"""
    bl_idname="pytho_mats.unhide_droplets"
    bl_label="Un-hide Droplets"

    def execute(self, context):
        pytho_mats = bpy.context.object.active_material.pytho_mats
        if "Droplets" in bpy.context.active_object.particle_systems:
            bpy.context.active_object.modifiers['Droplets'].show_viewport = True
            bpy.context.active_object.modifiers['Droplets'].show_render = True
            pytho_mats.particle_bool = 2
        return {'FINISHED'}

class LoadParticleScreen(bpy.types.Operator):  #Jump to Particle Settings Tab
    """View the Particle Settings"""
    bl_idname="pyhto_mats.load_particle_screen"
    bl_label= "View Particle Screen"

    def execute(self, context):
        bpy.context.space_data.context = 'PARTICLES'
        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Material.pytho_mats = PointerProperty(type = PythoMatsProp)

def unregister():
    del bpy.types.Material.pytho_mats
    bpy.utils.unregister_module(__name__)
