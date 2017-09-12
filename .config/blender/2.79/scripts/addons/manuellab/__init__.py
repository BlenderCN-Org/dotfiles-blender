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


bl_info = {
    "name": "ManuelbastioniLAB",
    "author": "Manuel Bastioni",
    "version": (1, 3, 0),
    "blender": (2, 7, 7),
    "location": "View3D > Tools > ManuelbastioniLAB",
    "description": "A complete lab for characters creation",
    "warning": "",
    'wiki_url': "http://www.manuelbastioni.com",
    "category": "Characters"}

import bpy
import os
import json
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.app.handlers import persistent
from . import humanoid
import time
import logging

#import cProfile, pstats, io
#import faulthandler
#faulthandler.enable()

log_path = os.path.join(bpy.context.user_preferences.filepaths.temporary_directory, "manuellab_log.txt")
log_is_writeable = True

try:
    test_writing = open(log_path, 'w')
    test_writing.close()
except:
    print("WARNING: Writing permission error for {0}".format(log_path))
    print("The log will be redirected to the console (here)")
    log_is_writeable = False

lab_logger = logging.getLogger('manuelbastionilab_logger')
lab_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

if log_is_writeable:

    fhandler = logging.FileHandler(log_path, mode ='w')
    fhandler.setLevel(logging.INFO)
    chandler = logging.StreamHandler()
    chandler.setLevel(logging.WARNING)
    fhandler.setFormatter(formatter)
    chandler.setFormatter(formatter)
    lab_logger.addHandler(fhandler)
    lab_logger.addHandler(chandler)

else:

    chandler = logging.StreamHandler()
    chandler.setLevel(logging.INFO)
    chandler.setFormatter(formatter)    
    lab_logger.addHandler(chandler)


T1 = "humanoid_humanf01"
T1_LABEL = "Caucasian female"
T1_DESCR = "Generate a realistic caucasian female character"

T2 = "humanoid_humanf02"
T2_LABEL = "Asian female"
T2_DESCR = "Generate a realistic asian female character"

T3 = "humanoid_humanf03"
T3_LABEL = "Afro female"
T3_DESCR = "Generate a realistic african female character"

T4 = "humanoid_humanm01"
T4_LABEL = "Caucasian male"
T4_DESCR = "Generate a realistic caucasian male character"

T5 = "humanoid_humanm02"
T5_LABEL = "Asian male"
T5_DESCR = "Generate a realistic asian male character"

T6 = "humanoid_humanm03"
T6_LABEL = "Afro male"
T6_DESCR = "Generate a realistic african male character"

T7 = "humanoid_animef01"
T7_LABEL = "Anime Classic female shojo"
T7_DESCR = "Generate an anime female in shojo style"

T8 = "humanoid_animem01"
T8_LABEL = "Anime Classic male shojo"
T8_DESCR = "Generate an anime male in shojo style"

T9 = "humanoid_animef02"
T9_LABEL = "Anime Modern female shojo"
T9_DESCR = "Generate an anime female in modern shojo style"

T10 = "humanoid_animem02"
T10_LABEL = "Anime Modern male shojo"
T10_DESCR = "Generate an anime female in modern shojo style"


HUMANOID_TYPES = [
    (T1, T1_LABEL, T1_DESCR),
    (T2, T2_LABEL, T2_DESCR),
    (T3, T3_LABEL, T3_DESCR),
    (T4, T4_LABEL, T4_DESCR),
    (T5, T5_LABEL, T5_DESCR),
    (T6, T6_LABEL, T6_DESCR),
    (T7, T7_LABEL, T7_DESCR),
    (T8, T8_LABEL, T8_DESCR),
    (T9, T9_LABEL, T9_DESCR),
    (T10, T10_LABEL, T10_DESCR)]


the_humanoid = humanoid.Humanoid(bl_info["version"])
gui_status = "NEW_SESSION"
gui_err_msg = ""

def get_current_blend_name_without_ext():
    current_blend_name = bpy.path.basename(bpy.data.filepath)
    name_without_extension = os.path.splitext(current_blend_name)[0]
    return name_without_extension


