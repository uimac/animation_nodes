import bpy
from .. preferences import getPreferences
from .. operators.output_execution_code import setupTextEditorCallback, executionCodeTextBlockName


class DeveloperPanel(bpy.types.Panel):
    bl_idname = "AN_PT_developer_panel"
    bl_label = "Developer"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Node Tree"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 3

    @classmethod
    def poll(cls, context):
        try: return context.space_data.node_tree.bl_idname == "an_AnimationNodeTree"
        except: return False

    def draw(self, context):
        layout = self.layout
        tree = context.space_data.node_tree

        preferences = getPreferences()

        col = layout.column()
        self.drawExecutionCodeSettings(col, preferences)

        layout.separator()

        col = layout.column()
        self.drawProfilingSettings(col, preferences)

        layout.separator()

        layout.prop(preferences.nodeColors, "nodeColorMode", text = "Color Mode")

        col = layout.column()
        self.drawTimelineSettings(col, preferences)

    def drawExecutionCodeSettings(self, layout, preferences):
        executionCode = preferences.executionCode
        layout.label(text = "Execution Code:")

        col = layout.column(align = True)

        row = col.row(align = True)
        row.prop(executionCode, "type", text = "")
        if executionCode.type == "MEASURE":
            row.operator("an.reset_measurements", text = "", icon = "RECOVER_LAST")

        row = col.row(align = True)
        row.operator("an.print_current_execution_code", text = "Print", icon = "CONSOLE")
        row.operator("an.write_current_execution_code", text = "Write", icon = "TEXT")
        subrow = row.row(align = True)
        subrow.active = executionCodeTextBlockName in bpy.data.texts
        subrow.operator("an.select_area", text = "", icon = "ZOOM_SELECTED").callback = setupTextEditorCallback

    def drawProfilingSettings(self, layout, preferences):
        profiling = preferences.developer.profiling

        col = layout.column()
        col.prop(profiling, "function", text = "Function")
        col.prop(profiling, "sort", text = "Sort Mode")
        col.prop(profiling, "output", text = "Output")

        props = col.operator("an.profile", text = "Profile", icon = "PREVIEW_RANGE")
        props.function = profiling.function
        props.sort = profiling.sort
        props.output = profiling.output

    def drawTimelineSettings(self, layout, preferences):
        col = layout.column()
        props = col.operator("an.experimental_timeline_in_the_world", text = "(Experimental) Use Timeline In The World", icon = "PREVIEW_RANGE")