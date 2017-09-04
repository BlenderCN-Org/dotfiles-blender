# Addon Info
bl_info = {
    "name": "Real Camera",
    "description": "Real Camera Controls and Effects",
    "author": "Wolf",
    "version": (1, 1),
    "blender": (2, 77, 0),
    "location": "Properties > Camera",
    "wiki_url": "http://3dwolf.weebly.com/camera.html",
    "tracker_url": "http://3dwolf.weebly.com/camera.html",
    "support": "OFFICIAL",
    "category": "Compositing"
    }


# Import
import bpy
import os
import mathutils
from bpy.props import *
import bpy.utils.previews
from bpy.types import WindowManager


#Update##############################################################

# Update Toggle
def toggle_update(self, context):
    settings = context.scene.camera_settings

    if not settings.enabled:

        #########Clear Nodes#################################################
        # Switch On Nodes and get Reference
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        
        # Clear Nodes
        for node in tree.nodes:
            tree.nodes.remove(node)
        
        # Input Node
        layer_node = tree.nodes.new(type='CompositorNodeRLayers')
        layer_node.location = 0,0

        # Output Node
        comp_node = tree.nodes.new('CompositorNodeComposite')
        comp_node.location = 200, 0

        # Link
        links = tree.links
        links.new(layer_node.outputs[0], comp_node.inputs[0])
        links.new(layer_node.outputs[1], comp_node.inputs[1])

        # Get Selected Camera Info
        obj = bpy.context.active_object
        name = obj.name

        loc_x = bpy.data.objects[name].location.x
        loc_y = bpy.data.objects[name].location.y
        loc_z = bpy.data.objects[name].location.z

        rot_x = bpy.data.objects[name].rotation_euler.x
        rot_y = bpy.data.objects[name].rotation_euler.y
        rot_z = bpy.data.objects[name].rotation_euler.z

        # Create Camera and move it to the previous point
        size = 1
        cam = bpy.data.cameras.new("Camera")
        cam.name = 'Camera'
        cam_ob = bpy.data.objects.new("Camera", cam)
        bpy.context.scene.objects.link(cam_ob)

        bpy.data.objects["Camera"].location.x = loc_x
        bpy.data.objects["Camera"].location.y = loc_y
        bpy.data.objects["Camera"].location.z = loc_z

        bpy.data.objects["Camera"].rotation_euler.x = rot_x
        bpy.data.objects["Camera"].rotation_euler.y = rot_y
        bpy.data.objects["Camera"].rotation_euler.z = rot_z

        bpy.data.objects["Camera"].scale.x = size
        bpy.data.objects["Camera"].scale.y = size
        bpy.data.objects["Camera"].scale.z = size

        # Delete Old Camera and Change Name
        bpy.ops.object.select_all(action='DESELECT')
        o = bpy.data.objects[name]
        o.select = True
        bpy.context.scene.objects.active = o
        bpy.ops.object.delete()
        name = "Camera"
        bpy.context.scene.camera = bpy.data.objects[name]

        # Delete Flash
        bpy.ops.object.select_all(action='DESELECT')
        o = bpy.data.objects['Flash']
        o.select = True
        bpy.context.scene.objects.active = o
        bpy.ops.object.delete()

        # Delete Flash Material
        bpy.data.materials.remove(bpy.data.materials["Flash"])

        # Select Camera
        bpy.ops.object.select_all(action='DESELECT')
        o = bpy.data.objects["Camera"]
        o.select = True
        bpy.context.scene.objects.active = o

        # Reset Limits
        bpy.data.cameras[name].show_limits = False
        # Reset Motion Blur
        bpy.context.scene.render.use_motion_blur = False
        # Change Aperture to FSTOP
        bpy.context.object.data.cycles.aperture_type = 'RADIUS'

    else:

        effects = bpy.context.scene.camera_effects.effects
        if effects == False:
            ######### Nodes #####################################################
            # Switch On Nodes and get Reference
            bpy.context.scene.use_nodes = True
            tree = bpy.context.scene.node_tree
            
            # Clear Nodes
            for node in tree.nodes:
                tree.nodes.remove(node)
            
            # Input Node
            layer_node = tree.nodes.new(type='CompositorNodeRLayers')
            layer_node.location = 0,0

            # Output Node
            comp_node = tree.nodes.new('CompositorNodeComposite')
            comp_node.location = 200, 0

            # Link
            links = tree.links
            links.new(layer_node.outputs[0], comp_node.inputs[0])
            links.new(layer_node.outputs[1], comp_node.inputs[1])

        else:
            ######### Nodes #####################################################
            # Switch On Nodes and get Reference
            bpy.context.scene.use_nodes = True
            tree = bpy.context.scene.node_tree
            
            # Clear Nodes
            for node in tree.nodes:
                tree.nodes.remove(node)

            # Append Lens Flare
            bpy.ops.wm.append (directory = os.path.join(os.path.dirname(__file__), "Lens Flare.blend/NodeTree/"), filepath="Lens Flare.blend", filename="Lens Flare")
            # Append Bokeh
            bpy.ops.wm.append (directory = os.path.join(os.path.dirname(__file__), "Lens Flare.blend/NodeTree/"), filepath="Lens Flare.blend", filename="Bokeh")
            
            # Input Node
            layer_node = tree.nodes.new(type='CompositorNodeRLayers')
            layer_node.location = 0,0

            # Output Node
            comp_node = tree.nodes.new('CompositorNodeComposite')
            comp_node.location = 800, 0

            # Lens Flare Node
            flare_node = tree.nodes.new(type='CompositorNodeGroup')
            flare_node.node_tree = bpy.data.node_groups["Lens Flare"]
            flare_node.location = 200, 200

            # Bokeh Node
            bokeh_node = tree.nodes.new(type='CompositorNodeGroup')
            bokeh_node.node_tree = bpy.data.node_groups["Bokeh"]
            bokeh_node.location = 400, 0

            # Lens Distortion Node
            lens_node = tree.nodes.new('CompositorNodeLensdist')
            lens_node.location = 200,0

            # Mix Node 1
            mix1_node = tree.nodes.new('CompositorNodeMixRGB')
            mix1_node.location = 400, 200

            # Mix Node 2
            mix2_node = tree.nodes.new('CompositorNodeMixRGB')
            mix2_node.location = 600, 100

            # Link
            links = tree.links
            links.new(layer_node.outputs[0], lens_node.inputs[0])
            links.new(layer_node.outputs[0], flare_node.inputs[0])
            links.new(flare_node.outputs[0], mix1_node.inputs[2])
            links.new(lens_node.outputs[0], mix1_node.inputs[1])
            links.new(mix1_node.outputs[0], mix2_node.inputs[1])
            links.new(layer_node.outputs[0], bokeh_node.inputs[0])
            links.new(bokeh_node.outputs[0], mix2_node.inputs[2])
            links.new(mix2_node.outputs[0], comp_node.inputs[0])
            links.new(layer_node.outputs[1], comp_node.inputs[1])

            # Set Fit
            bpy.context.scene.node_tree.nodes['Lens Distortion'].use_fit = True

            # Set Add Nodes
            bpy.context.scene.node_tree.nodes['Mix'].blend_type = 'ADD'
            bpy.context.scene.node_tree.nodes['Mix.001'].blend_type = 'ADD'


        # Get Selected Camera Info
        obj = bpy.context.active_object
        name = obj.name

        loc_x = bpy.data.objects[name].location.x
        loc_y = bpy.data.objects[name].location.y
        loc_z = bpy.data.objects[name].location.z

        rot_x = bpy.data.objects[name].rotation_euler.x
        rot_y = bpy.data.objects[name].rotation_euler.y
        rot_z = bpy.data.objects[name].rotation_euler.z
    
        # Create Camera
        size = 0.037
        cam = bpy.data.cameras.new("Real Camera")
        cam.name = 'Real Camera'
        cam_ob = bpy.data.objects.new("Real Camera", cam)
        bpy.context.scene.objects.link(cam_ob)
        '''cam_name = bpy.data.cameras[cam.name]'''

        # Camera Size
        bpy.data.objects["Real Camera"].scale.x = size
        bpy.data.objects["Real Camera"].scale.y = size
        bpy.data.objects["Real Camera"].scale.z = size

        # Lock Camera Scale
        bpy.data.objects["Real Camera"].lock_scale = [True, True, True]

        # Append Flash
        bpy.ops.wm.append (directory = os.path.join(os.path.dirname(__file__), "Lens Flare.blend/Object/"), filepath="Lens Flare.blend", filename="Flash")

        # Delete Old Camera and Change Name
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[name].select = True
        bpy.ops.object.delete()
        name = "Real Camera"
        bpy.context.scene.camera = bpy.data.objects[name]

        # Select Flash
        bpy.ops.object.select_all(action='DESELECT')
        o = bpy.data.objects["Flash"]
        o.select = True
        bpy.context.scene.objects.active = o

        # Select Camera
        o = bpy.data.objects["Real Camera"]
        o.select = True
        bpy.context.scene.objects.active = o

        # Parent
        bpy.ops.object.parent_set()

        # Camera Translate
        bpy.data.objects["Real Camera"].location.x = loc_x
        bpy.data.objects["Real Camera"].location.y = loc_y
        bpy.data.objects["Real Camera"].location.z = loc_z

        # Camera Rotate
        bpy.data.objects["Real Camera"].rotation_euler.x = rot_x
        bpy.data.objects["Real Camera"].rotation_euler.y = rot_y
        bpy.data.objects["Real Camera"].rotation_euler.z = rot_z

        # Select Camera
        bpy.ops.object.select_all(action='DESELECT')
        o = bpy.data.objects["Real Camera"]
        o.select = True
        bpy.context.scene.objects.active = o

        # Invisible Flash
        bpy.data.objects["Flash"].hide = True
        bpy.data.objects["Flash"].hide_render = True

        # Set Motion Blur
        bpy.context.scene.render.use_motion_blur = True
        # Set Limits
        bpy.data.cameras[name].show_limits = True
        # Set Metric System
        bpy.context.scene.unit_settings.system = 'METRIC'
        # Change Aperture to FSTOP
        bpy.data.cameras["Real Camera"].cycles.aperture_type = 'FSTOP'

        # Update to fix the visual issue
        bpy.data.cameras["Real Camera"].cycles.aperture_fstop = 1.2
        bpy.context.scene.camera_settings.shutter_speed = 0.05
        bpy.context.scene.camera_settings.iso = 160
        bpy.data.cameras["Real Camera"].dof_distance = 1
        bpy.data.cameras["Real Camera"].lens = 35
        bpy.context.scene.camera_effects.chromatic_aberration = 0.01
        bpy.context.scene.camera_effects.lens_distortion = 0.01