def start_lab_session():

    global the_humanoid
    global gui_status,gui_err_msg

    lab_logger.info("Start_the lab session...")
    scn = bpy.context.scene

    library_name = "humanoid_library.blend"
    lib_filepath = os.path.join(the_humanoid.data_path, library_name)
    lamp_names = ["Lamp_back", "Lamp_top", "Lamp_right", "Lamp_left"] #TODO: read from library blend instead hardcoded

    if scn.use_cycles:
        if scn.render.engine != 'CYCLES':
            lab_logger.info("Rendering engine was {0}".format(scn.render.engine))
            scn.render.engine = 'CYCLES'
            lab_logger.info("Rendering engine now is {0}".format(scn.render.engine))

        if scn.use_lamps:
            append_from_blend(lib_filepath, lamp_names)


    obj = None
    is_obj = the_humanoid.looking_for_humanoid_obj()

    if is_obj[0] == "ERROR":
        gui_status = "ERROR_SESSION"
        gui_err_msg = is_obj[1]
        return

    if is_obj[0] == "NO_OBJ":
        append_from_blend(lib_filepath, [scn.characterType])
        if scn.characterType in bpy.data.objects:
            obj = bpy.data.objects[scn.characterType]

    if is_obj[0] == "FOUND":
        obj = the_humanoid.get_object_by_name(is_obj[1])

    if not obj:
        lab_logger.critical("Init failed. Check the log file: {0}".format(log_path))
        gui_status = "ERROR_SESSION"
        gui_err_msg = "Init failed. Check the log file"
    else:
        the_humanoid.init_database()
        if the_humanoid.has_data:
            init_morphing_props(the_humanoid)
            init_categories_props(the_humanoid)
            init_measures_props(the_humanoid)
            init_expression_props(the_humanoid)
            init_presets_props(the_humanoid)
            init_pose_props(the_humanoid)
            init_rnd_generator_props(the_humanoid)
            init_ethnic_props(the_humanoid)
            init_metaparameters_props(the_humanoid)
            init_material_parameters_props(the_humanoid)
            the_humanoid.update_materials()
            if gui_status == "RECOVERY_SESSION":
                lab_logger.info("Re-init the character {0}".format(obj.name))
                if hasattr(obj, "character_ID"):
                    if scn.clean_loading == False:
                        the_humanoid.store_mesh_in_cache()
                    the_humanoid.reset_mesh()
                    the_humanoid.recover_prop_values_from_obj_attr()
                    if scn.clean_loading == False:
                        the_humanoid.restore_mesh_from_cache()
                else:
                    lab_logger.warning("Recovery failed. Character_ID not present")
            gui_status = "ACTIVE_SESSION"

@persistent
def check_manuelbastionilab_session(dummy):
    global the_humanoid
    global gui_status, gui_err_msg
    scn = bpy.context.scene
    if the_humanoid:
        gui_status = "NEW_SESSION"
        is_obj = the_humanoid.looking_for_humanoid_obj()
        if is_obj[0] == "FOUND":
            gui_status = "RECOVERY_SESSION"
            if scn.do_not_ask_again:
                start_lab_session()
        if is_obj[0] == "ERROR":
            gui_status = "ERROR_SESSION"
            gui_err_msg = is_obj[1]
            return

bpy.app.handlers.load_post.append(check_manuelbastionilab_session)

def link_to_scene(obj):
    scn = bpy.context.scene
    if obj.name not in scn.object_bases:
        scn.objects.link(obj)
    else:
        lab_logger.warning("The object {0} is already linked to the scene".format(obj.name))

def append_from_blend(lib_filepath, obj_names):
    scn = bpy.context.scene

    names_of_obj_to_append = []
    for obj_name in obj_names:

        if obj_name in bpy.data.objects:
            lab_logger.warning("An object named {0} is already present in the scene".format(obj_name))
        else:
            names_of_obj_to_append.append(obj_name)

    try:
        with bpy.data.libraries.load(lib_filepath) as (data_from, data_to):
            data_to.objects = names_of_obj_to_append
    except:
        lab_logger.critical("{0} not found".format(lib_filepath))
        return None

    for obj in data_to.objects:
        if obj.name in bpy.data.objects:
            link_to_scene(obj)
            if obj.parent != None:
                link_to_scene(obj.parent)
        else:
            lab_logger.critical("{0} not found in library {1}".format(scn.characterType, library_name))
            return None


def realtime_update(self, context):
    """
    Update the character while the prop slider moves.
    """
    global the_humanoid
    if the_humanoid.bodydata_activated:
        #time1 = time.time()
        scn = bpy.context.scene
        the_humanoid.update_character(category_name = scn.morphingCategory, mode="update_realtime")
        the_humanoid.sync_gui_according_measures()
        #print("realtime_update: {0}".format(time.time()-time1))

def age_update(self, context):
    global the_humanoid
    if the_humanoid.metadata_activated:
        time1 = time.time()
        the_humanoid.calculate_transformation("AGE")

def mass_update(self, context):
    global the_humanoid
    if the_humanoid.metadata_activated:
        the_humanoid.calculate_transformation("FAT")

def tone_update(self, context):
    global the_humanoid
    if the_humanoid.metadata_activated:
        the_humanoid.calculate_transformation("MUSCLE")

def preset_update(self, context):
    """
    Update the character while prop slider moves
    """
    scn = bpy.context.scene
    global the_humanoid
    obj = the_humanoid.get_object()
    filepath = os.path.join(
        the_humanoid.preset_path,
        "".join([obj.preset, ".json"]))
    the_humanoid.load_character(filepath, mix=scn.mix_characters)

def ethnic_update(self, context):
    scn = bpy.context.scene
    global the_humanoid
    obj = the_humanoid.get_object()
    filepath = os.path.join(
        the_humanoid.ethnic_path,
        "".join([obj.ethnic, ".json"]))
    the_humanoid.load_character(filepath, mix=scn.mix_characters)

