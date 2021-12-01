import bpy

# https://blenderartists.org/forum/showthread.php209369-Synchronizing-text-with-changes-from-outside

def execute():
    """ Check modified external scripts in the scene and update if possible
    """
    ctx = bpy.context.copy()
    #Ensure  context area is not None
    ctx['area'] = ctx['screen'].areas[0]
    for t in bpy.data.texts:
        if t.is_modified and not t.is_in_memory:
            print("  * Warning: Updating external script", t.name)
            # Change current context to contain a TEXT_EDITOR
            oldAreaType = ctx['area'].type
            ctx['area'].type = 'TEXT_EDITOR'
            ctx['edit_text'] = t
            bpy.ops.text.resolve_conflict(ctx, resolution='RELOAD')
            #Restore context
            ctx['area'].type = oldAreaType

execute()