# Update Aperture
def update_aperture(self, context):
    bpy.context.object.data.cycles.aperture_fstop = bpy.context.scene.camera_settings.aperture
# Update Shutter Speed
def update_shutter_speed(self, context):
    fps = bpy.context.scene.render.fps
    value = bpy.context.scene.camera_settings.shutter_speed
    motion = fps*value
    bpy.context.scene.render.motion_blur_shutter = motion
# Update ISO
def update_iso(self, context):
    iso = bpy.context.scene.camera_settings.iso
    exp = iso/160
    bpy.context.scene.cycles.film_exposure = exp
    
# Update Flash
def update_flash(self, context):
    energy = bpy.context.scene.camera_settings.flash
    e = energy*100
    bpy.data.materials["Flash"].node_tree.nodes["Emission"].inputs[1].default_value = e

    # Invisible Flash if energy is 0
    if e == 0:
        bpy.data.objects["Flash"].hide = True
        bpy.data.objects["Flash"].hide_render = True
    else:
        bpy.data.objects["Flash"].hide = False
        bpy.data.objects["Flash"].hide_render = False

# Update Focus Point
def update_focus_point(self, context):
    bpy.context.object.data.dof_distance = bpy.context.scene.camera_settings.focus_point
# Update Zoom
def update_zoom(self, context):
    bpy.context.object.data.lens = bpy.context.scene.camera_settings.zoom

