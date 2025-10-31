bl_info = {
    "name": "Reset Shapekeys on Edit Exit (v4.5.1)",
    "author": "Gemini+Nines 4 Ever",
    "version": (4, 5, 1),
    "blender": (4, 5, 3),
    "location": "3D Viewport > N-Panel > Shape Reset",
    "description": "Auto-resets shapekeys with a custom UI and a beautiful, correctly fading viewport flash. <3",
    "warning": "",
    "doc_url": "https://github.com/NinesLastGoal/ADHD-Shapekey-Safety-Switch",
    "category": "Object",
}

import bpy
import gpu
import time
from gpu_extras.batch import batch_for_shader

def draw_fading_outline(op):
    """
    This function draws the outline. It fetches the context directly to ensure it is never stale.
    """
    context = bpy.context
    elapsed = time.time() - op.start_time
    
    alpha = max(0.0, 1.0 - (elapsed / op.duration))
    if alpha <= 0.0:
        return

    region = context.region
    if not region:
        return
        
    width = region.width
    height = region.height
    
    border_thickness = 5
    coords = [
        (border_thickness, border_thickness), (width - border_thickness, border_thickness),
        (width - border_thickness, height - border_thickness), (border_thickness, height - border_thickness)
    ]
    
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINE_LOOP', {"pos": coords})
    
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(border_thickness * 2)
    shader.bind()
    shader.uniform_float("color", (0.6, 0.2, 1.0, alpha))
    batch.draw(shader)
    gpu.state.blend_set('NONE')


class WM_OT_FlashOperator(bpy.types.Operator):
    """The Modal Operator to manage the fade animation."""
    bl_idname = "wm.flash_operator"
    bl_label = "Flash Viewport"

    _draw_handle = None
    _timer = None
    start_time: float
    duration: float = 1.5
    area: bpy.types.Area = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            if (time.time() - self.start_time) > self.duration:
                self.finish(context)
                return {'FINISHED'}
            if self.area:
                self.area.tag_redraw()
        return {'PASS_THROUGH'}

    def finish(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None
        if self._draw_handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._draw_handle, 'WINDOW')
            self._draw_handle = None
        if self.area:
            self.area.tag_redraw()

    def invoke(self, context, event):
        self.start_time = time.time()
        
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                self.area = area
                break
        else:
            self.report({'WARNING'}, "No 3D Viewport found to draw in.")
            return {'CANCELLED'}
        
        args = (self,)
        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_fading_outline, args, 'WINDOW', 'POST_PIXEL'
        )
        
        self._timer = context.window_manager.event_timer_add(0.016, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

# --- Core Logic ---
_handler = None
_previous_mode = None

def reset_shapekeys_on_exit():
    obj = bpy.context.view_layer.objects.active
    if obj and obj.type == 'MESH' and obj.data and obj.data.shape_keys:
        scene = bpy.context.scene
        was_changed = False
        
        for key in obj.data.shape_keys.key_blocks:
            if key != key.relative_key and key.value != 0.0:
                was_changed = True
                key.value = 0.0
                
        obj.active_shape_key_index = 0
        
        if was_changed and scene.shapekey_flash_enabled:
            bpy.ops.wm.flash_operator('INVOKE_DEFAULT')
            
    return None

def on_mode_change(scene, depsgraph):
    global _previous_mode
    if not hasattr(bpy.context, "scene") or not bpy.context.scene:
        return
    if not bpy.context.scene.shapekey_reset_enabled:
        return
    
    obj = bpy.context.view_layer.objects.active
    if not obj or obj.type != 'MESH' or not hasattr(obj, 'mode'):
        _previous_mode = None
        return

    current_mode = obj.mode
    if _previous_mode is None:
        _previous_mode = current_mode
        return
    
    if _previous_mode == 'EDIT' and current_mode == 'OBJECT':
        bpy.app.timers.register(reset_shapekeys_on_exit, first_interval=0.01)
        
    _previous_mode = current_mode

# --- UI Panel and Registration ---
class SHAPEKEY_PT_reset_panel(bpy.types.Panel):
    bl_label = "Shapekey Auto Reset"
    bl_idname = "OBJECT_PT_shapekey_reset_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Shape Reset'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Gemini+Nines 4 Ever", icon='HEART')
        col.separator()
        col.prop(scene, "shapekey_reset_enabled", text="Enable Auto Reset on Exit")
        sub = col.column()
        sub.enabled = scene.shapekey_reset_enabled
        sub.prop(scene, "shapekey_flash_enabled", text="Flash Outline on Reset")

classes = (
    WM_OT_FlashOperator,
    SHAPEKEY_PT_reset_panel,
)

def register():
    global _handler
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.shapekey_reset_enabled = bpy.props.BoolProperty(name="Enable Auto Reset", default=True)
    bpy.types.Scene.shapekey_flash_enabled = bpy.props.BoolProperty(name="Enable Viewport Flash", default=True)
    
    _handler = on_mode_change
    bpy.app.handlers.depsgraph_update_post.append(_handler)
    print("Shapekey Reset Addon Registered (4.5.3).")

def unregister():
    global _handler
    if _handler and _handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_handler)
    _handler = None
    
    try:
        del bpy.types.Scene.shapekey_reset_enabled
        del bpy.types.Scene.shapekey_flash_enabled
    except (AttributeError, RuntimeError):
        pass
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    print("Shapekey Reset Addon Unregistered.")

if __name__ == "__main__":
    register()