def pose_update(self, context):
    """
    Load pose quaternions
    """
    global the_humanoid
    obj = the_humanoid.get_object()
    filepath = os.path.join(
        the_humanoid.pose_path,
        "".join([obj.static_pose, ".json"]))
    the_humanoid.load_pose(filepath)

def material_update(self, context):
    global the_humanoid
    the_humanoid.update_materials(float_values_only = True)

def measure_units_update(self, context):
    global the_humanoid
    the_humanoid.sync_gui_according_measures()


def expression_update(self, context):
    global the_humanoid
    scn = bpy.context.scene
    obj = the_humanoid.get_object()
    filepath = os.path.join(
        the_humanoid.expression_path,
        "".join([obj.expressions, ".json"]))

    the_humanoid.load_character(filepath, reset_string = "Expression", reset_unassigned=False)
    if scn.realtime_expression_fitting:
        the_humanoid.correct_expressions()

def init_expression_props(humanoid_instance):
    expression_path = humanoid_instance.expression_path
    expression_items = []
    if os.path.isdir(expression_path):
        for database_file in os.listdir(expression_path):
            e_item, extension = os.path.splitext(database_file)
            if "json" in extension:
                expression_items.append((e_item, e_item, e_item))
        expression_items.sort()
        bpy.types.Object.expressions = bpy.props.EnumProperty(
            items=expression_items,
            name="Expressions",
            update=expression_update)
    else:
        lab_logger.warning("{0} not found".format(algorithms.simple_path(humanoid_instance.expression_path)))

def init_morphing_props(humanoid_instance):
    for prop in humanoid_instance.character_data:
        setattr(
            bpy.types.Object,
            prop,
            bpy.props.FloatProperty(
                name=prop,
                min = -5.0,
                max = 5.0,
                soft_min = 0.0,
                soft_max = 1.0,
                precision=3,
                default=0.5,
                update=realtime_update))

def init_measures_props(humanoid_instance):
    for measure_name,measure_val in humanoid_instance.m_engine.measures.items():
        setattr(
            bpy.types.Object,
            measure_name,
            bpy.props.FloatProperty(
                name=measure_name, min=0.0, max=500.0,
                default=measure_val))
    humanoid_instance.sync_gui_according_measures()

def init_categories_props(humanoid_instance):
    categories_enum = []
    for category in the_humanoid.get_categories()  :
        categories_enum.append(
            (category.name, category.name, category.name))

    bpy.types.Scene.morphingCategory = bpy.props.EnumProperty(
        items=categories_enum,
        name="Morphing categories")

def init_presets_props(humanoid_instance):
    preset_items = []
    if os.path.isdir(humanoid_instance.preset_path):
        for database_file in os.listdir(humanoid_instance.preset_path):
            p_item, extension = os.path.splitext(database_file)
            if "json" in extension:
                preset_items.append((p_item, p_item, p_item))
            else:
                lab_logger.warning("Unknow file extension in {0}".format(algorithms.simple_path(preset_path)))
        preset_items.sort()
        bpy.types.Object.preset = bpy.props.EnumProperty(
            items=preset_items,
            name="Types",
            update=preset_update)
    else:
        lab_logger.warning("{0} not found".format(algorithms.simple_path(humanoid_instance.preset_path)))

def init_pose_props(humanoid_instance):
    pose_items = []
    if os.path.isdir(humanoid_instance.pose_path):
        for database_file in os.listdir(humanoid_instance.pose_path):
            po_item, extension = os.path.splitext(database_file)
            if "json" in extension:
                pose_items.append((po_item, po_item, po_item))
        pose_items.sort()
        bpy.types.Object.static_pose = bpy.props.EnumProperty(
            items=pose_items,
            name="Pose",
            update=pose_update)
    else:
        lab_logger.warning("{0} not found".format(algorithms.simple_path(humanoid_instance.pose_path)))

def init_rnd_generator_props(humanoid_instance):

            for bool_prp in humanoid_instance.generator_bool_props:
                bool_name = bool_prp.split("_")[1:]
                bool_name = " ".join(bool_name)
                bool_name.capitalize()
                bool_descr = [s.capitalize() for s in bool_prp.split("_")]
                bool_descr = " ".join(bool_descr)
                setattr(
                    bpy.types.Object,
                    bool_prp,
                    bpy.props.BoolProperty(
                        name=bool_name,
                        description=bool_descr))

            for float_prp in humanoid_instance.generator_float_props:
                float_name = [s.capitalize() for s in float_prp.split("_")]
                float_name = " ".join(float_name)
                setattr(
                    bpy.types.Object,
                    float_prp,
                    bpy.props.FloatProperty(
                        name=float_name, min=0.0, max=1.0,
                        default=0.5))

            bpy.types.Object.random_engine = bpy.props.EnumProperty(
                items = humanoid_instance.generator_levels,
                name = "Engine",
                default = humanoid_instance.generator_levels[0][0])