# Update Effects
def update_effects(self, context):
    effects = bpy.context.scene.camera_effects.effects
    if effects == False:
        ######### Nodes #####################################################
        # Switch On Nodes and get Reference
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        
        # Clear Nodes
        for node in tree.nodes:
            tree.nodes.remove(node)
        
        # Input Node
        layer_node = tree.nodes.new(type='CompositorNodeRLayers')
        layer_node.location = 0,0

        # Output Node
        comp_node = tree.nodes.new('CompositorNodeComposite')
        comp_node.location = 200, 0

        # Link
        links = tree.links
        links.new(layer_node.outputs[0], comp_node.inputs[0])
        links.new(layer_node.outputs[1], comp_node.inputs[1])

    else:
        ######### Nodes #####################################################
        # Switch On Nodes and get Reference
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        
        # Clear Nodes
        for node in tree.nodes:
            tree.nodes.remove(node)

        # Append Lens Flare
        bpy.ops.wm.append (directory = os.path.join(os.path.dirname(__file__), "Lens Flare.blend/NodeTree/"), filepath="Lens Flare.blend", filename="Lens Flare")
        # Append Bokeh
        bpy.ops.wm.append (directory = os.path.join(os.path.dirname(__file__), "Lens Flare.blend/NodeTree/"), filepath="Lens Flare.blend", filename="Bokeh")
        
        # Input Node
        layer_node = tree.nodes.new(type='CompositorNodeRLayers')
        layer_node.location = 0,0

        # Output Node
        comp_node = tree.nodes.new('CompositorNodeComposite')
        comp_node.location = 800, 0

        # Lens Flare Node
        flare_node = tree.nodes.new(type='CompositorNodeGroup')
        flare_node.node_tree = bpy.data.node_groups["Lens Flare"]
        flare_node.location = 200, 200

        # Bokeh Node
        bokeh_node = tree.nodes.new(type='CompositorNodeGroup')
        bokeh_node.node_tree = bpy.data.node_groups["Bokeh"]
        bokeh_node.location = 400, 0

        # Lens Distortion Node
        lens_node = tree.nodes.new('CompositorNodeLensdist')
        lens_node.location = 200,0

        # Mix Node 1
        mix1_node = tree.nodes.new('CompositorNodeMixRGB')
        mix1_node.location = 400, 200

        # Mix Node 2
        mix2_node = tree.nodes.new('CompositorNodeMixRGB')
        mix2_node.location = 600, 100

        # Link
        links = tree.links
        links.new(layer_node.outputs[0], lens_node.inputs[0])
        links.new(layer_node.outputs[0], flare_node.inputs[0])
        links.new(flare_node.outputs[0], mix1_node.inputs[2])
        links.new(lens_node.outputs[0], mix1_node.inputs[1])
        links.new(mix1_node.outputs[0], mix2_node.inputs[1])
        links.new(layer_node.outputs[0], bokeh_node.inputs[0])
        links.new(bokeh_node.outputs[0], mix2_node.inputs[2])
        links.new(mix2_node.outputs[0], comp_node.inputs[0])
        links.new(layer_node.outputs[1], comp_node.inputs[1])
        
        # Set Fit
        bpy.context.scene.node_tree.nodes['Lens Distortion'].use_fit = True

        # Set Add Nodes
        bpy.context.scene.node_tree.nodes['Mix'].blend_type = 'ADD'
        bpy.context.scene.node_tree.nodes['Mix.001'].blend_type = 'ADD'

        # Update to fix the visual issue
        bpy.context.object.data.cycles.aperture_fstop = 1.2
        bpy.context.scene.render.motion_blur_shutter = 0.05
        bpy.context.scene.cycles.film_exposure = 160
        bpy.data.materials["Flash"].node_tree.nodes["Emission"].inputs[1].default_value = 0
        bpy.context.object.data.dof_distance = 1
        bpy.context.object.data.lens = 35
        bpy.context.scene.camera_effects.chromatic_aberration = 0.01
        bpy.context.scene.camera_effects.lens_distortion = 0.01


