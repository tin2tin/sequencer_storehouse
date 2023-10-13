bl_info = {
    "name": "Sequencer Storehouse",
    "author": "tintwotin",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "Sequencer > Seqeunce Menu > Storehouse Files",
    "description": "Copy all source files to a folder and update strip paths accordingly",
    "warning": "",
    "doc_url": "",
    "category": "Sequencer",
}


import bpy
import shutil
import os
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

# Set this variable to True to enable debugging prints
debug_mode = False

class SEQUENCER_OT_copy_strips(Operator, ImportHelper):
    """Copy all source files to a folder and update strip paths accordingly"""
    bl_idname = "sequencer.copy_strips"
    bl_label = "Storehouse Files"

    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No directory selected")
            return {'CANCELLED'}

        destination_folder = bpy.path.abspath(self.filepath)
        print("Folder: "+destination_folder)

        supported_strip_types = {'MOVIE', 'SOUND', 'IMAGE'}

        for sequence in bpy.context.scene.sequence_editor.sequences:
            if sequence.type in supported_strip_types:
                if sequence.type == 'IMAGE' and bpy.path.abspath(sequence.directory) and sequence.name:
                    source_path = os.path.join(sequence.directory, sequence.name)
                elif sequence.type == 'SOUND':
                    sound_filepath = bpy.path.abspath(sequence.sound.filepath)
                    if sound_filepath:
                        source_path = sound_filepath
                elif sequence.type == 'MOVIE':
                    file_path = bpy.path.abspath(sequence.filepath)
                    if file_path:
                        source_path = file_path
                else:
                    continue
                
                if not os.path.exists(source_path):
                    print("not found: "+source_path)

                destination_path = os.path.join(destination_folder, os.path.basename(source_path))

                if not os.path.exists(destination_path):
                    try:
                        shutil.copy(source_path, destination_path)
                        if debug_mode:
                            print(f"Copied '{os.path.basename(destination_path)}' to '{destination_folder}'")

                        if sequence.type == 'IMAGE':
                            sequence.directory = bpy.path.relpath(destination_folder)
                            sequence.name = os.path.basename(sequence.name)
                        elif sequence.type == 'SOUND':
                            sequence.sound.filepath = bpy.path.relpath(destination_path)
                            sequence.name = os.path.basename(destination_path)
                        elif sequence.type == 'MOVIE':
                            sequence.filepath = bpy.path.relpath(destination_path)
                            sequence.name = os.path.basename(destination_path)

                    except Exception as e:
                        print(f"Error copying '{os.path.basename(destination_path)}': {str(e)}")

        if debug_mode:
            print("Copy and update process completed")
        self.report({'INFO'}, "Files copied and strip paths updated.")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filepath = ""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def draw_sequence_menu(self, context):
    layout = self.layout
    layout.operator("sequencer.copy_strips")

def append_sequence_menu(self, context):
    self.layout.menu("SEQUENCER_MT_sequence")

def register():
    bpy.utils.register_class(SEQUENCER_OT_copy_strips)
    bpy.types.SEQUENCER_MT_editor_menus.prepend(append_sequence_menu)
    bpy.types.SEQUENCER_MT_sequence.append(draw_sequence_menu)

def unregister():
    bpy.utils.unregister_class(SEQUENCER_OT_copy_strips)
    bpy.types.SEQUENCER_MT_editor_menus.remove(append_sequence_menu)
    bpy.types.SEQUENCER_MT_sequence.remove(draw_sequence_menu)

if __name__ == "__main__":
    register()