def init_ethnic_props(humanoid_instance):
    ethnic_items = []
    if os.path.isdir(humanoid_instance.ethnic_path):
        for database_file in os.listdir(humanoid_instance.ethnic_path):
            et_item, extension = os.path.splitext(database_file)
            if "json" in extension:
                ethnic_items.append((et_item, et_item, et_item))
        ethnic_items.sort()
        bpy.types.Object.ethnic = bpy.props.EnumProperty(
            items=ethnic_items,
            name="Phenotype",
            update=ethnic_update)
    else:
        lab_logger.warning("{0} not found".format(algorithms.simple_path(humanoid_instance.ethnic_path)))

def init_metaparameters_props(humanoid_instance):
    for meta_data_prop in humanoid_instance.character_metaproperties.keys():
        upd_function = None

        if "age" in meta_data_prop:
            upd_function = age_update
        if "mass" in meta_data_prop:
            upd_function = mass_update
        if "tone" in meta_data_prop:
            upd_function = tone_update
        if "last" in meta_data_prop:
            upd_function = None

        if "last_" not in meta_data_prop:
            setattr(
                bpy.types.Object,
                meta_data_prop,
                bpy.props.FloatProperty(
                    name=meta_data_prop, min=-1.0, max=1.0,
                    precision=3,
                    default=0.0,
                    update=upd_function))


def init_material_parameters_props(humanoid_instance):

    for material_data_prop, value in humanoid_instance.character_material_properties.items():
        setattr(
            bpy.types.Object,
            material_data_prop,
            bpy.props.FloatProperty(
                name=material_data_prop,
                min = 0.0,
                max = 1.0,
                precision=2,
                update = material_update,
                default=value))


bpy.types.Object.proxy_ID = bpy.props.StringProperty(
    name="human_ID",
    maxlen = 1024,
    default= "-")

bpy.types.Scene.do_not_ask_again = bpy.props.BoolProperty(
    name="Do not ask me again for this scene",
    default = False,
    description="If checked, next time the the file is loaded the init will start automatically")

bpy.types.Scene.clean_loading = bpy.props.BoolProperty(
    name="Regenerate the character",
    default = False,
    description="Clean the manual edits and approximation errors")

bpy.types.Scene.use_cycles = bpy.props.BoolProperty(
    name="Use Cycles materials (needed for skin shaders)",
    default = True,
    description="This is needed in order to use the skin editor and shaders (highly recommended)")

bpy.types.Scene.use_lamps = bpy.props.BoolProperty(
    name="Use poirtrait studio lights (recommended)",
    default = True,
    description="Add a set of lights optimized for poirtrait. Useful during the design of skin (recommended)")

bpy.types.Scene.show_age = bpy.props.BoolProperty(
    name="Age tools",
    default = False,
    description="Modify the age")

bpy.types.Scene.show_parameters = bpy.props.BoolProperty(
    name="Body parameters",
    description="Show parameter controls")

bpy.types.Scene.show_skin_editor = bpy.props.BoolProperty(
    name="Skin editor tools",
    description="Show skin controls",
    )

bpy.types.Scene.show_subdivision = bpy.props.BoolProperty(
    name="Displacement preview",
    description="Preview the displacement with subsurf (this option disables some lab tools, too CPU expensive in subdivision mode)",
    )

bpy.types.Scene.show_measures = bpy.props.BoolProperty(
    name="Body measures",
    description="Show measures controls")

bpy.types.Scene.measure_filter = bpy.props.StringProperty(
    name="Filter",
    default = "",
    description="Filter the measures to show")

bpy.types.Scene.show_automodelling = bpy.props.BoolProperty(
    name="Automodelling tools",
    description="Show automodelling controls")

bpy.types.Scene.show_expressions = bpy.props.BoolProperty(
    name="Expression tools",
    description="Show expressions controls")

bpy.types.Scene.show_poses = bpy.props.BoolProperty(
    name="Pose tools",
    description="Show poses controls")

bpy.types.Scene.show_proxies = bpy.props.BoolProperty(
    name="Proxies tools",
    description="Show proxies controls")

bpy.types.Scene.show_finalize = bpy.props.BoolProperty(
    name="Finalize",
    description="Finalize the character")

bpy.types.Scene.show_utilities = bpy.props.BoolProperty(
    name="Utilities",
    description="Quick access to some Blender tools")

bpy.types.Scene.show_files = bpy.props.BoolProperty(
    name="Files import-export",
    description="Show file controls")

bpy.types.Scene.show_random_generator = bpy.props.BoolProperty(
    name="Random generator tools",
    description="Show generator controls")

bpy.types.Scene.mix_characters = bpy.props.BoolProperty(
    name="Mix with current",
    description="Mix templates")

bpy.types.Scene.realtime_expression_fitting = bpy.props.BoolProperty(
    name="Fit expressions",
    description="Fit the expression to character face (slower)")

bpy.types.Scene.characterType = bpy.props.EnumProperty(
    items=HUMANOID_TYPES,
    name="Select",
    default="humanoid_humanf01")



bpy.types.Object.use_inch = bpy.props.BoolProperty(
    name="Inch",
    update = measure_units_update,
    description="Use inch instead of cm")