# Update Lens Type
def update_lens_type(self, context):
    if bpy.context.scene.camera_effects.lens_type == True:
        bpy.context.scene.node_tree.nodes['Lens Distortion'].use_projector = False
    else:
        bpy.context.scene.node_tree.nodes['Lens Distortion'].use_projector = True
# Update Longitudinal-Lateral Text
def lens(self, context):
    if bpy.context.scene.camera_effects.lens_type == True:
        return "Longitudinal"
    else:
        return "Lateral"
# Update Longitudinal-Lateral Icon
def select_icon(self, context):
    if bpy.context.scene.camera_effects.lens_type == True:
        return custom_icons["lo"].icon_id
    else:
        return custom_icons["la"].icon_id

# Update Chromatic Aberration
def update_chromatic_aberration(self, context):
    bpy.context.scene.node_tree.nodes['Lens Distortion'].inputs[2].default_value = bpy.context.scene.camera_effects.chromatic_aberration
# Update Lens Distortion
def update_lens_distortion(self, context):
    bpy.context.scene.node_tree.nodes['Lens Distortion'].inputs[1].default_value = bpy.context.scene.camera_effects.lens_distortion
# Update Lens Flare Threshold
def update_lens_flare_threshold(self, context):
    bpy.context.scene.node_tree.nodes['Group'].inputs[1].default_value = bpy.context.scene.camera_effects.lens_flare_threshold
