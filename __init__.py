bl_info = {
    "name": "Bone Renamer",
    "author": "nao2002_",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Tool > Bone Renamer",
    "description": "Rename selected bones with optional prefixes or suffixes.",
    "category": "Object",
}

import bpy
from . import bone_renamer

def register():
    bone_renamer.register()

def unregister():
    bone_renamer.unregister()

if __name__ == "__main__":
    register()