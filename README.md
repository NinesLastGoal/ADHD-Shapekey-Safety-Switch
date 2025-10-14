# ADHD Shapekey Safety Switch

Auto-resets shapekeys when exiting edit mode in Blender, with a beautiful viewport flash animation.

## Blender 4.5.3 LTS Compatibility

All addon variants have been updated to work with Blender 4.5.3 LTS.

## Available Variants

### 4.5.3 Variant A.py (Recommended)
- Uses `depsgraph_update_post` handler
- Clean implementation without debug output
- Best for production use

### 4.5.3 variant B.py
- Uses `depsgraph_update_post` handler
- Fetches context directly in draw function
- Alternative implementation style

### Nines Shapekey Oversight Fixer.py
- Uses `depsgraph_update_post` handler
- Includes debug print statements
- Useful for troubleshooting

## Installation

1. Download one of the addon files (.py)
2. Open Blender
3. Go to Edit > Preferences > Add-ons
4. Click "Install..." and select the downloaded .py file
5. Enable the addon by checking its checkbox

## Usage

Once installed, the addon will automatically:
- Reset all shapekeys to 0 when you exit Edit mode
- Flash the viewport border to confirm the reset (if enabled)

Access settings via the N-Panel in the 3D Viewport under "Shape Reset":
- **Enable Auto Reset on Exit**: Toggle automatic shapekey reset
- **Flash Outline on Reset**: Toggle the viewport flash animation

## Changes for Blender 4.5.3

- Migrated from deprecated `mode_update_post` handler to `depsgraph_update_post`
- Updated handler signature to accept `depsgraph` parameter
- Changed to use `bpy.context.view_layer.objects.active` for better reliability
- Added proper enable flag checking in all variants
- Added MESH type validation before accessing mode attributes

## Credits

Created by Gemini+Nines 4 Ever