# Update Lens Flare Effect
def update_lens_flare_effect(self, context):
    bpy.context.scene.node_tree.nodes['Group'].inputs[2].default_value = bpy.context.scene.camera_effects.lens_flare_effect
# Update Bokeh Threshold
def update_bokeh_threshold(self, context):
    bpy.context.scene.node_tree.nodes['Group.001'].inputs[1].default_value = bpy.context.scene.camera_effects.bokeh_threshold
# Update Bokeh Effect
def update_bokeh_effect(self, context):
    bpy.context.scene.node_tree.nodes['Group.001'].inputs[2].default_value = bpy.context.scene.camera_effects.bokeh_effect


#Settings############################################################

class CameraSettings(bpy.types.PropertyGroup):
    
    #Toggle
    enabled = bpy.props.BoolProperty(
        name = "Enabled",
        description = "Enable Real Camera",
        default = False,
        update = toggle_update
    )
    
    # Exposure Triangle
    aperture = bpy.props.FloatProperty(
        name = "Aperture",
        description = "Depth of Field, measured in F-Stops",
        min = 0,
        max = 64,
        step = 10,
        precision = 1,
        default = 1.2,
        update = update_aperture
    )
    shutter_speed = bpy.props.FloatProperty(
        name = "Shutter Speed",
        description = "Motion Blur, measured in Seconds",
        min = 0,
        max = float('inf'),
        step = 0.1,
        precision = 3,
        default = 0.05,
        update = update_shutter_speed
    )
    iso = bpy.props.IntProperty(
        name = "ISO",
        description = "Exposure, measured in EVs",
        min = 0,
        max = 1600,
        default = 160,
        update = update_iso
    )
    
    # Mechanics
    flash = bpy.props.FloatProperty(
        name = "Flash",
        description = "Flash Energy",
        min = 0,
        max = float('inf'),
        step = 10,
        precision = 2,
        default = 0,
        update = update_flash
    )
    focus_point = bpy.props.FloatProperty(
        name = "Focus Point",
        description = "Focus Point for the DOF, measured in Meters",
        min = 0,
        max = float('inf'),
        step = 1,
        precision = 2,
        default = 1,
        update = update_focus_point
    )
    zoom = bpy.props.FloatProperty(
        name = "Focal Length",
        description = "Zoom, measured in Millimeters",
        min = 1,
        max = float('inf'),
        step = 10,
        precision = 1,
        default = 35,
        update = update_zoom
    )

    
#Effects#############################################################

class CameraEffects(bpy.types.PropertyGroup):

    effects = bpy.props.BoolProperty(
        name = "Effects",
        description = "Enable Effects",
        default = False,
        update = update_effects
    )

    lens_type = bpy.props.BoolProperty(
        name = "Lens Type",
        description = "Lens Type",
        default = True,
        update = update_lens_type
    )
    chromatic_aberration = bpy.props.FloatProperty(
        name = "Chromatic Aberration",
        description = "Chromatic Aberration Effect",
        min = 0.001,
        max = 1,
        step = 1,
        precision = 3,
        default = 0.01,
        update = update_chromatic_aberration
    )
    lens_distortion = bpy.props.FloatProperty(
        name = "Lens Distortion",
        description = "Lens Distortion Effect",
        min = 0.001,
        max = 1,
        step = 1,
        precision = 3,
        default = 0.01,
        update = update_lens_distortion
    )
    lens_flare_threshold = bpy.props.FloatProperty(
        name = "Lens Threshold",
        description = "Lens Flare Threshold: controls the pixel intensity for getting the Flare effect",
        min = 0,
        max = float('inf'),
        step = 1,
        precision = 3,
        default = 1,
        update = update_lens_flare_threshold
    )
    lens_flare_effect = bpy.props.FloatProperty(
        name = "Lens Effect",
        description = "Lens Flare Effect: controls the intensity of the Lens Flare",
        min = 0,
        max = float('inf'),
        step = 1,
        precision = 3,
        default = 1,
        update = update_lens_flare_effect
    )
    bokeh_threshold = bpy.props.FloatProperty(
        name = "Lens Threshold",
        description = "Lens Flare Threshold: controls the pixel intensity for getting the Bokeh effect",
        min = 0,
        max = float('inf'),
        step = 1,
        precision = 3,
        default = 1,
        update = update_bokeh_threshold
    )
    bokeh_effect = bpy.props.FloatProperty(
        name = "Lens Effect",
        description = "Lens Flare Effect: controls the intensity of the Bokeh",
        min = 0,
        max = float('inf'),
        step = 1,
        precision = 3,
        default = 1,
        update = update_bokeh_effect
    )


