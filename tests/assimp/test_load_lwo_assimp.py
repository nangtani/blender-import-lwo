import bpy
from lwo_helper import load_lwo


def test_load_assimp0():
    infile = "tests/assimp/src/LWO/LWO2/boxuv.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp1():
    infile = "tests/assimp/src/LWO/LWO2/box_2uv_1unused.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp2():
    infile = "tests/assimp/src/LWO/LWO2/box_2vc_1unused.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp3():
    infile = "tests/assimp/src/LWO/LWO2/concave_polygon.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp4():
    infile = "tests/assimp/src/LWO/LWO2/concave_self_intersecting.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp5():
    infile = "tests/assimp/src/LWO/LWO2/hierarchy.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp6():
    infile = "tests/assimp/src/LWO/LWO2/hierarchy_smoothed.lwo"
    load_lwo(infile, cancel_search=True)


# def test_load_assimp7():
#     infile = "tests/assimp/src/LWO/LWO2/ModoExport_vertNormals.lwo"
#     load_lwo(infile, cancel_search=True)


def test_load_assimp8():
    infile = "tests/assimp/src/LWO/LWO2/nonplanar_polygon.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp9():
    infile = "tests/assimp/src/LWO/LWO2/rifle.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp10():
    infile = "tests/assimp/src/LWO/LWO2/sphere_with_gradient.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp11():
    infile = "tests/assimp/src/LWO/LWO2/sphere_with_mat_gloss_10pc.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp12():
    infile = "tests/assimp/src/LWO/LWO2/Subdivision.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp13():
    infile = "tests/assimp/src/LWO/LWO2/transparency.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp14():
    infile = "tests/assimp/src/LWO/LWO2/UglyVertexColors.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp15():
    infile = "tests/assimp/src/LWO/LWO2/uvtest.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp16():
    infile = "tests/assimp/src/LWO/LWO2/LWSReferences/QuickDraw--Arm-ForeArm.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp17():
    infile = "tests/assimp/src/LWO/LWO2/LWSReferences/QuickDraw--Arm-Shoulder.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp18():
    infile = "tests/assimp/src/LWO/LWO2/LWSReferences/QuickDraw--Arm-Tip.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp19():
    infile = "tests/assimp/src/LWO/LWO2/LWSReferences/QuickDraw--CabinPortals.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp20():
    infile = "tests/assimp/src/LWO/LWO2/LWSReferences/QuickDraw--Chasis.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp21():
    infile = "tests/assimp/src/LWO/LWO2/LWSReferences/QuickDraw--GP-Gun.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp22():
    infile = "tests/assimp/src/LWO/LWO2/LWSReferences/QuickDraw--GP-Lid.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp23():
    infile = "tests/assimp/src/LWO/LWO2/LWSReferences/QuickDraw--GP-Pod.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp24():
    infile = "tests/assimp/src/LWO/LWO2/LWSReferences/QuickDraw--Laserbeam.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp25():
    infile = "tests/assimp/src/LWO/LWO2/LWSReferences/QuickDraw--Standin-Driver.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp26():
    infile = "tests/assimp/src/LWO/LWO2/LWSReferences/QuickDraw--Wheels-Back.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp27():
    infile = "tests/assimp/src/LWO/LWO2/LWSReferences/QuickDraw--Wheels-Front.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp28():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_cylindrical_x.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp29():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_cylindrical_x_scale_222_wrap_21.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp30():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_cylindrical_y.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp31():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_cylindrical_y_scale_111.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp32():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_cylindrical_y_scale_111_wrap_21.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp33():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_cylindrical_z.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp34():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_planar_x.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp35():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_planar_y.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp36():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_planar_z.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp37():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_planar_z_scale_111.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp38():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_spherical_x.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp39():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_spherical_x_scale_222_wrap_22.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp40():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_spherical_y.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp41():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_spherical_z.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp42():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_spherical_z_wrap_22.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp43():
    infile = "tests/assimp/src/LWO/LWO2/MappingModes/earth_uv_cylindrical_y.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp44():
    infile = "tests/assimp/src/LWO/LWO2/shader_test/CellShader.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp45():
    infile = "tests/assimp/src/LWO/LWO2/shader_test/fastFresnel.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp46():
    infile = "tests/assimp/src/LWO/LWO2/shader_test/realFresnel.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp47():
    infile = "tests/assimp/src/LWO/LWO2/shader_test/SuperCellShader.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp48():
    infile = "tests/assimp/src/LWO/LWOB/ConcavePolygon.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp49():
    infile = "tests/assimp/src/LWO/LWOB/sphere_with_mat_gloss_10pc.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp50():
    infile = "tests/assimp/src/LWO/LWOB/sphere_with_mat_gloss_50pc.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp51():
    infile = "tests/assimp/src/LWO/LWOB/MappingModes/bluewithcylindrictexz.lwo"
    load_lwo(infile, cancel_search=True)


def test_load_assimp52():
    infile = "tests/assimp/src/LWS/simple_cube.lwo"
    load_lwo(infile, cancel_search=True)
