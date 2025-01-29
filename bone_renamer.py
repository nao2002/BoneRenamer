import bpy

class OBJECT_OT_RenameSelectedBones(bpy.types.Operator):
    """Rename Selected Bones"""
    bl_idname = "object.rename_selected_bones"
    bl_label = "Rename Selected Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object

        if armature and armature.type == 'ARMATURE':
            if context.selected_bones:
                selected_bones = context.selected_bones
                selected_bones_set = set(selected_bones)
                parents = get_roots(selected_bones)
                root_count = 1 if len(parents) > 1 else 0
                
                new_name = context.scene.new_bone_name
                bone_prefix = context.scene.bone_prefix
                if bone_prefix != "NONE":
                    bone_prefix += "_"
                else:
                    bone_prefix = ""
                bone_suffix = context.scene.bone_suffix
                if bone_suffix != "NONE":
                    bone_suffix = "_" + bone_suffix
                else:
                    bone_suffix = ""
                
                renamed_count = 0
                
                root_count_str = ""
                for root in parents:
                    if root_count != 0:
                        root_count_str = "_" + str(root_count).zfill(2)
                        root_count += 1
                    renamed_count += update_bone_names(selected_bones_set, root, root_count_str, new_name, bone_prefix, bone_suffix)
                
                self.report({'INFO'}, f"Renamed {renamed_count} bones.")
        else:
            self.report({'WARNING'}, "Please select an armature object and bones.")

        return {'FINISHED'}

class OBJECT_PT_BoneRenamerPanel(bpy.types.Panel):
    """Panel to rename selected bones"""
    bl_label = "Bone Renamer"
    bl_idname = "OBJECT_PT_bone_renamer_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.mode == 'EDIT'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, "new_bone_name", text="Name")
        row = layout.row()
        row.prop(context.scene, "bone_prefix", text="Prefix")
        row = layout.row()
        row.prop(context.scene, "bone_suffix", text="Suffix")
        row = layout.row()
        row.operator("object.rename_selected_bones", text="Rename Bones")

def register():
    bpy.utils.register_class(OBJECT_OT_RenameSelectedBones)
    bpy.utils.register_class(OBJECT_PT_BoneRenamerPanel)
    bpy.types.Scene.new_bone_name = bpy.props.StringProperty(name="Bone Name", default="RenamedBone")
    bpy.types.Scene.bone_prefix = bpy.props.EnumProperty(
        name="Bone Prefix",
        description="Choose the prefix of the bones",
        items=[
            ("NONE", "None", "No Prefix"),
            ("R", "R", "Prefix R"),
            ("L", "L", "Prefix L")
        ],
        default="NONE"
    )
    bpy.types.Scene.bone_suffix = bpy.props.EnumProperty(
        name="Bone Suffix",
        description="Choose the suffix of the bones",
        items=[
            ("NONE", "None", "No Suffix"),
            ("R", "R", "Suffix R"),
            ("L", "L", "Suffix L")
        ],
        default="NONE"
    )

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_RenameSelectedBones)
    bpy.utils.unregister_class(OBJECT_PT_BoneRenamerPanel)
    del bpy.types.Scene.new_bone_name
    del bpy.types.Scene.bone_prefix
    del bpy.types.Scene.bone_suffix

def get_roots(selectedBones):
    memo = {bone:None for bone in selectedBones}
    all_bones = set(selectedBones)
    for bone in selectedBones:
        if memo[bone] is None:
            _get_root_recursive(memo, all_bones, bone)
    seen = set()
    roots = []
    for bone in selectedBones:
        if memo[bone] not in seen:
            roots.append(memo[bone])
            seen.add(memo[bone])
    return roots
  
def _get_root_recursive(memo, all_bones, bone):
    if bone.parent is None or bone.parent not in all_bones:
        memo[bone] = bone
        return bone
    if memo[bone.parent] is not None:
        memo[bone] = memo[bone.parent]
        return memo[bone.parent]
    memo[bone] = _get_root_recursive(memo, all_bones, bone.parent)
    return memo[bone]

def update_bone_names(all_bones, root_bone, root_count_str, new_name, prefix, suffix):
    counter = 0
    def update_child_name(b):
        nonlocal counter
        if counter == 0:
            b.name = prefix + new_name + root_count_str + suffix
        else:
            b.name = prefix + new_name + root_count_str + "_" + str(counter).zfill(3) + suffix
        counter += 1
        for child in b.children:
            if child in all_bones:
                update_child_name(child)
    update_child_name(root_bone)
    return counter

if __name__ == "__main__":
    register()