#Panel###############################################################

class PreviewsPanel(bpy.types.Panel):
    # Create a Panel in the Camera Properties
    bl_category = "Real Camera"
    bl_label = "Real Camera"
    bl_space_type = 'PROPERTIES'
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    # Draw

    def draw_header(self, context):
        settings = context.scene.camera_settings
        layout = self.layout
        
        layout.prop(settings, 'enabled', text='')
        cam = context.camera
        
    def draw(self, context):
        settings = context.scene.camera_settings
        layout = self.layout
        scn = context.scene
        ob = context.object
        layout.enabled = settings.enabled

        layout.operator("render.render", text="Render", icon='RENDER_STILL')
        
        layout.label("Exposure Triangle", icon_value=custom_icons["exposure_triangle"].icon_id)
        split = layout.split()
        col = split.column(align=True)
        col.prop(settings, 'aperture')
        col.prop(settings, 'shutter_speed')
        col.prop(settings, 'iso')
        
        layout.label("Mechanics", icon_value=custom_icons["mechanics"].icon_id)
        split = layout.split()
        col = split.column(align=True)
        col.prop(settings, 'flash', text="Flash")
        col.prop(settings, 'focus_point')
        col.prop(settings, 'zoom')

        ef = context.scene.camera_effects
        layout.prop(ef, 'effects', icon_value=custom_icons["effects"].icon_id)
        col = layout.column()
        col.active = ef.effects
        col.label("Lens")
        split = col.split()
        col = split.column(align=True)
        col.prop(ef, 'lens_type', text=lens(self, context), icon_value=select_icon(self, context))
        col.prop(ef, 'chromatic_aberration')
        col.prop(ef, 'lens_distortion')
        col.label("Lens Flare")
        split = col.split()
        col = split.column(align=True)
        col.prop(ef, 'lens_flare_threshold', text="Threshold")
        col.prop(ef, 'lens_flare_effect', text="Effect")
        col.label("Bokeh")
        split = col.split()
        col = split.column(align=True)
        col.prop(ef, 'bokeh_threshold', text="Threshold")
        col.prop(ef, 'bokeh_effect', text="Effect")
        

#Register and Unregister############################################

# Register
def register():
    
    bpy.utils.register_module(__name__)
    bpy.types.Scene.camera_settings = bpy.props.PointerProperty(type=CameraSettings)
    bpy.types.Scene.camera_effects = bpy.props.PointerProperty(type=CameraEffects)
    # Icons
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    script_path = os.path.join(os.path.dirname(__file__), "Icons")
    icons_dir = os.path.join(os.path.dirname(script_path), "Icons")
    custom_icons.load("exposure_triangle", os.path.join(icons_dir, "Exposure Triangle.png"), 'IMAGE')
    custom_icons.load("mechanics", os.path.join(icons_dir, "Mechanics.png"), 'IMAGE')
    custom_icons.load("effects", os.path.join(icons_dir, "Effects.png"), 'IMAGE')
    custom_icons.load("lo", os.path.join(icons_dir, "Lo.png"), 'IMAGE')
    custom_icons.load("la", os.path.join(icons_dir, "La.png"), 'IMAGE')


# Unregister
def unregister():

    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.camera_settings
    del bpy.types.Scene.camera_effects
    # Icons
    global custom_icons
    bpy.utils.previews.remove(custom_icons)


if __name__ == "__main__":
    register()
