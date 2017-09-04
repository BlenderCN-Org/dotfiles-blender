#ManuelbastioniLAB - Copyright (C) 2016 Manuel Bastioni
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import array
import bpy
import os
import time
import logging
from . import algorithms
lab_logger = logging.getLogger('manuelbastionilab_logger')
class MaterialEngine:

    def __init__(self, obj, data_path):
        time1 = time.time()
        if obj:
            self.obj_name = obj.name
            self.texture_database_exist = False
            self.filename_disp = obj.name[:len(obj.name)-2]+"_displace.png"
            self.filename_derm = obj.name[:len(obj.name)-2]+"_dermal.png"
            self.filename_subderm = obj.name[:len(obj.name)-2]+"_subdermal.png"
            self.filename_complexion = obj.name[:len(obj.name)-2]+"_complexion.png"

            self.skin_mat_name = obj.name[:len(obj.name)-3]+"_skin"
            self.eye_mat_name = obj.name[:len(obj.name)-3]+"_eyes"

            self.skin_node_dermal_texture = obj.name[:len(obj.name)-3]+"_tex_derm"
            self.skin_node_subdermal_texture = obj.name[:len(obj.name)-3]+"_tex_subderm"
            self.skin_node_complexion_texture = obj.name[:len(obj.name)-3]+"_tex_complexion"
            self.skin_node_displacement_texture = obj.name[:len(obj.name)-3]+"_tex_displ"
            self.skin_node_eyeball_texture = obj.name[:len(obj.name)-3]+"_tex_eyes"


            self.displace_data_path = os.path.join(
                data_path,
                "shared_textures",
                self.filename_disp)

            self.dermal_texture_path = os.path.join(
                data_path,
                "shared_textures",
                self.filename_derm)

            self.subdermal_texture_path = os.path.join(
                data_path,
                "shared_textures",
                self.filename_subderm)

            self.complexion_texture_path = os.path.join(
                data_path,
                "shared_textures",
                self.filename_complexion)

            self.load_data_images()

            if hasattr(obj, 'character_ID'):
                self.material_ID = obj.character_ID
            else:
                lab_logger.error("The object has not character ID")
            self.generated_disp_image_name = self.material_ID+"_disp.png"
            self.generated_disp_modifier_ID = "displ_mod_"+self.material_ID
            self.generated_disp_texture_name = "displ_tex_"+self.material_ID
            self.subdivision_modifier_name = "subs_mod_"+self.material_ID

            self.material_names = [self.skin_mat_name,self.eye_mat_name]


    def load_data_images(self):

        img_paths = [self.displace_data_path,self.dermal_texture_path,self.subdermal_texture_path,self.complexion_texture_path]
        self.texture_database_exist = True
        for img_path in img_paths:
            if os.path.exists(img_path):
                img_block_already_in_scene = False
                for img in bpy.data.images:
                    if img.source == "FILE":
                        if os.path.basename(img_path) == img.name:
                            img.filepath = img_path
                            img_block_already_in_scene = True
                            lab_logger.info("Using existing image: {0}".format(img.name))

                if not img_block_already_in_scene:
                    bpy.data.images.load(img_path, check_existing=True)
                    lab_logger.info("Loading image: {0}".format(algorithms.simple_path(img_path)))
            else:
                self.texture_database_exist = False
                lab_logger.warning("Image not found: {0}".format(algorithms.simple_path(img_path)))


    def image_to_array(self, blender_image):
        return array.array('f',blender_image.pixels[:])

    def calculate_disp_pixels(self, blender_image, age_factor,tone_factor,mass_factor):

        source_data_image = self.image_to_array(blender_image)
        result_image= array.array('f')

        if age_factor > 0:
            age_f = age_factor
        else:
            age_f = 0

        if tone_factor > 0:
            tone_f = tone_factor
        else:
            tone_f = 0

        if mass_factor > 0:
            mass_f = (1-tone_f)*mass_factor
        else:
            mass_f = 0

        for i in range(0,len(source_data_image),4):
            r = source_data_image[i]
            g = source_data_image[i+1]
            b = source_data_image[i+2]
            a = source_data_image[i+3]

            details = r
            age_disp = age_f*(g-0.5)
            tone_disp = tone_f*(b-0.5)
            mass_disp = mass_f*(a-0.5)

            add_result = details+age_disp+tone_disp+mass_disp
            if add_result > 1.0:
                add_result = 1.0

            for i2 in range(3):
                result_image.append(add_result) #R,G,B
            result_image.append(1.0)#Alpha is always 1

        return result_image.tolist()

    def multiply_images(self, blender_image1, blender_image2, result_name, blending_factor = 0.5, ):

        if blender_image1 and blender_image2:
            size1 = blender_image1.size
            size2 = blender_image2.size

            if size1[0] != size1[1]:
                return None

            if size2[0] != size2[1]:
                return None

            if size1[0]*size1[1] > size2[0]*size2[1]:
                blender_image2.scale(size1[0],size1[1])

            if size1[0]*size1[1] < size2[0]*size2[1]:
                blender_image1.scale(size2[0],size2[1])

            image1 = self.image_to_array(blender_image1)
            image2 = self.image_to_array(blender_image2)


            result_array= array.array('f')

            for i in range(len(image1)):

                px1 = image1[i]
                px2 = image2[i]
                px_result = (px1 * px2 * blending_factor) + (px1 * (1 - blending_factor))

                #if add_result > 1.0:
                    #add_result = 1.0

                result_array.append(px_result)

            result_img = self.new_image(result_name, blender_image1.size)
            result_img.pixels =  result_array.tolist()


    def set_node_image(self, node_name, image_name):
        lab_logger.info("Assigning the image {0} to node {1}".format(image_name,node_name))
        mat_node = self.get_material_node(node_name)
        if mat_node:
            mat_image = self.get_image(image_name)
            if mat_image:
                mat_node.image = mat_image
            else:
                lab_logger.warning("Image not found: {0}".format(image_name))


    def get_material_parameters(self):

        parameter_identifiers = ["skin_", "eyes_"]
        material_parameters = {}

        for material_name in self.material_names:
            material = self.get_material(material_name)
            if material:
                for node in material.node_tree.nodes:
                    is_parameter = False
                    for param_identifier in parameter_identifiers:
                        if param_identifier in node.name:
                            is_parameter = True
                    if is_parameter == True:
                        material_parameters[node.name] = node.outputs[0].default_value
        return material_parameters



    def get_material_node(self, node_name):
        #TODO: check for double nodes in different materials

        material_node = None
        for material_name in self.material_names:
            material = self.get_material(material_name)
            if material:
                if node_name in material.node_tree.nodes:
                    material_node = material.node_tree.nodes[node_name]                    

        if not material_node:
            lab_logger.warning("Node not found: {0}".format(node_name))
        return material_node



    def set_node_float(self, node_name, value):
        mat_node = self.get_material_node(node_name)
        if mat_node:
            try:
                mat_node.outputs[0].default_value = value
            except:
                lab_logger.warning("Impossible to assign the default value to node {0}".format(node_name))




    def update_shader(self, material_parameters, float_values_only):

        for node_name, value in material_parameters.items():
            self.set_node_float(node_name, value)

        if float_values_only == False:
            self.set_node_image(self.skin_node_dermal_texture, self.filename_derm)
            self.set_node_image(self.skin_node_subdermal_texture, self.filename_subderm)
            self.set_node_image(self.skin_node_complexion_texture, self.filename_complexion)
            self.set_node_image(self.skin_node_displacement_texture, self.generated_disp_image_name)
            self.set_node_image(self.skin_node_eyeball_texture, self.filename_derm)


    def get_material(self, material_name):
        #To handle cases like human_skin.001
        obj = self.get_object()
        if obj:
            for material in obj.data.materials:
                if material_name in material.name:
                    return material
            lab_logger.warning("Material {0} not found in {1}".format(material_name, obj.name))
        return None


    def rename_skin_shaders(self):
        obj = self.get_object()
        for shader_name in self.material_names:
            human_mat = self.get_material(shader_name)
            if human_mat:
                human_mat.name = human_mat.name+str(time.time())


    def get_object(self):
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        return None

    def add_subdivision_modifier(self):
        obj = self.get_object()
        if self.subdivision_modifier_name not in obj.modifiers:
            obj.modifiers.new(self.subdivision_modifier_name,'SUBSURF')
        obj.modifiers[self.subdivision_modifier_name].levels = 2
        obj.modifiers[self.subdivision_modifier_name].render_levels = 2
        obj.modifiers[self.subdivision_modifier_name].show_viewport = False



    def add_displacement_modifier(self):

        disp_data_image = self.get_image(self.filename_disp)
        if disp_data_image:
            disp_img = self.new_image(self.generated_disp_image_name, disp_data_image.size)
            disp_img.generated_color = (0.5,0.5,0.5,1)

            obj = self.get_object()
            if self.generated_disp_modifier_ID not in obj.modifiers:
                obj.modifiers.new(self.generated_disp_modifier_ID,'DISPLACE')
            displacement_modifier = obj.modifiers[self.generated_disp_modifier_ID]
            displacement_modifier.texture_coords = 'UV'
            displacement_modifier.strength = 0.01
            displacement_modifier.show_viewport = False

            disp_tex = self.new_texture(self.generated_disp_modifier_ID)
            disp_tex.image = disp_img
            displacement_modifier.texture = disp_tex
        else:
            lab_logger.warning("Cannot create the displacement modifier: data image not found: {0}".format(algorithms.simple_path(self.displace_data_path)))


    def remove_displacement_modifier(self):
        obj = self.get_object()
        if self.generated_disp_modifier_ID in obj.modifiers:
            obj.modifiers.remove(obj.modifiers[self.generated_disp_modifier_ID])


    def get_displacement_visibility(self):
        obj = self.get_object()
        if self.generated_disp_modifier_ID in obj.modifiers:
            return obj.modifiers[self.generated_disp_modifier_ID].show_viewport

    def get_subdivision_visibility(self):
        obj = self.get_object()
        if self.subdivision_modifier_name in obj.modifiers:
            return obj.modifiers[self.subdivision_modifier_name].show_viewport

    def set_subdivision_visibility(self, value):
        obj = self.get_object()
        if self.subdivision_modifier_name in obj.modifiers:
            obj.modifiers[self.subdivision_modifier_name].show_viewport = value

    def set_displacement_visibility(self, value):
        obj = self.get_object()
        if self.generated_disp_modifier_ID in obj.modifiers:
            obj.modifiers[self.generated_disp_modifier_ID].show_viewport =value


    def new_image(self, name, img_size):
        lab_logger.info("Creating new image {0} ". format(name))
        if name not in bpy.data.images:
            bpy.data.images.new(name,img_size[0],img_size[1])
        else:
            lab_logger.info("Using existing {0} ". format(name))
        return bpy.data.images[name]

    def get_image(self, name):
        lab_logger.info("Getting image {0}".format(name))
        if name in bpy.data.images:

            #Some check for log
            if bpy.data.images[name].source == "FILE":
                if os.path.basename(bpy.data.images[name].filepath) != name:
                    lab_logger.warning("Image named {0} is from file: {1}".format(name,os.path.basename(bpy.data.images[name].filepath)))
            else:
                if not bpy.data.images[name]:
                    lab_logger.warning("Image {0} has not data".format(name))


            return bpy.data.images[name]
        else:
            lab_logger.warning("Image {0} not found in bpy.data.images".format(name))
        return None

    def new_texture(self, name):
        if name not in bpy.data.textures:
            bpy.data.textures.new(name, type = 'IMAGE')
        return bpy.data.textures[name]

    def save_image(self, name, filepath):
        img = self.get_image(name)
        scn = bpy.context.scene
        if img:
            current_format = scn.render.image_settings.file_format
            scn.render.image_settings.file_format = "PNG"
            img.save_render(filepath)
            scn.render.image_settings.file_format = current_format

            #if img.source == "GENERATED":
                #img.filepath_raw = filepath
                #img.file_format = scn.render.image_settings.file_format
                #img.save()
            #else:
                #img.save_render(filepath)
        else:
            lab_logger.warning("The image {0} cannot be saved because it's not present in bpy.data.images.". format(name))


    def has_displace_modifier(self):
        obj = self.get_object()
        return self.generated_disp_modifier_ID in obj.modifiers

    def calculate_displacement_texture(self,age_factor,tone_factor,mass_factor):
        time1 = time.time()

        if self.generated_disp_image_name in bpy.data.images:
            disp_img = bpy.data.images[self.generated_disp_image_name]
        else:
            lab_logger.warning("Displace image not found: {0}".format(self.generated_disp_image_name))
            return

        if self.generated_disp_modifier_ID in bpy.data.textures:
            disp_tex  = bpy.data.textures[self.generated_disp_modifier_ID]
        else:
            lab_logger.warning("Displace texture not found: {0}".format(self.generated_disp_modifier))
            return

        disp_data_image = self.get_image(self.filename_disp)
        if disp_data_image:
            disp_img.pixels =  self.calculate_disp_pixels(disp_data_image,age_factor,tone_factor,mass_factor)
            disp_tex.image = disp_img
            lab_logger.info("Displacement calculated in {0} seconds".format(time.time()-time1))
        else:
            lab_logger.error("Displace data image not found: {0}".format(algorithms.simple_path(self.displace_data_path)))


    def save_displacement_texture(self, filepath):
        self.save_image(self.generated_disp_image_name, filepath)

    def save_dermal_texture(self, filepath, material_parameters):

        derm_img = self.get_image(self.filename_derm)
        complexion_img = self.get_image(self.filename_complexion)
        b_factor = 0.5

        for node_name, value in material_parameters.items():
            if "omplexion" in node_name:
                b_factor = value
                break


        result_derm_img = self.multiply_images(derm_img, complexion_img, "derm_complexion", blending_factor = b_factor)
        self.save_image("derm_complexion", filepath)

    def save_subdermal_texture(self, filepath):
        self.save_image(self.filename_subderm, filepath)