bpy.types.Object.export_proportions = bpy.props.BoolProperty(
    name="Export proportions",
    description="Include proportions in the exported character file")


class UpdateSkinDisplacement(bpy.types.Operator):
    """
    Calculate and apply the skin displacement
    """
    bl_label = 'Update displacement'
    bl_idname = 'skindisplace.calculate'
    bl_description = 'Calculate and apply the skin details using displace modifier'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        """
        Calculate and apply the skin displacement
        """
        global the_humanoid
        scn = bpy.context.scene
        the_humanoid.update_displacement()
        the_humanoid.update_materials()
        return {'FINISHED'}


class DisableSubdivision(bpy.types.Operator):
    """
    Disable subdivision surface
    """
    bl_label = 'Disable subdivision preview'
    bl_idname = 'subdivision.disable'
    bl_description = 'Disable subdivision modifier'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        """
        Calculate and apply the skin displacement
        """
        global the_humanoid
        scn = bpy.context.scene

        if the_humanoid.get_subd_visibility() == True:
            the_humanoid.set_subd_visibility(False)
        return {'FINISHED'}

class EnableSubdivision(bpy.types.Operator):
    """
    Enable subdivision surface
    """
    bl_label = 'Enable subdivision preview'
    bl_idname = 'subdivision.enable'
    bl_description = 'Enable subdivision preview (Warning: it will slow down the morphing)'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        """
        Calculate and apply the skin displacement
        """
        global the_humanoid
        scn = bpy.context.scene

        if the_humanoid.get_subd_visibility() == False:
            the_humanoid.set_subd_visibility(True)
        return {'FINISHED'}

class DisableDisplacement(bpy.types.Operator):
    """
    Disable displacement modifier
    """
    bl_label = 'Disable displacement preview'
    bl_idname = 'displacement.disable'
    bl_description = 'Disable displacement modifier'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        """
        Calculate and apply the skin displacement
        """
        global the_humanoid
        scn = bpy.context.scene

        if the_humanoid.get_disp_visibility() == True:
            the_humanoid.set_disp_visibility(False)
        return {'FINISHED'}

class EnableDisplacement(bpy.types.Operator):
    """
    Enable displacement modifier
    """
    bl_label = 'Enable displacement preview'
    bl_idname = 'displacement.enable'
    bl_description = 'Enable displacement preview (Warning: it will slow down the morphing)'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        """
        Calculate and apply the skin displacement
        """
        global the_humanoid
        scn = bpy.context.scene

        if the_humanoid.get_disp_visibility() == False:
            the_humanoid.set_disp_visibility(True)
        return {'FINISHED'}


class FinalizeCharacter(bpy.types.Operator):
    """
    Convert the expression morphings to Blender standard shape keys
    """
    bl_label = 'Finalize'
    bl_idname = 'finalize.character'
    bl_description = 'Finalize, converting the parameters in shapekeys. Warning: after the conversion the character will be no longer modifiable using ManuelbastioniLAB tools'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        """
        Fit the expressions to character and then convert them.
        """
        global the_humanoid
        global gui_status
        the_humanoid.correct_expressions(correct_all=True)
        the_humanoid.m_engine.convert_all_to_blshapekeys()
        the_humanoid.delete_all_properties()
        the_humanoid.rename_materials()
        the_humanoid.rename_obj()
        gui_status = "NEW_SESSION"
        return {'FINISHED'}

class ResetParameters(bpy.types.Operator):
    """
    Reset all morphings.
    """
    bl_label = 'Reset All'
    bl_idname = 'reset.allproperties'
    bl_description = 'Reset all character parameters'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.reset_character()
        return {'FINISHED'}

class ResetExpressions(bpy.types.Operator):
    """
    Reset all morphings.
    """
    bl_label = 'Reset Expression'
    bl_idname = 'reset.expression'
    bl_description = 'Reset the expression'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def reset_expression(self):
        global the_humanoid
        scn = bpy.context.scene
        obj = the_humanoid.get_object()
        filepath = os.path.join(
            the_humanoid.expression_path,
            "neutral.json")

        the_humanoid.load_character(filepath, reset_string = "Expression", reset_unassigned=False)

    def execute(self, context):
        self.reset_expression()
        return {'FINISHED'}


class Reset_category(bpy.types.Operator):
    """
    Reset the parameters for the currently selected category
    """
    bl_label = 'Reset category'
    bl_idname = 'reset.categoryonly'
    bl_description = 'Reset the parameters for the current category'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        scn = bpy.context.scene
        the_humanoid.reset_category(scn.morphingCategory)
        return {'FINISHED'}


class CharacterGenerator(bpy.types.Operator):
    """
    Generate a new character using the specified parameters.
    """
    bl_label = 'Generate'
    bl_idname = 'character.generator'
    bl_description = 'Generate a new character according the parameters.'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.generate_character()
        return {'FINISHED'}

