import bpy
import gpu
import time
from gpu_extras.batch import batch_for_shader

bl_info = {
    "name": "Auto Basis on Leave Edit",
    "author": "Grok",
    "version": (1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > N Panel > Shape Keys tab",
    "description": "Resets active shape key to Basis when leaving Edit mode (except to Sculpt) with 4-second purple halo indication",
    "category": "Mesh",
}

class OutlineIndicator:
    def __init__(self, obj):
        self.obj = obj
        self.start_time = time.time()
        self.shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')

        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()

        if len(mesh.loop_triangles) == 0:
            eval_obj.to_mesh_clear()
            return

        scale = 1.03
        scaled_cos = [mesh.vertices[v_idx].co * scale for tri in mesh.loop_triangles for v_idx in tri.vertices]
        self.positions = [obj.matrix_world @ co for co in scaled_cos]

        self.batch = batch_for_shader(self.shader, 'TRIS', {"pos": self.positions})

        eval_obj.to_mesh_clear()

        self.handle = bpy.types.SpaceView3D.draw_handler_add(self.draw, (), 'WINDOW', 'POST_VIEW')
        bpy.app.timers.register(self.update_timer)

    def draw(self):
        elapsed = time.time() - self.start_time
        if elapsed >= 4.0:
            self.cleanup()
            return

        opacity = 1.0 - (elapsed / 4.0)
        self.shader.uniform_float("color", (0.55, 0.0, 1.0, opacity))

        gpu.state.blend_set('ALPHA')
        gpu.state.depth_test_set('NONE')
        gpu.state.face_culling_set('FRONT')

        self.batch.draw(self.shader)

    def update_timer(self):
        elapsed = time.time() - self.start_time
        if elapsed >= 4.0:
            self.cleanup()
            return None

        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        return 0.05

    def cleanup(self):
        if hasattr(self, 'handle') and self.handle:
            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
        if 'shape_key_outline' in bpy.app.driver_namespace:
            del bpy.app.driver_namespace['shape_key_outline']

def mode_check_timer():
    wm = bpy.context.window_manager
    if not wm.shape_key_auto_basis:
        return 0.2

    current = bpy.context.mode
    prev = wm.shape_key_prev_mode

    if current != prev:
        if prev == 'EDIT_MESH' and current != 'SCULPT':
            obj = bpy.context.active_object
            if obj and obj.type == 'MESH' and obj.data.shape_keys and obj.active_shape_key_index > 0:
                obj.active_shape_key_index =  = 0
                if 'shape_key_outline' in bpy.app.driver_namespace:
                    bpy.app.driver_namespace['shape_key_outline'].cleanup()
                bpy.app.driver_namespace['shape_key_outline'] = OutlineIndicator(obj)

        wm.shape_key_prev_mode = current

    return 0.2

class VIEW3D_PT_shape_keys_auto(bpy.types.Panel):
    bl_label = "Auto Reset to Basis"
    bl_idname = "VIEW3D_PT_shape_keys_auto"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Shape Keys"

    def draw(self, context):
        self.layout.prop(context.window_manager, "shape_key_auto_basis", text="Enabled (default on)")

def register():
    bpy.utils.register_class(VIEW3D_PT_shape_keys_auto)
    bpy.types.WindowManager.shape_key_auto_basis = bpy.props.BoolProperty(name="Auto Reset to Basis", default=True)
    bpy.types.WindowManager.shape_key_prev_mode = bpy.props.StringProperty(default="OBJECT")
    bpy.app.timers.register(mode_check_timer)

def unregister():
    if bpy.app.timers.is_registered(mode_check_timer):
        bpy.app.timers.unregister(mode_check_timer)
    if 'shape_key_outline' in bpy.app.driver_namespace:
        bpy.app.driver_namespace['shape_key_outline'].cleanup()
    bpy.utils.unregister_class(VIEW3D_PT_shape_keys_auto)
    del bpy.types.WindowManager.shape_key_auto_basis
    del bpy.types.WindowManager.shape_key_prev_mode

if __name__ == "__main__":
    register()
