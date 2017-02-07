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

import bpy
from . import morphengine, skeletonengine, algorithms, proxyengine, materialengine
import os
import time
import json
import logging
import operator


lab_logger = logging.getLogger('manuelbastionilab_logger')


class HumanModifier:
    """
    A modifier is a group of related properties.
    """

    def __init__(self, name, obj_name):
        self.name = name
        self.obj_name = obj_name
        self.properties = []

    def get_object(self):
        """
        Get the blender object. It can't be stored because
        Blender's undo and redo change the memory locations
        """
        if self.obj_name in bpy.data.objects:
            return bpy.data.objects[self.obj_name]
        return None

    def add(self, prop):
        self.properties.append(prop)

    def __contains__(self, prop):
        for propx in self.properties:
            if propx == prop:
                return True
        return False

    def get_properties(self):
        """
        Return the properties contained in the
        modifier. Important: keep unsorted!
        """
        return self.properties

    def get_property(self, prop):
        """
        Return the property by name.
        """
        for propx in self.properties:
            if propx == prop:
                return propx
        return None

    def is_changed(self, char_data):
        """
        If a prop is changed, the whole modifier is considered changed
        """
        obj = self.get_object()
        for prop in self.properties:
            current_val = getattr(obj, prop, 0.5)
            if char_data[prop] != current_val:
                return True
        return False

    def sync_modifier_data_to_obj_prop(self, char_data):
        obj = self.get_object()
        for prop in self.properties:
            if hasattr(obj, prop):
                current_val = getattr(obj, prop, 0.5)
                char_data[prop] = current_val


    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return "Modifier <{0}> with {1} properties: {2}".format(
            self.name,
            len(self.properties),
            self.properties)

class HumanCategory:
    """
    A category is a group of related modifiers
    """

    def __init__(self, name):
        self.name = name
        self.modifiers = []

    def add(self, modifier):
        self.modifiers.append(modifier)

    def get_modifiers(self):
        return self.modifiers

    def get_modifier(self, name):
        for modifier in self.modifiers:
            if modifier.name == name:
                return modifier
        return None

    def get_all_properties(self):
        """
        Return all properties involved in the category,
        sorted and without double entries.
        """
        properties = []
        for modifier in self.modifiers:
            for prop in modifier.properties:
                if prop not in properties:
                    properties.append(prop)
        properties.sort()
        return properties

    def __contains__(self, mdf):
        for modifier in self.modifiers:
            if mdf.name == modifier.name:
                return True
        return False

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return "Category {0} with {1} modfiers".format(
            self.name,
            len(self.modifiers))


