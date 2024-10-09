import bpy
import shutil
import os
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

# Set this variable to True to enable debugging prints
debug_mode = True

class SEQUENCER_OT_copy_strips(Operator, ImportHelper):
    """Copy all source files to a folder and update strip paths accordingly"""
    bl_idname = "sequencer.copy_strips"
    bl_label = "Storehouse Files"

    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No directory selected")
            return {'CANCELLED'}

        destination_folder = bpy.path.abspath(self.filepath)
        destination_folder = os.path.normpath(destination_folder)
        print("Destination Folder: " + destination_folder)

        supported_strip_types = {'MOVIE', 'SOUND', 'IMAGE'}

        for sequence in bpy.context.scene.sequence_editor.sequences:
            source_path = None

            if sequence.type in supported_strip_types:
                # Handling for different strip types
                if sequence.type == 'IMAGE' and bpy.path.abspath(sequence.directory) and sequence.elements:
                    # Construct the full path for IMAGE type
                    source_directory = bpy.path.abspath(sequence.directory)
                    source_directory = os.path.normpath(source_directory)
                    
                    # Get the exact filename from the sequence
                    source_filename = sequence.elements[0].filename if sequence.elements else sequence.name
                    source_path = os.path.join(source_directory, source_filename)

                elif sequence.type == 'SOUND':
                    # Get the full path for SOUND type
                    source_path = bpy.path.abspath(sequence.sound.filepath)
                elif sequence.type == 'MOVIE':
                    # Get the full path for MOVIE type
                    source_path = bpy.path.abspath(sequence.filepath)
                else:
                    continue

                if source_path:
                    # Normalize and clean up the path
                    source_path = os.path.normpath(source_path)
                    source_path = source_path.strip()  # Remove leading/trailing whitespace

                    # For debug: show the cleaned-up absolute path
                    print(f"Checking Source Path: {source_path}")

                    # Handle long paths on Windows (extended-length path support)
                    if os.name == 'nt' and len(source_path) > 240:
                        source_path = f"\\\\?\\{source_path}"

                # Verify if the source path exists
                if not source_path or not os.path.exists(source_path):
                    print(f"Path not found: '{source_path}'")
                    continue  # Skip to the next sequence if the path doesn't exist

                destination_path = os.path.join(destination_folder, os.path.basename(source_path))
                destination_path = os.path.normpath(destination_path)

                # If the file doesn't exist in the destination, copy it
                if not os.path.exists(destination_path):
                    try:
                        shutil.copy(source_path, destination_path)
                        if debug_mode:
                            print(f"Copied '{os.path.basename(destination_path)}' to '{destination_folder}'")

                        # Update the strip paths to use the absolute path
                        if sequence.type == 'IMAGE':
                            sequence.directory = bpy.path.relpath(destination_folder)
                            sequence.name = os.path.basename(source_filename)  # Ensure to use original filename
                        elif sequence.type == 'SOUND':
                            sequence.sound.filepath = bpy.path.relpath(destination_path)
                        elif sequence.type == 'MOVIE':
                            sequence.filepath = bpy.path.relpath(destination_path)

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
    if "SEQUENCER_MT_sequence" not in bpy.types.SEQUENCER_MT_editor_menus.__dict__:
        bpy.types.SEQUENCER_MT_editor_menus.prepend(append_sequence_menu)
    layout.menu("SEQUENCER_MT_sequence")

def register():
    bpy.utils.register_class(SEQUENCER_OT_copy_strips)
    # Check if the menu already exists before appending
    if "SEQUENCER_MT_sequence" not in bpy.types.SEQUENCER_MT_editor_menus.__dict__:
        bpy.types.SEQUENCER_MT_sequence.append(draw_sequence_menu)

def unregister():
    bpy.utils.unregister_class(SEQUENCER_OT_copy_strips)
    # Remove the operator from the menu only if it exists
    if "SEQUENCER_MT_sequence" in bpy.types.SEQUENCER_MT_editor_menus.__dict__:
        bpy.types.SEQUENCER_MT_sequence.remove(draw_sequence_menu)

if __name__ == "__main__":
    register()
