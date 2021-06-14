import bpy
from bpy.props import *

class ExperimentalTimelineInTheWorld(bpy.types.Operator):
    bl_idname = "an.experimental_timeline_in_the_world"
    bl_label = "Use Timeline In The World"
    bl_description = "Add world for AnimationNodes's timeline for keyframing."

    def execute(self, context):
        an_world = bpy.data.worlds.new("AnimationNodes")
        if an_world is not None:
            context.scene.world = an_world
            # create node_tree data
            an_world.use_nodes = True
            # insert key for creating animation_data block
            an_world.node_tree.nodes["Background"].inputs[1].keyframe_insert('default_value', frame=1)
            an_world.use_nodes = False

            tree = context.space_data.node_tree
            if tree.animation_data == None:
                # force creating animation_data
                bpy.ops.node.add_node(type="an_DataInputNode", use_transform=True, settings=[{"name":"assignedType", "value":"'Integer'"}])
                node = context.active_node
                node.inputs[0].keyframe_insert('value', frame=1)

            # inject node_tree action!
            an_world.node_tree.animation_data.action = tree.animation_data.action

            return {"FINISHED"}
        self.report({"ERROR"}, "ExperimentalTimelineInTheWorld failed to create new world")
        return {"CANCELLED"}