class Humanoid:
    """
    The humanoid is a container for categories of modifiers.
    """

    def __init__(self, lab_version):

        self.lab_vers = list(lab_version)
        self.has_data = False
        self.name = ""
        addon_directory = os.path.dirname(os.path.realpath(__file__))
        data_dir = os.path.join(addon_directory, "data")
        lab_logger.info("Looking for the database in the folder {0}...".format(algorithms.simple_path(data_dir)))
        if os.path.isdir(data_dir):
            self.data_path = data_dir
        else:
            lab_logger.critical("Database not found. Please check your Blender addons directory.")



    def init_database(self):

        is_obj = self.looking_for_humanoid_obj()
        if is_obj[0] == "FOUND":
            obj = self.get_object_by_name(is_obj[1])

        if obj:

            self.name = obj.name
            lab_logger.info("Found the humanoid object: {0}".format(obj.name))
            self.humanoid_type = obj.name[:len(obj.name)-2]
            self.character_ID = "0001"
            self.assign_ID()
            lab_logger.info("Init the database...")

            self.filepath = bpy.data.filepath
            if obj.data.shape_keys:
                lab_logger.error("The human object can't have shapekeys")

            self.no_categories = "BasisAsymTest"
            self.categories = {}
            self.bodydata_activated = True
            self.generator_bool_props = [
                "preserve_mass", "preserve_height", "preserve_tone",
                "preserve_face", "preserve_phenotype",
                "set_tone_and_mass"]
            self.generator_float_props = ["body_mass", "body_tone"]
            self.generator_levels = [
                ("LI", "Light", "Little variations from the standard"),
                ("RE", "Realistic", "Realistic characters"),
                ("NO", "Noticeable", "Very characterized people"),
                ("CA", "Caricature", "Engine for caricatures"),
                ("EX", "Extreme", "Extreme characters")]
            self.armat = skeletonengine.SkeletonEngine(
                obj,
                obj.parent,
                self.data_path)

            self.ethnic_path = os.path.join(self.data_path, self.name, "phenotypes")

            self.expression_path = os.path.join(
                self.data_path,
                "shared_expressions",
                obj.name[:len(obj.name)-2])
            self.preset_path = os.path.join(
                self.data_path,
                "shared_presets",
                obj.name[:len(obj.name)-2])
            self.pose_path = os.path.join(
                self.data_path,
                "shared_poses",
                obj.name[:len(obj.name)-2])


            self.m_engine = morphengine.MorphingEngine(obj, self.data_path)
            self.mat_engine = materialengine.MaterialEngine(obj, self.data_path)
            self.character_data = {}
            self.character_metaproperties = {"last_character_age":0.0,
                                            "character_age":0.0,
                                            "last_character_mass":0.0,
                                            "character_mass":0.0,
                                            "last_character_tone":0.0,
                                            "character_tone":0.0}
            self.character_material_properties = self.mat_engine.get_material_parameters()

            self.metadata_activated = True
            self.shared_transformation_filename = obj.name[:len(obj.name)-2]+"_transf.json"
            self.shared_transform_data_path = os.path.join(
                                            self.data_path,
                                            "shared_transformations",
                                            self.shared_transformation_filename)
            self.transformations_data = {}

            for morph in self.m_engine.morph_data.keys():
                self.init_character_data(morph)

            lab_logger.info("Loaded {0} categories from morph database".format(
                len(self.categories)))
            bpy.context.scene.objects.active = obj
            self.measures = self.m_engine.measures
            self.delta_measures = {}
            self.init_delta_measures()
            self.load_transformation_database()
            self.mat_engine.add_subdivision_modifier()
            self.mat_engine.add_displacement_modifier()
            self.has_data = True
            #self.is_subdivided = False
        else:
            lab_logger.error("No humanoid for ManuelbastioniLAB found")
            self.has_data = False


    def assign_ID(self):

        bpy.types.Object.character_ID = bpy.props.StringProperty(
            name="human_ID",
            maxlen = 25,
            default= "-")

        obj = self.get_object()
        if "character_ID" in obj.keys():
            lab_logger.info("Character_ID recovered from existing ID property")
            self.character_ID = obj['character_ID']
        else:
            lab_logger.info("Character_ID assigned from scratch")
            self.character_ID = str(time.time())

        obj.character_ID = self.character_ID


    def check_version(self,m_vers):

        version_check = False

        #m_vers must be a list, tuple or str
        if type(m_vers) is not str: #For example it is an IDfloatarray
            m_vers = list(m_vers)

        lab_version = str(self.lab_vers)
        lab_version = lab_version.replace(' ','')
        lab_version = lab_version.strip("[]()")

        mesh_version = str(m_vers)
        mesh_version = mesh_version.replace(' ','')
        mesh_version = mesh_version.strip("[]()")

        lab_logger.info("Check humanoid version {0} with the current {1}".format(mesh_version,lab_version))

        if len(lab_version) == len(mesh_version):
            if lab_version[0] == mesh_version[0]:
                if lab_version[2] == mesh_version[2]:
                    version_check = True

        lab_logger.info("Version_check: {0}".format(version_check))
        return version_check


    def rename_obj(self):
        obj = self.get_object()
        obj.name = str(time.time())

    def rename_materials(self):
        self.mat_engine.rename_skin_shaders()




    def looking_for_humanoid_obj(self):
        """
        Looking for a mesh with a valid manuellab_vers IDproperty
        """
        lab_logger.info("Looking for an humanoid object...")
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                if "manuellab_vers" in obj.keys():
                    if self.check_version(obj["manuellab_vers"]):
                        if not obj.data.shape_keys:
                            return ("FOUND", obj.name)
                        else:
                            msg = "{0} has some shapekeys and can't be used in the lab".format(obj.name)
                            lab_logger.warning(msg)
                            return("ERROR",msg)
                    else:
                        msg = "{0} is created with a different version of the lab.".format(obj.name)
                        lab_logger.warning(msg)
                        return("ERROR",msg)

        msg = "No existing valid human objects found in the scene"
        lab_logger.info(msg)
        return("NO_OBJ", msg )



    def get_object_by_name(self,name):
        if name in bpy.data.objects:
            return bpy.data.objects[name]
        return None

    def get_object(self):
        if self.name in bpy.data.objects:
            return bpy.data.objects[self.name]
        return None

    def load_transformation_database(self):
        if os.path.isfile(self.shared_transform_data_path):
            time1 = time.time()
            database_file = open(self.shared_transform_data_path, "r")
            try:
                self.transformations_data = json.load(database_file)
                lab_logger.info("Transformations database {0}".format(algorithms.simple_path(self.shared_transform_data_path)))
            except:
                lab_logger.error("Error decoding {0}".format(algorithms.simple_path(self.shared_transform_data_path)))
            database_file.close()
        else:
            lab_logger.warning("Tranformations database not found")

    def get_categories(self):
        categories = self.categories.values()
        return sorted(categories)

    def get_category(self, name):
        if name in self.categories:
            return self.categories[name]

    def get_properties_in_category(self, name):
        return self.categories[name].get_all_properties()

    def init_character_data(self, morph_name):
        """
        Creates categories and properties from shapekey name
        """
        components = morph_name.split("_")
        if components[0][:4] not in self.no_categories:
            if len(components) == 3:
                category_name = components[0]
                if category_name not in self.categories:
                    category = HumanCategory(category_name)
                    self.categories[category_name] = category
                else:
                    category = self.categories[category_name]

                modifier_name = components[0]+"_"+components[1]
                modifier = category.get_modifier(modifier_name)
                if not modifier:
                    modifier = HumanModifier(modifier_name, self.name)
                    category.add(modifier)

                for element in components[1].split("-"):
                    prop = components[0]+"_" + element
                    if prop not in modifier:
                        modifier.add(prop)
                    self.character_data[prop] = 0.5
            else:
                lab_logger.warning("Wrong name for morph: {0}".format(morph_name))

    def reset_category(self, categ):
        time1 = time.time()
        obj = self.get_object()
        category = self.get_category(categ)
        for prop in category.get_all_properties():
            self.character_data[prop] = 0.5
        self.update_character(category_name=category.name, mode = "update_all")
        lab_logger.info("Category resetted in {0} secs".format(time.time()-time1))


    def exist_measure_database(self):
        return self.m_engine.measures_database_exist

    def exist_texture_database(self):
        return self.mat_engine.texture_database_exist




    def automodelling(self,use_measures_from_GUI=False, use_measures_from_dict=None, use_measures_from_current_obj=False, mix=False):

        if self.m_engine.measures_database_exist:
            time2 = time.time()
            obj = self.get_object()
            n_samples = 3

            if use_measures_from_GUI:
                convert_to_inch = getattr(obj, "use_inch",False)
                if convert_to_inch:
                    conversion_factor = 39.37001
                else:
                    conversion_factor = 100

                wished_measures = {}
                for measure_name in self.m_engine.measures.keys():
                    if measure_name != "body_height_Z":
                        wished_measures[measure_name] = getattr(obj, measure_name, 0.5)/conversion_factor


                total_height_Z = 0
                for measure_name in self.m_engine.body_height_Z_parts:
                    total_height_Z += wished_measures[measure_name]

                wished_measures["body_height_Z"] = total_height_Z

            if use_measures_from_current_obj:
                current_shape_verts = []
                for vert in obj.data.vertices:
                    current_shape_verts.append(vert.co.copy())
                wished_measures = self.m_engine.calculate_measures(vert_coords=current_shape_verts)

            if use_measures_from_dict:
                wished_measures = use_measures_from_dict

            #if use_database:
            self.m_engine.calculate_proportions(wished_measures)
            similar_characters_data  = self.m_engine.compare_data_proportions()

            best_character = similar_characters_data[0]
            filepath = best_character[1]
            self.load_character(filepath)

            for char_data in similar_characters_data[1:n_samples]:
                filepath = char_data[1]
                self.load_character(filepath, mix = True)


            self.measure_fitting(wished_measures, mix)
            self.update_character(mode = "update_directly_verts")
            #self.update_character(mode = "update_all")

            lab_logger.info("Human fitting in {0} secs".format(time.time()-time2))

    def clean_verts_to_process(self):
        self.m_engine.verts_to_update.clear()

    def update_displacement(self):
        obj = self.get_object()
        age_factor = obj.character_age
        tone_factor = obj.character_tone
        mass_factor = obj.character_mass
        self.mat_engine.calculate_displacement_texture(age_factor,tone_factor,mass_factor)



    def remove_skin_displacement(self):
        self.mat_engine.remove_displacement_modifier()

    def save_skin_displacement_image(self, filepath):
        self.mat_engine.save_displacement_texture(filepath)

    def save_skin_dermal_image(self, filepath):
        self.mat_engine.save_dermal_texture(filepath, self.character_material_properties)

    def save_skin_subdermal_image(self, filepath):
        self.mat_engine.save_subdermal_texture(filepath)

    def get_subd_visibility(self):
        return self.mat_engine.get_subdivision_visibility()

    def set_subd_visibility(self,value):
        self.mat_engine.set_subdivision_visibility(value)

    def get_disp_visibility(self):
        return self.mat_engine.get_displacement_visibility()

    def set_disp_visibility(self,value):
        self.mat_engine.set_displacement_visibility(value)

    def update_materials(self, float_values_only = False):
        obj = self.get_object()
        for prop in self.character_material_properties.keys():
            if hasattr(obj, prop):
                self.character_material_properties[prop] = getattr(obj, prop)
        self.mat_engine.update_shader(self.character_material_properties,float_values_only)

    def correct_expressions(self, correct_all=False, finish_it=False):
        """
        Correct all the expression morphing that are different from 0
        """

        #TODO: re-enable the finishing after some improvements

        time1 = time.time()
        expressions_to_correct = []
        for prop in self.categories["Expressions"].get_all_properties():
            if not correct_all:
                if self.character_data[prop] != 0.5:
                    expressions_to_correct.append(prop)
            else:
                expressions_to_correct.append(prop)
        self.m_engine.correct_morphs(expressions_to_correct)
        if finish_it:
            self.m_engine.apply_finishing_morph()
        lab_logger.info("Expression corrected in {0} secs".format(time.time()-time1))


    def reset_character(self):
        time1 = time.time()
        obj = self.get_object()
        self.reset_metadata()
        for category in self.get_categories():
            for modifier in category.get_modifiers():
                for prop in modifier.get_properties():
                    self.character_data[prop] = 0.5
        self.update_character(mode = "update_all")


        lab_logger.info("Character reset in {0} secs".format(time.time()-time1))


    def reset_metadata(self):
        obj = self.get_object()
        for meta_data_prop in self.character_metaproperties.keys():
            self.character_metaproperties[meta_data_prop]=0.0


    def reset_mesh(self):
        self.m_engine.reset()

    def store_mesh_in_cache(self):
        self.m_engine.copy_in_cache()

    def restore_mesh_from_cache(self):
        self.m_engine.copy_from_cache()
        self.m_engine.update(update_all_verts=True)
        self.m_engine.clean_the_cache()


    def sync_obj_props_to_character_metadata(self):

        self.metadata_activated = False
        obj = self.get_object()
        for meta_data_prop, value in self.character_metaproperties.items():
            if hasattr(obj, meta_data_prop):
                setattr(obj, meta_data_prop, value)
            else:
                lab_logger.warning("metadata {0}.{1} not found".format(obj.name,meta_data_prop))
        self.metadata_activated = True


    def delete_all_properties(self):
        time1 = time.time() #TODO: usare obj.keys per lavorare solo sui valory applicati
        lab_logger.info("Deleting custom properties")
        obj = self.get_object()
        props_to_delete = set(["manuellab_vers", "character_ID"])
        for category in self.get_categories():
            for modifier in category.get_modifiers():
                for prop in modifier.get_properties():
                    if hasattr(obj, prop):
                        props_to_delete.add(prop)
                for measure in self.m_engine.measures.keys():
                    if hasattr(obj, measure):
                        props_to_delete.add(measure)
                for metaproperty in self.character_metaproperties.keys():
                    if hasattr(obj, metaproperty):
                        props_to_delete.add(metaproperty)

        for prop in props_to_delete:
            try:
                del obj[prop]
            except:
                lab_logger.info("Property {0} was not used by this character".format(prop))
        lab_logger.info("Character reset in {0} secs".format(time.time()-time1))




    def recover_prop_values_from_obj_attr(self):
        obj = self.get_object()
        char_data = {"structural":{}, "metaproperties":{}, "materialproperties":{}}


        for prop in self.character_data.keys():
            if prop in obj.keys():
                char_data["structural"][prop] = obj[prop]

        for prop in self.character_metaproperties.keys():
            if prop in obj.keys():
                char_data["metaproperties"][prop] = obj[prop]
                char_data["metaproperties"]["last_"+prop] = obj[prop]

        for prop in self.character_material_properties.keys():
            if prop in obj.keys():
                char_data["materialproperties"][prop] = obj[prop]
        self.load_character(char_data)

    def sync_obj_props_to_character_data(self):
        obj = self.get_object()
        self.bodydata_activated = False
        for prop,value in self.character_data.items():
            setattr(obj, prop, value)

    def sync_internal_data_with_mesh(self):
        self.m_engine.init_final_form()


    def sync_gui_according_measures(self):

        obj = self.get_object()
        measures = self.m_engine.calculate_measures()
        convert_to_inch = getattr(obj, "use_inch", False)
        if convert_to_inch:
            conversion_factor = 39.37001
        else:
            conversion_factor = 100
        for measure_name,measure_val in measures.items():
            setattr(obj, measure_name, measure_val*conversion_factor)

    def update_character(self, category_name = None, mode = "update_all"):
        time1 = time.time()
        obj = self.get_object()
        self.clean_verts_to_process()

        if mode == "test":
            update_directly_verts = False
            update_geometry_all = False
            update_geometry_selective = False
            update_armature = False
            update_normals = False
            update_proxy = False
            update_measures = True
            sync_morphdata = False
            sync_GUI = True
            sync_GUI_metadata = True

        if mode == "update_all":
            update_directly_verts = False
            update_geometry_all = True
            update_geometry_selective = False
            update_armature = True
            update_normals = True
            update_proxy = False
            update_measures = True
            sync_morphdata = False
            sync_GUI = True
            sync_GUI_metadata = True

        if mode == "update_metadata":
            update_directly_verts = False
            update_geometry_all = True
            update_geometry_selective = False
            update_armature = True
            update_normals = True
            update_proxy = False
            update_measures = True
            sync_morphdata = False
            sync_GUI = True
            sync_GUI_metadata = False

        if mode == "update_directly_verts":
            update_directly_verts = True
            update_geometry_all = False
            update_geometry_selective = False
            update_armature = True
            update_normals = True
            update_proxy = False
            update_measures = True
            sync_morphdata = False
            sync_GUI = True
            sync_GUI_metadata = False

        if mode == "update_only_morphdata":
            update_directly_verts = False
            update_geometry_all = False
            update_geometry_selective = False
            update_armature = False
            update_normals = False
            update_proxy = False
            update_measures = False
            sync_morphdata = False
            sync_GUI = False
            sync_GUI_metadata = False

        if mode == "update_realtime":
            update_directly_verts = False
            update_geometry_all = False
            update_geometry_selective = True
            update_armature = True
            update_normals = False
            update_proxy = False
            update_measures = False
            sync_morphdata = True
            sync_GUI = False
            sync_GUI_metadata = False


        if update_directly_verts:
            self.m_engine.update(update_all_verts=True)
        else:
            if category_name:
                category = self.categories[category_name]
                modified_modifiers = []
                for modifier in category.get_modifiers():
                    if modifier.is_changed(self.character_data):
                        modified_modifiers.append(modifier)
                for modifier in modified_modifiers:
                    if sync_morphdata:
                        modifier.sync_modifier_data_to_obj_prop(self.character_data)
                    self.combine_morphings(modifier)
            else:
                for category in self.get_categories():
                    for modifier in category.get_modifiers():
                        self.combine_morphings(modifier, add_vertices_to_update=True)

        if update_geometry_all:
            self.m_engine.update(update_all_verts=True)
        if update_geometry_selective:
            self.m_engine.update(update_all_verts=False)
        if sync_GUI:
            self.sync_obj_props_to_character_data()
        if sync_GUI_metadata:
            self.sync_obj_props_to_character_metadata()
        if update_measures:
            self.sync_gui_according_measures()
        if update_armature:
            self.armat.fit_joints()
        if update_normals:
            obj.data.calc_normals()
        if update_proxy:
            self.load_proxy()


        #lab_logger.debug("Character updated in {0} secs".format(time.time()-time1))

    def generate_character(self):
        lab_logger.info("Generating character...")
        random_value = {"LI": 0.05, "RE": 0.1, "NO": 0.2, "CA":0.3, "EX": 0.5}

        obj = self.get_object()
        excluded_properties = ["Expressions"]
        if obj.preserve_mass:
            excluded_properties += ["Mass"]
        if obj.preserve_tone:
            excluded_properties += ["Tone"]
        if obj.preserve_height:
            excluded_properties += ["Length", "Body_Size"]
        if obj.preserve_face:
            excluded_properties += ["Eye", "Eyelid", "Nose", "Mouth"]
            excluded_properties += ["Ear", "Head", "Forehead", "Cheek", "Jaw"]
        if obj.preserve_phenotype:
            excluded_properties = ["Expressions"]

        for prop in self.character_data:
            if not algorithms.is_excluded(prop, excluded_properties):
                new_val = algorithms.generate_parameter(
                    self.character_data[prop],
                    random_value[obj.random_engine],
                    obj.preserve_phenotype)
                if obj.set_tone_and_mass:
                    if "Mass" in prop:
                        new_val = obj.body_mass + (1-obj.body_mass)*new_val*obj.body_mass
                    if "Tone" in prop:
                        new_val = obj.body_tone + (1-obj.body_tone)*new_val*obj.body_tone
                self.character_data[prop] = new_val
        self.update_character(mode = "update_all")




    def calculate_transformation(self, tr_type):
        #lab_logger.debug("Modifying the {0}".format(tr_type))


        obj = self.get_object()

        #TODO automatizzare con getattr direttamente dal dizionario

        if tr_type == "AGE":
            current_tr_factor = obj.character_age
            previous_tr_factor = self.character_metaproperties["last_character_age"]
            transformation_id = "age_data"
        if tr_type == "FAT":
            current_tr_factor = obj.character_mass
            previous_tr_factor = self.character_metaproperties["last_character_mass"]
            transformation_id = "fat_data"
        if tr_type == "MUSCLE":
            current_tr_factor = obj.character_tone
            previous_tr_factor = self.character_metaproperties["last_character_tone"]
            transformation_id = "muscle_data"

        if current_tr_factor >= 0:
            transformation_2 = current_tr_factor
            transformation_1 = 0
        else:
            transformation_2 = 0
            transformation_1 = -current_tr_factor

        if previous_tr_factor >= 0:
            last_transformation_2 = previous_tr_factor
            last_transformation_1 = 0
        else:
            last_transformation_2 = 0
            last_transformation_1 = -previous_tr_factor


        if transformation_id in self.transformations_data:
            tr_data = self.transformations_data[transformation_id]

            for prop in self.character_data:
                for tr_parameter in tr_data:
                    if tr_parameter[0] in prop:
                        linear_factor = tr_parameter[1]*transformation_1 + tr_parameter[2]*transformation_2 - tr_parameter[1]*last_transformation_1 - tr_parameter[2]*last_transformation_2

                        self.character_data[prop] = self.character_data[prop] + linear_factor

            if tr_type == "AGE":
                self.character_metaproperties['character_age'] = current_tr_factor
                self.character_metaproperties['last_character_age'] = current_tr_factor
            if tr_type == "FAT":
                self.character_metaproperties['character_mass'] = current_tr_factor
                self.character_metaproperties['last_character_mass'] = current_tr_factor
            if tr_type == "MUSCLE":
                self.character_metaproperties['character_tone'] = current_tr_factor
                self.character_metaproperties['last_character_tone'] = current_tr_factor

            self.update_character(mode = "update_metadata")

        else:
            lab_logger.warning("{0} data not present".format(transformation_id))


    def init_delta_measures(self):

        obj = self.get_object()
        time1 = time.time()
        for relation in self.m_engine.measures_relat_data:
            m_name = relation[0]
            modifier_name = relation[1]
            for category in self.get_categories():
                for modifier in category.get_modifiers():
                    if modifier.name == modifier_name:
                        for prop in modifier.get_properties():

                            self.character_data[prop] = 0.0
                            self.combine_morphings(modifier)
                            measure1 = self.m_engine.calculate_measures(measure_name=m_name)

                            self.character_data[prop] = 1.0
                            self.combine_morphings(modifier)
                            measure3 = self.m_engine.calculate_measures(measure_name=m_name)

                            #Last measure also restores the value to 0.5
                            self.character_data[prop] = 0.5
                            self.combine_morphings(modifier)
                            measure2 = self.m_engine.calculate_measures(measure_name=m_name)

                            delta_name = modifier_name+prop

                            delta1 = measure1-measure2
                            delta3 = measure3-measure2

                            self.delta_measures[delta_name] = [delta1,delta3]


        lab_logger.info("Delta init in {0} secs".format(time.time()-time1))


    def search_best_value(self,m_name,wished_measure,human_modifier,prop):

        self.character_data[prop] = 0.5
        self.combine_morphings(human_modifier)
        measure2 = self.m_engine.calculate_measures(measure_name=m_name)
        delta_name = human_modifier.name+prop

        delta1 = self.delta_measures[delta_name][0]
        delta3 = self.delta_measures[delta_name][1]

        measure1 = measure2 + delta1
        measure3 = measure2 + delta3

        if wished_measure < measure2:
            xa = 0
            xb = 0.5
            ya = measure1
            yb = measure2
        else:
            xa = 0.5
            xb = 1
            ya = measure2
            yb = measure3

        if ya-yb != 0:
            value = algorithms.linear_interpolation_y(xa,xb,ya,yb,wished_measure)

            if value < 0:
                value = 0
            if value > 1:
                value = 1
        else:
            value = 0.5
        return value


    def measure_fitting(self, wished_measures,mix = False):

        if self.m_engine.measures_database_exist:
            obj = self.get_object()
            time1 = time.time()
            for relation in self.m_engine.measures_relat_data:
                measure_name = relation[0]
                modifier_name = relation[1]
                if measure_name in wished_measures:
                    wish_measure = wished_measures[measure_name]

                    for category in self.get_categories():
                        for modifier in category.get_modifiers():
                            if modifier.name == modifier_name:
                                for prop in modifier.get_properties():

                                    if mix:
                                        best_val = self.search_best_value(measure_name,wish_measure,modifier,prop)
                                        value = (self.character_data[prop]+best_val)/2
                                        self.character_data[prop] = value
                                    else:
                                        self.character_data[prop] = self.search_best_value(measure_name,wish_measure,modifier,prop)
                                self.combine_morphings(modifier)

            lab_logger.info("Measures fitting in {0} secs".format(time.time()-time1))


    def save_character(self, filepath):
        lab_logger.info("Exporting character to {0}".format(algorithms.simple_path(filepath)))
        obj = self.get_object()
        char_data = {"manuellab_vers": self.lab_vers, "structural":dict(), "proportions":dict(), "metaproperties":dict(), "materialproperties":dict()}

        if obj:

            for meta_data_prop, value in self.character_metaproperties.items():
                char_data["metaproperties"][meta_data_prop] = value #getattr(obj, meta_data_prop, 0.0)

            for prop in self.character_data.keys():
                if self.character_data[prop] != 0.5:
                    char_data["structural"][prop] = round(self.character_data[prop], 4)

            for prop in self.character_material_properties.keys():
                char_data["materialproperties"][prop] = round(self.character_material_properties[prop])

            if obj.export_proportions:
                self.m_engine.calculate_proportions(self.m_engine.calculate_measures())
                for proportion, value in self.m_engine.proportions.items():
                    char_data["proportions"][proportion] = round(value, 4)

            output_file = open(filepath, 'w')
            json.dump(char_data, output_file)
            output_file.close()

    def export_measures(self, filepath):
        lab_logger.info("Exporting measures to {0}".format(algorithms.simple_path(filepath)))
        obj = self.get_object()
        char_data = {"manuellab_vers": self.lab_vers, "measures":dict()}
        if obj:
            measures = self.m_engine.calculate_measures()
            for measure, measure_val in measures.items():
                measures[measure] = round(measure_val, 3)
            char_data["measures"]=measures
            output_file = open(filepath, 'w')
            json.dump(char_data, output_file)
            output_file.close()


    def load_character(self, data_source, reset_string = "nothing", reset_unassigned=True, mix=False, update_mode = "update_all"):

        obj = self.get_object()
        log_msg_type = "character data"

        if type(data_source) == str:
            if os.path.isfile(data_source):
                log_msg_type = algorithms.simple_path(data_source)
                try:
                    database_file = open(data_source, "r")
                    charac_data = json.load(database_file)
                    database_file.close()
                except:
                    lab_logger.error("{0} not valid".format(log_msg_type))
                    return None
            else:
                lab_logger.warning("File not valid: {0}".format(log_msg_type))
                return None
        #TODO: better check of types
        else:
            charac_data = data_source

        lab_logger.info("Loading character from {0}".format(log_msg_type))

        if "manuellab_vers" in charac_data:
            if not self.check_version(charac_data["manuellab_vers"]):
                lab_logger.warning("{0} created with vers. {1}. Current vers is {2}".format(log_msg_type,charac_data["manuellab_vers"],self.lab_vers))
        else:
            lab_logger.warning("No lab version specified in {0}".format(log_msg_type))

        if "structural" in charac_data:
            char_data = charac_data["structural"]
        else:
            lab_logger.warning("No structural data in  {0}".format(log_msg_type))
            char_data = {}

        if "materialproperties" in charac_data:
            material_data = charac_data["materialproperties"]
        else:
            lab_logger.info("No material data in  {0}".format(log_msg_type))
            material_data = {}

        if "metaproperties" in charac_data:
            meta_data = charac_data["metaproperties"]
        else:
            lab_logger.warning("No metaproperties data in  {0}".format(log_msg_type))
            meta_data = {}

        if char_data != None:
            for name in self.character_data.keys():
                if reset_string in name:
                    self.character_data[name] = 0.5
                if name in char_data:
                    if mix:
                        self.character_data[name] = (self.character_data[name]+char_data[name])/2
                    else:
                        self.character_data[name] = char_data[name]
                else:
                    if reset_unassigned:
                        if mix:
                            self.character_data[name] = (self.character_data[name]+0.5)/2
                        else:
                            self.character_data[name] = 0.5


        for name in self.character_metaproperties.keys():
            if name in meta_data:
                self.character_metaproperties[name] = meta_data[name]


        for name in self.character_material_properties.keys():
            if name in material_data:
                self.character_material_properties[name] = material_data[name]

        self.update_character(mode = update_mode)



    def load_measures(self, filepath):
        lab_logger.info("Loading measures from {0}".format(algorithms.simple_path(filepath)))
        if os.path.isfile(filepath):
            try:
                database_file = open(filepath, "r")
                char_data = json.load(database_file)
                database_file.close()
            except:
                lab_logger.error("json not valid, {0}".format(algorithms.simple_path(filepath)))
                return None
            #Check the database structure
            if not ("measures" in char_data):
                lab_logger.error("This json has not the measures info, {0}".format(algorithms.simple_path(filepath)))
                return None
            c_data = char_data["measures"]
            return c_data
        else:
            lab_logger.warning("File not valid: {0}".format(algorithms.simple_path(filepath)))
            return None


    def import_measures(self, filepath):
        char_data = self.load_measures(filepath)
        if char_data:
            self.automodelling(use_measures_from_dict=char_data)

    def load_pose(self, filepath):
        lab_logger.info("Loading pose from {0}".format(algorithms.simple_path(filepath)))
        self.armat.load_pose(filepath)
        #self.load_proxy()

    def save_pose(self, filepath):
        lab_logger.info("Saving pose to {0}".format(algorithms.simple_path(filepath)))
        self.armat.save_pose(filepath)

    def reset_pose(self):
        self.armat.reset_pose()        
   

    def validate_proxy_for_saving(self):
        obj = self.get_object()

        if self.armat.is_in_rest_pose():
            return proxyengine.validate_proxy_save(obj)
        else:
            return "Please reset the pose of character before calibration of proxy"


    def validate_proxy_for_loading(self):
        obj = self.get_object()
        return proxyengine.validate_proxy_load(obj)

    def validate_proxy_for_selection(self):
        obj = self.get_object()
        return proxyengine.validate_proxy_select(obj)

    def proxy_origin_to_human_origin(self):
        obj = self.get_object()
        proxyengine.move_proxy_origin_to_human_origin(obj)

    def scale_proxy_to_human(self):
        obj = self.get_object()
        proxyengine.apply_proxy_transformations(obj)

    def disable_proxy_modifiers(self):
        obj = self.get_object()
        proxyengine.disable_modifiers(obj)

    def disable_human_modifiers(self):
        obj = self.get_object()
        for modf in obj.modifiers:
            if modf.type == 'SUBSURF':
                modf.show_viewport = False
                lab_logger.info("Disabled armature in {0}".format(obj.name))

    def save_proxy(self):
        obj = self.get_object()
        proxy_obj = bpy.context.active_object
        #proxy_obj.parent = obj
        proxy_ID = self.humanoid_type + proxy_obj.name
        proxy_path = os.path.join(bpy.context.user_preferences.filepaths.temporary_directory,proxy_ID)

        if os.path.isfile(proxy_path):
            lab_logger.info("Owerwriting proxy data for obj {0}".format(proxy_obj.name))
        else:
            lab_logger.info("Saving proxy data for obj {0}".format(proxy_obj.name))
        setattr(proxy_obj, 'proxy_ID', proxy_ID)
        filepath1 = proxy_path+".proxy"
        filepath2 = proxy_path+".forma"
        proxyengine.save_proxy_database(obj, proxy_obj, filepath1)
        proxyengine.save_forma_database(proxy_obj, filepath2)


    def load_proxy(self):

        obj = self.get_object()
        obj_armature = self.armat.get_armature()
        scene = bpy.context.scene
        current_form = obj.to_mesh(scene, True, 'PREVIEW')
        for blender_obj in bpy.data.objects:
            if blender_obj != obj and blender_obj.type == 'MESH':
                if obj_armature:

                    if 'proxy_ID' in blender_obj.keys():
                        proxy_obj = blender_obj

                        proxy_obj.matrix_world = obj_armature.matrix_world
                        lab_logger.info("Found proxy {0}".format(proxy_obj.name))
                        if hasattr(proxy_obj,'proxy_ID'):
                            proxy_ID = proxy_obj.proxy_ID
                        else:
                            proxy_ID = proxy_obj['proxy_ID']

                        proxy_path = os.path.join(bpy.context.user_preferences.filepaths.temporary_directory,proxy_ID)
                        filepath1 = proxy_path+".proxy"
                        filepath2 = proxy_path+".forma"

                        proxyengine.load_proxy_database(current_form, proxy_obj, filepath1)
                        forma_data = proxyengine.load_forma_database(filepath2)

                        boundary_verts = proxyengine.get_boundary_verts(proxy_obj)

                        if forma_data:
                            proxyengine.calculate_finishing_morph(
                                proxy_obj,
                                boundary_verts,
                                forma_data)

        bpy.data.meshes.remove(current_form)

    def combine_morphings(self, modifier, refresh_only=False, add_vertices_to_update=True):
        """
        Mix shapekeys using smart combo algorithm.
        """

        values = []
        for prop in modifier.properties:
            val = self.character_data[prop]
            if val > 1.0:
                val = 1.0
            if val < 0:
                val = 0
            val1 = algorithms.function_modifier_a(val)
            val2 = algorithms.function_modifier_b(val)
            values.append([val1, val2])
        names, weights = algorithms.smart_combo(modifier.name, values)
        for i in range(len(names)):
            if refresh_only:
                self.m_engine.morph_values[names[i]] = weights[i]
            else:
                self.m_engine.calculate_morph(
                    names[i],
                    weights[i],
                    add_vertices_to_update)


