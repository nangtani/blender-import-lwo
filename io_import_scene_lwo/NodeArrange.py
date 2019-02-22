# Lisence is FFA, Free For All
# you can do everything with the code, sell, loan, rent, publish it, not publish it, change your license

bl_info = {
    "name": "Node Arrange",
    "author": "JuhaW",
    "version": (0, 2, 0),
    "blender": (2, 79, 4),
    "location": "Node Editor > Properties > Trees",
    "description": "Node Tree Arrangement Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/JuhaW/NodeArrange/issues",
    "category": "Node",
}


import sys
import bpy
from collections import OrderedDict
from itertools import repeat
import pprint
import pdb

# pdb.set_trace()

CYCLES = True
VRAY = not CYCLES


class values:
    average_y = 0
    x_last = 0
    margin_x = 100
    mat_name = ""
    margin_y = 20


class NodePanel(bpy.types.Panel):
    bl_label = "Node Arrange"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Trees"

    def draw(self, context):

        layout = self.layout
        row = layout.row()
        col = layout.column
        # split = layout.split(percentage=.6)
        row.operator("node.button")

        row = layout.row()
        row.prop(bpy.context.scene, "nodemargin_x", text="Margin x")
        row = layout.row()
        row.prop(bpy.context.scene, "nodemargin_y", text="Margin y")
        row = layout.row()
        row.prop(context.scene, "node_center", text="Center nodes")

        # row = layout.row()
        # row.operator('node.button_center')
        # row = layout.row()
        # row.operator('node.button_odd')

        row = layout.row()
        # row.label(bpy.context.space_data.tree_type)
        # row.label(str(bpy.context.space_data.node_tree.name))
        row = layout.row()
        node = context.space_data.node_tree.nodes.active
        if node and node.select:
            row.prop(node, "location", text="Node X", index=0)
            row.prop(node, "location", text="Node Y", index=1)
            row = layout.row()
            row.prop(node, "width", text="Node width")

            # ntree.nodes.active.width = 240
            # ntree.nodes.active.location.x += 10
            # ntree.nodes.active.location.y += 10


class NodeButton(bpy.types.Operator):

    "Show the nodes for this material"
    bl_idname = "node.button"
    bl_label = "Arrange nodes"

    def execute(self, context):
        nodemargin(self, context)
        bpy.context.space_data.node_tree.nodes.update()
        bpy.ops.node.view_all()

        return {"FINISHED"}

        # not sure this is doing what you expect.
        # blender.org/api/blender_python_api_current/bpy.types.Operator.html#invoke

    def invoke(self, context, value):
        values.mat_name = bpy.context.space_data.node_tree
        nodemargin(self, context)
        return {"FINISHED"}


# bpy.context.space_data.tree_type = 'VRayNodeTreeObject'
# bpy.context.space_data.tree_type = 'VRayNodeTreeMaterial'


class NodeButtonOdd(bpy.types.Operator):

    "Show the nodes for this material"
    bl_idname = "node.button_odd"
    bl_label = "Select odd nodes"

    def execute(self, context):
        values.mat_name = ""  # reset
        mat = bpy.context.object.active_material
        nodes_iterate(mat, False)
        return {"FINISHED"}


class NodeButtonCenter(bpy.types.Operator):

    "Show the nodes for this material"
    bl_idname = "node.button_center"
    bl_label = "Center nodes (0,0)"

    def execute(self, context):
        values.mat_name = ""  # reset
        mat = bpy.context.object.active_material
        nodes_center(mat)
        return {"FINISHED"}


def nodemargin(self, context):

    values.margin_x = context.scene.nodemargin_x
    values.margin_y = context.scene.nodemargin_y

    ntree = context.space_data.node_tree

    nodes_iterate(ntree)

    # arrange nodes + this center nodes together
    if context.scene.node_center:
        nodes_center(ntree)


class ArrangeNodesOp(bpy.types.Operator):
    bl_idname = "node.arrange_nodetree"
    bl_label = "Nodes Private Op"

    mat_name = bpy.props.StringProperty()
    margin_x = bpy.props.IntProperty(default=120)
    margin_y = bpy.props.IntProperty(default=120)

    def nodemargin2(self, context):
        mat = None
        mat_found = bpy.data.materials.get(self.mat_name)
        if self.mat_name and mat_found:
            mat = mat_found
            # print(mat)

        if not mat:
            return
        else:
            values.mat_name = self.mat_name
            scn = context.scene
#             scn.nodemargin_x = self.margin_x
#             scn.nodemargin_y = self.margin_y
            nodes_iterate(mat)
            if scn.node_center:
                nodes_center(mat)

    def execute(self, context):
        self.nodemargin2(context)
        return {"FINISHED"}


def outputnode_search(mat):  # return node/None

    outputnodes = []
    #for node in bpy.context.space_data.node_tree.nodes:
    for node in nodetree_get(mat):
        if not node.outputs:
            for input in node.inputs:
                if input.is_linked:
                    outputnodes.append(node)
                    break


    if not outputnodes:
        print("No output node found")
        return None
    
    #print("outputnodes:",outputnodes)
    return outputnodes


# bpy.context.screen.areas[2].spaces[0].node_tree.nodes.active.type
#'VIEWER'
#'COMPOSITE'
# bpy.context.space_data.tree_type
#'CompositorNodeTree'