class ExpDisplacementImage(bpy.types.Operator, ExportHelper):
    """Export parameters for the character"""
    bl_idname = "export.dispimage"
    bl_label = "Save displacement image"
    filename_ext = ".png"
    filter_glob = bpy.props.StringProperty(
        default="*.png",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid
        the_humanoid.save_skin_displacement_image(self.filepath)
        return {'FINISHED'}

class ExpDermalImage(bpy.types.Operator, ExportHelper):
    """Export parameters for the character"""
    bl_idname = "export.dermimage"
    bl_label = "Save dermal image"
    filename_ext = ".png"
    filter_glob = bpy.props.StringProperty(
        default="*.png",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid
        the_humanoid.save_skin_dermal_image(self.filepath)
        return {'FINISHED'}

class ExpSubDermalImage(bpy.types.Operator, ExportHelper):
    """Export parameters for the character"""
    bl_idname = "export.subdermimage"
    bl_label = "Save subdermal image"
    filename_ext = ".png"
    filter_glob = bpy.props.StringProperty(
        default="*.png",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid
        the_humanoid.save_skin_subdermal_image(self.filepath)
        return {'FINISHED'}

class ExpCharacter(bpy.types.Operator, ExportHelper):
    """Export parameters for the character"""
    bl_idname = "export.character"
    bl_label = "Export character"
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid
        the_humanoid.save_character(self.filepath)
        return {'FINISHED'}

class ExpMeasures(bpy.types.Operator, ExportHelper):
    """Export parameters for the character"""
    bl_idname = "export.measures"
    bl_label = "Export measures"
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid
        the_humanoid.export_measures(self.filepath)
        return {'FINISHED'}


class ImpCharacter(bpy.types.Operator, ImportHelper):
    """
    Import parameters for the character
    """
    bl_idname = "import.character"
    bl_label = "Import character"
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid

        char_data = the_humanoid.load_character(self.filepath)
        return {'FINISHED'}

class ImpMeasures(bpy.types.Operator, ImportHelper):
    """
    Import parameters for the character
    """
    bl_idname = "import.measures"
    bl_label = "Import measures"
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid
        the_humanoid.import_measures(self.filepath)
        return {'FINISHED'}

class SaveProxy(bpy.types.Operator):
    """
    Calibrate the proxy object in order to be automatically adapted to body variation
    of the current humanoid. The data is calculated and stored the user temp directory.
    """

    bl_label = 'Calibrate Proxy'
    bl_idname = 'proxy.save'
    bl_description = 'Register proxy for auto fitting'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        proxy_status = the_humanoid.validate_proxy_for_saving()

        if proxy_status == "OK":
            the_humanoid.save_proxy()
            self.report({'INFO'}, "Proxy calibrated. Its data is saved to temp folder")
        else:
            self.report({'ERROR'}, proxy_status)
        return {'FINISHED'}



class FixProxyScale(bpy.types.Operator):
    """
    The proxy scale must be the same of humanoid scale. Both them should be 1.
    This tool set the scale of proxy equal to the scale of humanoid.
    """

    bl_label = 'Correct proxy scale'
    bl_idname = 'proxy.fixscale'
    bl_description = 'Set the proxy scale equal to humanoid scale'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        proxy_status = the_humanoid.validate_proxy_for_selection()
        if proxy_status == "OK":
            the_humanoid.scale_proxy_to_human()
        else:
            self.report({'ERROR'}, proxy_status)
        return {'FINISHED'}

class FixProxyModifiers(bpy.types.Operator):
    """
    Subdivision and armature modifiers can create unpredictable results if they are enabled during the calibration and fitting. Disable them.

    """

    bl_label = 'Disable proxy modifiers'
    bl_idname = 'proxy.fixmodifiers'
    bl_description = 'Disable modifiers that can create problems with proxies'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        proxy_status = the_humanoid.validate_proxy_for_selection()
        if proxy_status == "OK":
            the_humanoid.disable_proxy_modifiers()
        else:
            self.report({'ERROR'}, proxy_status)
        return {'FINISHED'}



class FixHumanModifiers(bpy.types.Operator):
    """
    Subdivision and armature modifiers can create unpredictable results if they are enabled during the calibration and fitting. Disable them.

    """

    bl_label = 'Disable Humanoid subdivision'
    bl_idname = 'proxy.fixhumanmodifiers'
    bl_description = 'Disable modifiers that can create problems with proxies'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.disable_human_modifiers()
        return {'FINISHED'}


class FixProxyOrigin(bpy.types.Operator):
    """
    The proxy must have the same location of the humanoid. This tool move the proxy origin (not the geometry) to the object location.
    """

    bl_label = 'Correct proxy origin'
    bl_idname = 'proxy.fixorigin'
    bl_description = 'Move the proxy origin (not the geometry) to the humanoid location.'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        proxy_status = the_humanoid.validate_proxy_for_selection()
        if proxy_status == "OK":
            the_humanoid.proxy_origin_to_human_origin()
        else:
            self.report({'ERROR'}, proxy_status)
        return {'FINISHED'}


class LoadProxy(bpy.types.Operator):
    """
    For each proxy in the scene, load the data and then fit it.
    """

    bl_label = 'Fit Proxies'
    bl_idname = 'proxy.load'
    bl_description = 'Fit all registered proxies to the character'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}


    def execute(self, context):
        global the_humanoid
        proxy_status = the_humanoid.validate_proxy_for_loading()
        if proxy_status == "OK":
            the_humanoid.load_proxy()
        else:
            self.report({'WARNING'}, proxy_status)
        return {'FINISHED'}


class ApplyMeasures(bpy.types.Operator):
    """
    Fit the character to the measures
    """

    bl_label = 'Update character'
    bl_idname = 'measures.apply'
    bl_description = 'Fit the character to the measures'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.automodelling(use_measures_from_GUI=True)
        return {'FINISHED'}


class AutoModelling(bpy.types.Operator):
    """
    Fit the character to the measures
    """

    bl_label = 'Auto modelling'
    bl_idname = 'auto.modelling'
    bl_description = 'Auto modelling'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.automodelling(use_measures_from_current_obj=True)
        return {'FINISHED'}

class AutoModellingMix(bpy.types.Operator):
    """
    Fit the character to the measures
    """

    bl_label = 'Smooth'
    bl_idname = 'auto.modellingmix'
    bl_description = 'Auto modelling2'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.automodelling(use_measures_from_current_obj=True, mix = True)
        return {'FINISHED'}

class ResetPose(bpy.types.Operator):
    """
    For each proxy in the scene, load the data and then fit it.
    """

    bl_label = 'Reset pose'
    bl_idname = 'pose.reset'
    bl_description = 'Reset the character pose'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.reset_pose()
        return {'FINISHED'}


class SavePose(bpy.types.Operator, ExportHelper):
    """Export pose"""
    bl_idname = "pose.save"
    bl_label = "Save pose"
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid
        the_humanoid.save_pose(self.filepath)
        return {'FINISHED'}

class LoadPose(bpy.types.Operator, ImportHelper):
    """
    Import parameters for the character
    """
    bl_idname = "pose.load"
    bl_label = "Load pose"
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid

        char_data = the_humanoid.load_pose(self.filepath)
        return {'FINISHED'}



class StartSession(bpy.types.Operator):
    bl_idname = "init.character"
    bl_label = "Init character"
    bl_description = 'Create the character selected above'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        start_lab_session()
        return {'FINISHED'}


class ManuelLabPanel(bpy.types.Panel):

    bl_label = "ManuelbastioniLAB {0}.{1}.{2}".format(bl_info["version"][0],bl_info["version"][1],bl_info["version"][2])
    bl_idname = "OBJECT_PT_characters01"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = "ManuelBastioniLAB"


    def draw(self, context):

        global the_humanoid,gui_status,gui_err_msg
        scn = bpy.context.scene

        if gui_status == "ERROR_SESSION":
            box = self.layout.box()
            box.alert = True
            box.label(gui_err_msg, icon="ERROR")
            #box.prop(scn,'use_cycles')
            #if scn.use_cycles:
                #box.prop(scn,'use_lamps')
            #box.prop(scn,'clean_loading')
            #box.operator('init.character')
            #box.prop(scn,'do_not_ask_again')

        if gui_status == "RECOVERY_SESSION":
            box = self.layout.box()
            box.label("I detected an existent lab session")
            box.label("To try a recover, press init button")
            box.prop(scn,'use_cycles')
            if scn.use_cycles:
                box.prop(scn,'use_lamps')
            box.prop(scn,'clean_loading')
            box.operator('init.character')
            box.prop(scn,'do_not_ask_again')

        if gui_status == "NEW_SESSION":
            box = self.layout.box()
            box.prop(scn, 'characterType')
            box.prop(scn,'use_cycles')
            if scn.use_cycles:
                box.prop(scn,'use_lamps')
            box.operator('init.character')

        if gui_status == "ACTIVE_SESSION":
            obj = the_humanoid.get_object()

            if obj:
                box = self.layout.box()
                sub = box.box()
                sub.label("Meta parameters")
                for meta_data_prop in sorted(the_humanoid.character_metaproperties.keys()):
                    if "last" not in meta_data_prop:
                        sub.prop(obj, meta_data_prop)

                sub = box.box()
                sub.label("Characters library")
                sub.prop(obj, "preset")
                sub.prop(obj, "ethnic")
                sub.prop(scn, 'mix_characters')
                sub.operator("reset.allproperties", icon="RECOVER_AUTO")

                box = self.layout.box()

                box.prop(scn, 'show_expressions')
                if scn.show_expressions:
                    box.prop(obj, "expressions")
                    box.prop(scn, 'realtime_expression_fitting')
                    box.operator("reset.expression", icon="RECOVER_AUTO")

                box = self.layout.box()
                box.prop(scn, 'show_random_generator')
                if scn.show_random_generator:
                    box.prop(obj, "random_engine")
                    box.label("Preserve:")
                    prop_id = 0
                    while prop_id < len(the_humanoid.generator_bool_props)-1:
                        row = box.row()
                        row.prop(obj, the_humanoid.generator_bool_props[prop_id])
                        row.prop(obj, the_humanoid.generator_bool_props[prop_id+1])
                        prop_id += 2

                    if obj.set_tone_and_mass:
                        for prop in the_humanoid.generator_float_props:
                            box.prop(obj, prop)
                    box.operator("character.generator", icon="FILE_REFRESH")

                box = self.layout.box()
                row = box.row()
                row.prop(scn, 'show_parameters')
                if scn.show_parameters:
                    the_humanoid.bodydata_activated = True
                    if the_humanoid.exist_measure_database():
                        row.prop(scn, 'show_measures')
                    split = box.split()

                    col = split.column()
                    col.label("PARAMETERS")
                    col.prop(scn, "morphingCategory")

                    for prop in the_humanoid.get_properties_in_category(scn.morphingCategory):
                        if hasattr(obj, prop):
                            col.prop(obj, prop)

                    if the_humanoid.exist_measure_database() and scn.show_measures:
                        col = split.column()
                        col.label("DIMENSIONS")
                        col.prop(obj, 'use_inch')
                        col.prop(scn, 'measure_filter')
                        col.operator("measures.apply")
                        m_unit = "cm"
                        if obj.use_inch:
                            m_unit = "Inches"
                        col.label("Height: {0} {1}".format(round(getattr(obj, "body_height_Z", 0),3),m_unit))
                        for measure in sorted(the_humanoid.measures.keys()):
                            if measure != "body_height_Z":
                                if hasattr(obj, measure):
                                    if scn.measure_filter in measure:
                                        col.prop(obj, measure)

                    sub = box.box()
                    sub.label("RESET")
                    sub.operator("reset.categoryonly")
                    sub.operator("reset.allproperties")

                box = self.layout.box()
                if the_humanoid.exist_measure_database():
                    box.prop(scn, 'show_automodelling')
                    if scn.show_automodelling:
                        box.operator("auto.modelling")
                        box.operator("auto.modellingmix")
                else:
                    box.enabled = False
                    box.label("No measure data found for this character", icon='INFO')


                box = self.layout.box()
                box.prop(scn, 'show_poses')
                if scn.show_poses:
                    box.prop(obj, "static_pose")
                    box.operator("pose.reset", icon='ARMATURE_DATA')
                    box.operator("pose.load", icon='IMPORT')
                    box.operator("pose.save", icon='EXPORT')

                box = self.layout.box()
                box.enabled = True
                box.prop(scn, 'show_skin_editor')

                if scn.render.engine != 'CYCLES':
                    box.enabled = False
                    box.label("Skin editor requires Cycles", icon='INFO')
                if scn.show_skin_editor:
                    if the_humanoid.exist_texture_database():
                        box.operator("skindisplace.calculate")
                        if the_humanoid.get_disp_visibility() == False:
                            box.operator("displacement.enable", icon='MOD_DISPLACE')
                        else:
                            box.operator("displacement.disable", icon='X')
                    if the_humanoid.get_subd_visibility() == False:
                        box.operator("subdivision.enable", icon='MOD_SUBSURF')
                        box.label("Subd. preview is very CPU intensive", icon='ERROR')
                    else:
                        box.operator("subdivision.disable", icon='X')
                        box.label("Disable subdivision to increase the performance", icon='INFO')
                    for material_data_prop in sorted(the_humanoid.character_material_properties.keys()):
                        box.prop(obj, material_data_prop)

                    if the_humanoid.exist_texture_database():
                        sub = box.box()
                        sub.label("Export textures")
                        sub.operator("export.dermimage", icon='EXPORT')
                        sub.operator("export.subdermimage", icon='EXPORT')
                        sub.operator("export.dispimage", icon='EXPORT')

                box = self.layout.box()
                box.prop(scn, 'show_proxies')
                if scn.show_proxies:
                    box.label("Experimental feature", icon='ERROR')
                    box.operator("proxy.save", icon="MOD_CLOTH")
                    box.operator("proxy.load", icon="MOD_CLOTH")

                    sub = box.box()
                    sub.label("Proxy utilities")
                    sub.operator("proxy.fixorigin")
                    sub.operator("proxy.fixscale")
                    sub.operator("proxy.fixhumanmodifiers")
                    sub.operator("proxy.fixmodifiers")

                box = self.layout.box()
                box.prop(scn, 'show_files')
                if scn.show_files:
                    sub = box.box()
                    sub.label("Character data (.json)")
                    sub.prop(obj, 'export_proportions')
                    sub.operator("export.character", icon='EXPORT')
                    sub.operator("import.character", icon='IMPORT')


                    sub = box.box()
                    if the_humanoid.exist_measure_database():
                        sub.enabled = True
                    else:
                        sub.enabled = False
                        sub.label("Measure data not present", icon='INFO')
                    sub.label("Character measures (.json)")
                    sub.operator("export.measures", icon='EXPORT')
                    sub.operator("import.measures", icon='IMPORT')

                box = self.layout.box()
                box.prop(scn, 'show_finalize')
                if scn.show_finalize:
                    box.operator("finalize.character", icon='FREEZE')

            else:
                gui_status = "NEW_SESSION"

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()





