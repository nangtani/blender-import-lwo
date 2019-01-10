# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Fake Plugin",
    "author": "Dave Keeshan",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
#     "location": "File > Import-Export",
#     "description": "Import-Export OBJ, Import OBJ mesh, UV's, materials and textures",
#     "warning": "",
#     "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Import-Export/Wavefront_OBJ",
#     "support": 'OFFICIAL',
    "category": "Object",
}

def register():
    print("Hello World")

def unregister():
    print("Goodbye World")