###############################################################
def nodes_iterate(mat, arrange=True):

    nodeoutput = outputnode_search(mat)
    if nodeoutput is None:
        # print ("nodeoutput is None")
        return None
    a = []
    a.append([])
    for i in nodeoutput:
        a[0].append(i)

    level = 0

    while a[level]:
        a.append([])
        # pprint.pprint (a)
        # print ("level:",level)

        for node in a[level]:
            # pdb.set_trace()
            # print ("while: level:", level)
            inputlist = [i for i in node.inputs if i.is_linked]
            # print ("inputlist:", inputlist)
            if inputlist:

                for input in inputlist:
                    for nlinks in input.links:
                        # dont add parented nodes (inside frame) to list
                        # if not nlinks.from_node.parent:
                        node1 = nlinks.from_node
                        # print ("appending node:",node1)
                        a[level + 1].append(node1)

            else:
                pass
                # print ("no inputlist at level:", level)

        level += 1

        # pprint.pprint(a)

        # delete last empty list
    del a[level]
    level -= 1

    # remove duplicate nodes at the same level, first wins
    for x, nodes in enumerate(a):
        a[x] = list(OrderedDict(zip(a[x], repeat(None))))
        # print ("Duplicate nodes removed")
        # pprint.pprint(a)

        # remove duplicate nodes in all levels, last wins
    top = level
    for row1 in range(top, 1, -1):
        # print ("row1:",row1, a[row1])
        for col1 in a[row1]:
            # print ("col1:",col1)
            for row2 in range(row1 - 1, 0, -1):
                for col2 in a[row2]:
                    if col1 == col2:
                        # print ("Duplicate node found:", col1)
                        # print ("Delete node:", col2)
                        a[row2].remove(col2)
                        break

                # print ("No duplicated nodes anymore:")
    """
	for x, i in enumerate(a):
		print (x)
		for j in i:
			print (j)
		#print()
	"""
    """
	#add node frames to nodelist 
	frames = []
	print ("Frames:")
	print ("level:", level)
	print ("a:",a)
	for row in range(level, 0, -1):
	
		for i, node in enumerate(a[row]):
			if node.parent:
				print ("Frame found:", node.parent, node)
				#if frame already added to the list ?
				frame = node.parent
				#remove node
				del a[row][i]
				if frame not in frames:
					frames.append(frame)
					#add frame to the same place than node was
					a[row].insert(i, frame)
	
	pprint.pprint(a)
	"""
    # return None
    ########################################

    if not arrange:
        nodes_odd(mat2, newnodes)
        return None

        ########################################

    levelmax = level + 1
    level = 0
    values.x_last = 0

    while level < levelmax:

        values.average_y = 0
        nodes = [x for x in a[level]]
        #print ("level, nodes:", level, nodes)
        nodes_arrange(mat, nodes, level)

        level += 1

    return None


###############################################################
def nodes_odd(mat, nodelist):

    ntree = nodetree_get(mat)
    for i in ntree:
        i.select = False

    a = [x for x in ntree if x not in nodelist]
    # print ("odd nodes:",a)
    for i in a:
        i.select = True


def nodes_arrange(mat, nodelist, level):

    parents = []
    for node in nodelist:
        #print(node, node.parent)
        parents.append(node.parent)
        node.parent = None
        nodetree_get(mat).update()

    widthmax = max([x.dimensions.x for x in nodelist])
    xpos = values.x_last - (widthmax + values.margin_x) if level != 0 else 0
    # print ("nodelist, xpos", nodelist,xpos)
    values.x_last = xpos

    # node y positions
    x = 0
    y = 0

    for node in nodelist:

        if node.hide:
            hidey = (node.dimensions.y / 2) - 8
            y = y - hidey
        else:
            hidey = 0

        node.location.y = y
        y = y - values.margin_y - node.dimensions.y + hidey

        node.location.x = xpos  # if node.type != "FRAME" else xpos + 1200

    y = y + values.margin_y

    center = (0 + y) / 2
    values.average_y = center - values.average_y

    for node in nodelist:

        node.location.y -= values.average_y

    for i, node in enumerate(nodelist):
        #print(i, node, node.parent, parents[i])
        node.parent = parents[i]


def nodetree_get(mat):

    if CYCLES:
        return mat.node_tree.nodes
    else:
        return mat.vray.ntree.nodes


def nodes_center(mat):

    bboxminx = []
    bboxmaxx = []
    bboxmaxy = []
    bboxminy = []

    for node in nodetree_get(mat):
        #print(node, node.parent)
        if not node.parent:
            bboxminx.append(node.location.x)
            bboxmaxx.append(node.location.x + node.dimensions.x)
            bboxmaxy.append(node.location.y)
            bboxminy.append(node.location.y - node.dimensions.y)

            # print ("bboxminy:",bboxminy)
    bboxminx = min(bboxminx)
    bboxmaxx = max(bboxmaxx)
    bboxminy = min(bboxminy)
    bboxmaxy = max(bboxmaxy)
    center_x = (bboxminx + bboxmaxx) / 2
    center_y = (bboxminy + bboxmaxy) / 2
    
#     print("minx:",bboxminx)
#     print("maxx:",bboxmaxx)
#     print("miny:",bboxminy)
#     print("maxy:",bboxmaxy)
# 
#     print("bboxes:", bboxminx, bboxmaxx, bboxmaxy, bboxminy)
#     print("center x:",center_x)
#     print("center y:",center_y)

    x = 0
    y = 0

    for node in nodetree_get(mat):

        if not node.parent:
            node.location.x -= center_x
            node.location.y += -center_y


def register():

    bpy.utils.register_module(__name__)

    bpy.types.Scene.nodemargin_x = bpy.props.IntProperty(default=100, update=nodemargin)
    bpy.types.Scene.nodemargin_y = bpy.props.IntProperty(default=20, update=nodemargin)
    bpy.types.Scene.node_center = bpy.props.BoolProperty(
        default=True, update=nodemargin
    )


def unregister():

    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.nodemargin_x
    del bpy.types.Scene.nodemargin_y
    del bpy.types.Scene.node_center


if __name__ == "__main__":
    register()
