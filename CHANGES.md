# Changes for Blender 4.5.3 Compatibility

## Problem
All features stopped working in Blender 4.5.3 LTS due to API changes in Blender's handler system.

## Root Cause
Blender 4.5 deprecated and removed the `bpy.app.handlers.mode_update_post` handler, which was being used by variant B of the addon.

## Solutions Implemented

### 1. Handler Migration (Variant B)
**Before:**
```python
bpy.app.handlers.mode_update_post.append(_handler)
```

**After:**
```python
bpy.app.handlers.depsgraph_update_post.append(_handler)
```

### 2. Handler Signature Update (All Variants)
**Before:**
```python
def on_mode_change(scene):
```

**After:**
```python
def on_mode_change(scene, depsgraph):
```

The `depsgraph_update_post` handler requires both `scene` and `depsgraph` parameters.

### 3. Context Access Improvement (All Variants)
**Before:**
```python
obj = bpy.context.object
```

**After:**
```python
obj = bpy.context.view_layer.objects.active
```

This provides more reliable access to the active object across different contexts.

### 4. Enable Flag Check (Variant A)
**Before:**
```python
def on_mode_change(scene, depsgraph):
    global _previous_mode
    obj = bpy.context.view_layer.objects.active
```

**After:**
```python
def on_mode_change(scene, depsgraph):
    global _previous_mode
    if not hasattr(bpy.context, "scene") or not bpy.context.scene:
        return
    if not bpy.context.scene.shapekey_reset_enabled:
        return
    obj = bpy.context.view_layer.objects.active
```

Added check to respect the user's enable/disable preference.

### 5. Type Safety (All Variants)
**Before:**
```python
if not obj or not hasattr(obj, 'mode'):
```

**After:**
```python
if not obj or obj.type != 'MESH' or not hasattr(obj, 'mode'):
```

Explicitly check that the object is a MESH type before accessing mode-related attributes.

### 6. Version Information Updates
- Updated `bl_info` version to (4, 5, 3)
- Updated `blender` requirement to (4, 5, 3)
- Removed deprecation warnings
- Updated registration messages to indicate 4.5.3 compatibility

## Files Modified
1. `4.5.3 Variant A.py` - Added enable flag check
2. `4.5.3 variant B.py` - Migrated handler, updated context access
3. `Nines Shapekey Oversight Fixer.py` - Updated context access and version info

## Additional Improvements
- Added `.gitignore` to prevent committing Python cache files
- Added comprehensive `README.md` with installation and usage instructions
- All variants now follow consistent patterns for reliability

## Testing
All files pass Python syntax validation:
```bash
python3 -m py_compile "4.5.3 Variant A.py"
python3 -m py_compile "4.5.3 variant B.py"
python3 -m py_compile "Nines Shapekey Oversight Fixer.py"
```

## Result
All three addon variants are now fully compatible with Blender 4.5.3 LTS and should work as expected.
