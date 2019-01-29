import os
import struct
import chunk


class _obj_layer(object):
    __slots__ = (
        "name",
        "index",
        "parent_index",
        "pivot",
        "pols",
        "bones",
        "bone_names",
        "bone_rolls",
        "pnts",
        "vnorms",
        "lnorms",
        "wmaps",
        "colmaps",
        "uvmaps_vmad",
        "uvmaps_vmap",
        "morphs",
        "edge_weights",
        "surf_tags",
        "has_subds",
    )

    def __init__(self):
        self.name = ""
        self.index = -1
        self.parent_index = -1
        self.pivot = [0, 0, 0]
        self.pols = []
        self.bones = []
        self.bone_names = {}
        self.bone_rolls = {}
        self.pnts = []
        self.vnorms = {}
        self.lnorms = {}
        self.wmaps = {}
        self.colmaps = {}
        self.uvmaps_vmad = {}
        self.uvmaps_vmap = {}
        self.morphs = {}
        self.edge_weights = {}
        self.surf_tags = {}
        self.has_subds = False


class _obj_surf(object):
    __slots__ = (
        "bl_mat",
        "name",
        "source_name",
        "colr",
        "diff",
        "lumi",
        "spec",
        "refl",
        "rblr",
        "tran",
        "rind",
        "tblr",
        "trnl",
        "glos",
        "shrp",
        "smooth",
        "textures",
        "textures_5",
    )

    def __init__(self):
        self.bl_mat = None
        self.name = "Default"
        self.source_name = ""
        self.colr = [1.0, 1.0, 1.0]
        self.diff = 1.0  # Diffuse
        self.lumi = 0.0  # Luminosity
        self.spec = 0.0  # Specular
        self.refl = 0.0  # Reflectivity
        self.rblr = 0.0  # Reflection Bluring
        self.tran = 0.0  # Transparency (the opposite of Blender's Alpha value)
        self.rind = 1.0  # RT Transparency IOR
        self.tblr = 0.0  # Refraction Bluring
        self.trnl = 0.0  # Translucency
        self.glos = 0.4  # Glossiness
        self.shrp = 0.0  # Diffuse Sharpness
        self.smooth = False  # Surface Smoothing
        self.textures = []  # Textures list
        self.textures_5 = []  # Textures list for LWOB


class _surf_texture(object):
    __slots__ = ("opac", "enab", "clipid", "projection", "enab", "uvname")

    def __init__(self):
        self.opac = 1.0
        self.enab = True
        self.clipid = 1
        self.projection = 5
        self.uvname = "UVMap"


class _surf_texture_5(object):
    __slots__ = ("path", "X", "Y", "Z")

    def __init__(self):
        self.path = ""
        self.X = False
        self.Y = False
        self.Z = False


def read_lwostring(raw_name):
    """Parse a zero-padded string."""

    i = raw_name.find(b"\0")
    name_len = i + 1
    if name_len % 2 == 1:  # Test for oddness.
        name_len += 1

    if i > 0:
        # Some plugins put non-text strings in the tags chunk.
        name = raw_name[0:i].decode("utf-8", "ignore")
    else:
        name = ""

    return name, name_len


def read_vx(pointdata):
    """Read a variable-length index."""
    if pointdata[0] != 255:
        index = pointdata[0] * 256 + pointdata[1]
        size = 2
    else:
        index = pointdata[1] * 65536 + pointdata[2] * 256 + pointdata[3]
        size = 4

    return index, size


def read_tags(tag_bytes, object_tags):
    """Read the object's Tags chunk."""
    offset = 0
    chunk_len = len(tag_bytes)

    while offset < chunk_len:
        tag, tag_len = read_lwostring(tag_bytes[offset:])
        offset += tag_len
        object_tags.append(tag)


def read_layr(layr_bytes, object_layers, load_hidden):
    """Read the object's layer data."""
    new_layr = _obj_layer()
    new_layr.index, flags = struct.unpack(">HH", layr_bytes[0:4])

    if flags > 0 and not load_hidden:
        return False

    print("Reading Object Layer")
    offset = 4
    pivot = struct.unpack(">fff", layr_bytes[offset : offset + 12])
    # Swap Y and Z to match Blender's pitch.
    new_layr.pivot = [pivot[0], pivot[2], pivot[1]]
    offset += 12
    layr_name, name_len = read_lwostring(layr_bytes[offset:])
    offset += name_len

    if layr_name:
        new_layr.name = layr_name
    else:
        new_layr.name = "Layer %d" % (new_layr.index + 1)

    if len(layr_bytes) == offset + 2:
        new_layr.parent_index, = struct.unpack(">h", layr_bytes[offset : offset + 2])

    object_layers.append(new_layr)
    return True


def read_layr_5(layr_bytes, object_layers):
    """Read the object's layer data."""
    # XXX: Need to check what these two exactly mean for a LWOB/LWLO file.
    new_layr = _obj_layer()
    new_layr.index, flags = struct.unpack(">HH", layr_bytes[0:4])

    print("Reading Object Layer")
    offset = 4
    layr_name, name_len = read_lwostring(layr_bytes[offset:])
    offset += name_len

    if name_len > 2 and layr_name != "noname":
        new_layr.name = layr_name
    else:
        new_layr.name = "Layer %d" % new_layr.index

    object_layers.append(new_layr)


def read_pnts(pnt_bytes, object_layers):
    """Read the layer's points."""
    print("\tReading Layer (" + object_layers[-1].name + ") Points")
    offset = 0
    chunk_len = len(pnt_bytes)

    while offset < chunk_len:
        pnts = struct.unpack(">fff", pnt_bytes[offset : offset + 12])
        offset += 12
        # Re-order the points so that the mesh has the right pitch,
        # the pivot already has the correct order.
        pnts = [
            pnts[0] - object_layers[-1].pivot[0],
            pnts[2] - object_layers[-1].pivot[1],
            pnts[1] - object_layers[-1].pivot[2],
        ]
        object_layers[-1].pnts.append(pnts)


def read_weightmap(weight_bytes, object_layers):
    """Read a weight map's values."""
    chunk_len = len(weight_bytes)
    offset = 2
    name, name_len = read_lwostring(weight_bytes[offset:])
    offset += name_len
    weights = []

    while offset < chunk_len:
        pnt_id, pnt_id_len = read_vx(weight_bytes[offset : offset + 4])
        offset += pnt_id_len
        value, = struct.unpack(">f", weight_bytes[offset : offset + 4])
        offset += 4
        weights.append([pnt_id, value])

    object_layers[-1].wmaps[name] = weights


def read_morph(morph_bytes, object_layers, is_abs):
    """Read an endomorph's relative or absolute displacement values."""
    chunk_len = len(morph_bytes)
    offset = 2
    name, name_len = read_lwostring(morph_bytes[offset:])
    offset += name_len
    deltas = []

    while offset < chunk_len:
        pnt_id, pnt_id_len = read_vx(morph_bytes[offset : offset + 4])
        offset += pnt_id_len
        pos = struct.unpack(">fff", morph_bytes[offset : offset + 12])
        offset += 12
        pnt = object_layers[-1].pnts[pnt_id]

        if is_abs:
            deltas.append([pnt_id, pos[0], pos[2], pos[1]])
        else:
            # Swap the Y and Z to match Blender's pitch.
            deltas.append([pnt_id, pnt[0] + pos[0], pnt[1] + pos[2], pnt[2] + pos[1]])

        object_layers[-1].morphs[name] = deltas


def read_colmap(col_bytes, object_layers):
    """Read the RGB or RGBA color map."""
    chunk_len = len(col_bytes)
    dia, = struct.unpack(">H", col_bytes[0:2])
    offset = 2
    name, name_len = read_lwostring(col_bytes[offset:])
    offset += name_len
    colors = {}

    if dia == 3:
        while offset < chunk_len:
            pnt_id, pnt_id_len = read_vx(col_bytes[offset : offset + 4])
            offset += pnt_id_len
            col = struct.unpack(">fff", col_bytes[offset : offset + 12])
            offset += 12
            colors[pnt_id] = (col[0], col[1], col[2])
    elif dia == 4:
        while offset < chunk_len:
            pnt_id, pnt_id_len = read_vx(col_bytes[offset : offset + 4])
            offset += pnt_id_len
            col = struct.unpack(">ffff", col_bytes[offset : offset + 16])
            offset += 16
            colors[pnt_id] = (col[0], col[1], col[2])

    if name in object_layers[-1].colmaps:
        if "PointMap" in object_layers[-1].colmaps[name]:
            object_layers[-1].colmaps[name]["PointMap"].update(colors)
        else:
            object_layers[-1].colmaps[name]["PointMap"] = colors
    else:
        object_layers[-1].colmaps[name] = dict(PointMap=colors)


def read_normmap(norm_bytes, object_layers):
    """Read vertex normal maps."""
    chunk_len = len(norm_bytes)
    offset = 2
    name, name_len = read_lwostring(norm_bytes[offset:])
    offset += name_len
    vnorms = {}

    while offset < chunk_len:
        pnt_id, pnt_id_len = read_vx(norm_bytes[offset : offset + 4])
        offset += pnt_id_len
        norm = struct.unpack(">fff", norm_bytes[offset : offset + 12])
        offset += 12
        vnorms[pnt_id] = [norm[0], norm[2], norm[1]]

    object_layers[-1].vnorms = vnorms


def read_color_vmad(col_bytes, object_layers, last_pols_count):
    """Read the Discontinuous (per-polygon) RGB values."""
    chunk_len = len(col_bytes)
    dia, = struct.unpack(">H", col_bytes[0:2])
    offset = 2
    name, name_len = read_lwostring(col_bytes[offset:])
    offset += name_len
    colors = {}
    abs_pid = len(object_layers[-1].pols) - last_pols_count

    if dia == 3:
        while offset < chunk_len:
            pnt_id, pnt_id_len = read_vx(col_bytes[offset : offset + 4])
            offset += pnt_id_len
            pol_id, pol_id_len = read_vx(col_bytes[offset : offset + 4])
            offset += pol_id_len

            # The PolyID in a VMAD can be relative, this offsets it.
            pol_id += abs_pid
            col = struct.unpack(">fff", col_bytes[offset : offset + 12])
            offset += 12
            if pol_id in colors:
                colors[pol_id][pnt_id] = (col[0], col[1], col[2])
            else:
                colors[pol_id] = dict({pnt_id: (col[0], col[1], col[2])})
    elif dia == 4:
        while offset < chunk_len:
            pnt_id, pnt_id_len = read_vx(col_bytes[offset : offset + 4])
            offset += pnt_id_len
            pol_id, pol_id_len = read_vx(col_bytes[offset : offset + 4])
            offset += pol_id_len

            pol_id += abs_pid
            col = struct.unpack(">ffff", col_bytes[offset : offset + 16])
            offset += 16
            if pol_id in colors:
                colors[pol_id][pnt_id] = (col[0], col[1], col[2])
            else:
                colors[pol_id] = dict({pnt_id: (col[0], col[1], col[2])})

    if name in object_layers[-1].colmaps:
        if "FaceMap" in object_layers[-1].colmaps[name]:
            object_layers[-1].colmaps[name]["FaceMap"].update(colors)
        else:
            object_layers[-1].colmaps[name]["FaceMap"] = colors
    else:
        object_layers[-1].colmaps[name] = dict(FaceMap=colors)


def read_uvmap(uv_bytes, object_layers):
    """Read the simple UV coord values."""
    chunk_len = len(uv_bytes)
    offset = 2
    name, name_len = read_lwostring(uv_bytes[offset:])
    offset += name_len
    uv_coords = {}

    while offset < chunk_len:
        pnt_id, pnt_id_len = read_vx(uv_bytes[offset : offset + 4])
        offset += pnt_id_len
        pos = struct.unpack(">ff", uv_bytes[offset : offset + 8])
        offset += 8
        uv_coords[pnt_id] = (pos[0], pos[1])

    if name in object_layers[-1].uvmaps_vmap:
        if "PointMap" in object_layers[-1].uvmaps_vmap[name]:
            object_layers[-1].uvmaps_vmap[name]["PointMap"].update(uv_coords)
        else:
            object_layers[-1].uvmaps_vmap[name]["PointMap"] = uv_coords
    else:
        object_layers[-1].uvmaps_vmap[name] = dict(PointMap=uv_coords)


def read_uv_vmad(uv_bytes, object_layers, last_pols_count):
    """Read the Discontinuous (per-polygon) uv values."""
    chunk_len = len(uv_bytes)
    offset = 2
    name, name_len = read_lwostring(uv_bytes[offset:])
    offset += name_len
    uv_coords = {}
    abs_pid = len(object_layers[-1].pols) - last_pols_count

    while offset < chunk_len:
        pnt_id, pnt_id_len = read_vx(uv_bytes[offset : offset + 4])
        offset += pnt_id_len
        pol_id, pol_id_len = read_vx(uv_bytes[offset : offset + 4])
        offset += pol_id_len

        pol_id += abs_pid
        pos = struct.unpack(">ff", uv_bytes[offset : offset + 8])
        offset += 8
        if pol_id in uv_coords:
            uv_coords[pol_id][pnt_id] = (pos[0], pos[1])
        else:
            uv_coords[pol_id] = dict({pnt_id: (pos[0], pos[1])})

    if name in object_layers[-1].uvmaps_vmad:
        if "FaceMap" in object_layers[-1].uvmaps_vmad[name]:
            object_layers[-1].uvmaps_vmad[name]["FaceMap"].update(uv_coords)
        else:
            object_layers[-1].uvmaps_vmad[name]["FaceMap"] = uv_coords
    else:
        object_layers[-1].uvmaps_vmad[name] = dict(FaceMap=uv_coords)


def read_weight_vmad(ew_bytes, object_layers):
    """Read the VMAD Weight values."""
    chunk_len = len(ew_bytes)
    offset = 2
    name, name_len = read_lwostring(ew_bytes[offset:])
    if name != "Edge Weight":
        return  # We just want the Catmull-Clark edge weights

    offset += name_len
    # Some info: LW stores a face's points in a clock-wize order (with the
    # normal pointing at you). This gives edges a 'direction' which is used
    # when it comes to storing CC edge weight values. The weight is given
    # to the point preceding the edge that the weight belongs to.
    while offset < chunk_len:
        pnt_id, pnt_id_len = read_vx(ew_bytes[offset : offset + 4])
        offset += pnt_id_len
        pol_id, pol_id_len = read_vx(ew_bytes[offset : offset + 4])
        offset += pol_id_len
        weight, = struct.unpack(">f", ew_bytes[offset : offset + 4])
        offset += 4

        face_pnts = object_layers[-1].pols[pol_id]
        try:
            # Find the point's location in the polygon's point list
            first_idx = face_pnts.index(pnt_id)
        except:
            continue

        # Then get the next point in the list, or wrap around to the first
        if first_idx == len(face_pnts) - 1:
            second_pnt = face_pnts[0]
        else:
            second_pnt = face_pnts[first_idx + 1]

        object_layers[-1].edge_weights["{0} {1}".format(second_pnt, pnt_id)] = weight


def read_normal_vmad(norm_bytes, object_layers):
    """Read the VMAD Split Vertex Normals"""
    chunk_len = len(norm_bytes)
    offset = 2
    name, name_len = read_lwostring(norm_bytes[offset:])
    lnorms = {}
    offset += name_len

    while offset < chunk_len:
        pnt_id, pnt_id_len = read_vx(norm_bytes[offset : offset + 4])
        offset += pnt_id_len
        pol_id, pol_id_len = read_vx(norm_bytes[offset : offset + 4])
        offset += pol_id_len
        norm = struct.unpack(">fff", norm_bytes[offset : offset + 12])
        offset += 12
        if not (pol_id in lnorms.keys()):
            lnorms[pol_id] = []
        lnorms[pol_id].append([pnt_id, norm[0], norm[2], norm[1]])

    print("LENGTH", len(lnorms.keys()))
    object_layers[-1].lnorms = lnorms


def read_pols(pol_bytes, object_layers):
    """Read the layer's polygons, each one is just a list of point indexes."""
    print("\tReading Layer (" + object_layers[-1].name + ") Polygons")
    offset = 0
    pols_count = len(pol_bytes)
    old_pols_count = len(object_layers[-1].pols)

    while offset < pols_count:
        pnts_count, = struct.unpack(">H", pol_bytes[offset : offset + 2])
        offset += 2
        all_face_pnts = []
        for j in range(pnts_count):
            face_pnt, data_size = read_vx(pol_bytes[offset : offset + 4])
            offset += data_size
            all_face_pnts.append(face_pnt)
        all_face_pnts.reverse()  # correct normals

        object_layers[-1].pols.append(all_face_pnts)

    return len(object_layers[-1].pols) - old_pols_count


def read_pols_5(pol_bytes, object_layers):
    """
    Read the polygons, each one is just a list of point indexes.
    But it also includes the surface index.
    """
    print("\tReading Layer (" + object_layers[-1].name + ") Polygons")
    offset = 0
    chunk_len = len(pol_bytes)
    old_pols_count = len(object_layers[-1].pols)
    poly = 0

    while offset < chunk_len:
        pnts_count, = struct.unpack(">H", pol_bytes[offset : offset + 2])
        offset += 2
        all_face_pnts = []
        for j in range(pnts_count):
            face_pnt, = struct.unpack(">H", pol_bytes[offset : offset + 2])
            offset += 2
            all_face_pnts.append(face_pnt)
        all_face_pnts.reverse()

        object_layers[-1].pols.append(all_face_pnts)
        sid, = struct.unpack(">h", pol_bytes[offset : offset + 2])
        offset += 2
        sid = abs(sid) - 1
        if sid not in object_layers[-1].surf_tags:
            object_layers[-1].surf_tags[sid] = []
        object_layers[-1].surf_tags[sid].append(poly)
        poly += 1

    return len(object_layers[-1].pols) - old_pols_count


def read_bones(bone_bytes, object_layers):
    """Read the layer's skelegons."""
    print("\tReading Layer (" + object_layers[-1].name + ") Bones")
    offset = 0
    bones_count = len(bone_bytes)

    while offset < bones_count:
        pnts_count, = struct.unpack(">H", bone_bytes[offset : offset + 2])
        offset += 2
        all_bone_pnts = []
        for j in range(pnts_count):
            bone_pnt, data_size = read_vx(bone_bytes[offset : offset + 4])
            offset += data_size
            all_bone_pnts.append(bone_pnt)

        object_layers[-1].bones.append(all_bone_pnts)


def read_bone_tags(tag_bytes, object_layers, object_tags, type):
    """Read the bone name or roll tags."""
    offset = 0
    chunk_len = len(tag_bytes)

    if type == "BONE":
        bone_dict = object_layers[-1].bone_names
    elif type == "BNUP":
        bone_dict = object_layers[-1].bone_rolls
    else:
        return

    while offset < chunk_len:
        pid, pid_len = read_vx(tag_bytes[offset : offset + 4])
        offset += pid_len
        tid, = struct.unpack(">H", tag_bytes[offset : offset + 2])
        offset += 2
        bone_dict[pid] = object_tags[tid]


def read_surf_tags(tag_bytes, object_layers, last_pols_count):
    """Read the list of PolyIDs and tag indexes."""
    print("\tReading Layer (" + object_layers[-1].name + ") Surface Assignments")
    offset = 0
    chunk_len = len(tag_bytes)

    # Read in the PolyID/Surface Index pairs.
    abs_pid = len(object_layers[-1].pols) - last_pols_count
    while offset < chunk_len:
        pid, pid_len = read_vx(tag_bytes[offset : offset + 4])
        offset += pid_len
        sid, = struct.unpack(">H", tag_bytes[offset : offset + 2])
        offset += 2
        if sid not in object_layers[-1].surf_tags:
            object_layers[-1].surf_tags[sid] = []
        object_layers[-1].surf_tags[sid].append(pid + abs_pid)


def read_surf(surf_bytes, object_surfs):
    """Read the object's surface data."""
    if len(object_surfs) == 0:
        print("Reading Object Surfaces")

    surf = _obj_surf()
    name, name_len = read_lwostring(surf_bytes)
    if len(name) != 0:
        surf.name = name

    # We have to read this, but we won't use it...yet.
    s_name, s_name_len = read_lwostring(surf_bytes[name_len:])
    offset = name_len + s_name_len
    block_size = len(surf_bytes)
    while offset < block_size:
        subchunk_name, = struct.unpack("4s", surf_bytes[offset : offset + 4])
        offset += 4
        subchunk_len, = struct.unpack(">H", surf_bytes[offset : offset + 2])
        offset += 2

        # Now test which subchunk it is.
        if subchunk_name == b"COLR":
            surf.colr = struct.unpack(">fff", surf_bytes[offset : offset + 12])
            # Don't bother with any envelopes for now.

        elif subchunk_name == b"DIFF":
            surf.diff, = struct.unpack(">f", surf_bytes[offset : offset + 4])

        elif subchunk_name == b"LUMI":
            surf.lumi, = struct.unpack(">f", surf_bytes[offset : offset + 4])

        elif subchunk_name == b"SPEC":
            surf.spec, = struct.unpack(">f", surf_bytes[offset : offset + 4])

        elif subchunk_name == b"REFL":
            surf.refl, = struct.unpack(">f", surf_bytes[offset : offset + 4])

        elif subchunk_name == b"RBLR":
            surf.rblr, = struct.unpack(">f", surf_bytes[offset : offset + 4])

        elif subchunk_name == b"TRAN":
            surf.tran, = struct.unpack(">f", surf_bytes[offset : offset + 4])

        elif subchunk_name == b"RIND":
            surf.rind, = struct.unpack(">f", surf_bytes[offset : offset + 4])

        elif subchunk_name == b"TBLR":
            surf.tblr, = struct.unpack(">f", surf_bytes[offset : offset + 4])

        elif subchunk_name == b"TRNL":
            surf.trnl, = struct.unpack(">f", surf_bytes[offset : offset + 4])

        elif subchunk_name == b"GLOS":
            surf.glos, = struct.unpack(">f", surf_bytes[offset : offset + 4])

        elif subchunk_name == b"SHRP":
            surf.shrp, = struct.unpack(">f", surf_bytes[offset : offset + 4])

        elif subchunk_name == b"SMAN":
            s_angle, = struct.unpack(">f", surf_bytes[offset : offset + 4])
            if s_angle > 0.0:
                surf.smooth = True

        elif subchunk_name == b"BLOK":
            block_type, = struct.unpack("4s", surf_bytes[offset : offset + 4])
            if block_type == b"IMAP":
                ordinal, ord_len = read_lwostring(surf_bytes[offset + 4 :])
                suboffset = 6 + ord_len
                colormap = True
                texture = _surf_texture()
                while suboffset < subchunk_len:
                    subsubchunk_name, = struct.unpack(
                        "4s", surf_bytes[offset + suboffset : offset + suboffset + 4]
                    )
                    suboffset += 4
                    subsubchunk_len, = struct.unpack(
                        ">H", surf_bytes[offset + suboffset : offset + suboffset + 2]
                    )
                    suboffset += 2
                    if subsubchunk_name == b"CHAN":
                        channel, = struct.unpack(
                            "4s",
                            surf_bytes[offset + suboffset : offset + suboffset + 4],
                        )
                        if channel != b"COLR":
                            colormap = False
                            break
                    if subsubchunk_name == b"OPAC":
                        opactype, = struct.unpack(
                            ">H",
                            surf_bytes[offset + suboffset : offset + suboffset + 2],
                        )
                        texture.opac, = struct.unpack(
                            ">f",
                            surf_bytes[offset + suboffset + 2 : offset + suboffset + 6],
                        )
                    if subsubchunk_name == b"ENAB":
                        texture.enab, = struct.unpack(
                            ">H",
                            surf_bytes[offset + suboffset : offset + suboffset + 2],
                        )
                    if subsubchunk_name == b"IMAG":
                        texture.clipid, = struct.unpack(
                            ">H",
                            surf_bytes[offset + suboffset : offset + suboffset + 2],
                        )
                    if subsubchunk_name == b"PROJ":
                        texture.projection, = struct.unpack(
                            ">H",
                            surf_bytes[offset + suboffset : offset + suboffset + 2],
                        )
                    if subsubchunk_name == b"VMAP":
                        texture.uvname, name_len = read_lwostring(
                            surf_bytes[offset + suboffset :]
                        )
                        print("VMAP", texture.uvname)
                    suboffset += subsubchunk_len

                if colormap:
                    surf.textures.append(texture)

        offset += subchunk_len

    object_surfs[surf.name] = surf


def read_surf_5(surf_bytes, object_surfs, dirpath):
    """Read the object's surface data."""
    if len(object_surfs) == 0:
        print("Reading Object Surfaces")

    surf = _obj_surf()
    name, name_len = read_lwostring(surf_bytes)
    if len(name) != 0:
        surf.name = name

    offset = name_len
    chunk_len = len(surf_bytes)
    while offset < chunk_len:
        subchunk_name, = struct.unpack("4s", surf_bytes[offset : offset + 4])
        offset += 4
        subchunk_len, = struct.unpack(">H", surf_bytes[offset : offset + 2])
        offset += 2

        # Now test which subchunk it is.
        if subchunk_name == b"COLR":
            color = struct.unpack(">BBBB", surf_bytes[offset : offset + 4])
            surf.colr = [color[0] / 255.0, color[1] / 255.0, color[2] / 255.0]

        elif subchunk_name == b"DIFF":
            surf.diff, = struct.unpack(">h", surf_bytes[offset : offset + 2])
            surf.diff /= 256.0  # Yes, 256 not 255.

        elif subchunk_name == b"LUMI":
            surf.lumi, = struct.unpack(">h", surf_bytes[offset : offset + 2])
            surf.lumi /= 256.0

        elif subchunk_name == b"SPEC":
            surf.spec, = struct.unpack(">h", surf_bytes[offset : offset + 2])
            surf.spec /= 256.0

        elif subchunk_name == b"REFL":
            surf.refl, = struct.unpack(">h", surf_bytes[offset : offset + 2])
            surf.refl /= 256.0

        elif subchunk_name == b"TRAN":
            surf.tran, = struct.unpack(">h", surf_bytes[offset : offset + 2])
            surf.tran /= 256.0

        elif subchunk_name == b"RIND":
            surf.rind, = struct.unpack(">f", surf_bytes[offset : offset + 4])

        elif subchunk_name == b"GLOS":
            surf.glos, = struct.unpack(">h", surf_bytes[offset : offset + 2])

        elif subchunk_name == b"SMAN":
            s_angle, = struct.unpack(">f", surf_bytes[offset : offset + 4])
            if s_angle > 0.0:
                surf.smooth = True

        elif subchunk_name in [b"CTEX", b"DTEX", b"STEX", b"RTEX", b"TTEX", b"BTEX"]:
            texture = None

        elif subchunk_name == b"TIMG":
            path, path_len = read_lwostring(surf_bytes[offset:])
            if path == "(none)":
                continue
            texture = _surf_texture_5()
            path = dirpath + os.sep + path.replace("//", "")
            texture.path = path
            surf.textures_5.append(texture)

        elif subchunk_name == b"TFLG":
            if texture:
                mapping, = struct.unpack(">h", surf_bytes[offset : offset + 2])
                if mapping & 1:
                    texture.X = True
                elif mapping & 2:
                    texture.Y = True
                elif mapping & 4:
                    texture.Z = True

        offset += subchunk_len

    object_surfs[surf.name] = surf


def read_clip(clip_bytes, dirpath, clips):
    """Read texture clip path"""
    print("Read clip")
    c_id = struct.unpack(">L", clip_bytes[0:4])[0]
    path1, path_len = read_lwostring(clip_bytes[10:])

    path1 = path1.replace(":/", ":")
    path1 = path1.replace(":\\", ":")
    path1 = path1.replace(":", ":/")
    dirpath = dirpath.replace("\\", "/")
    path2 = dirpath + os.sep + path1.replace("//", "")
    clips[c_id] = (path1, path2)


#     path = re.sub("\\\\", "/", path)
#     imagefile = path.split("/")[-1]
#     dirpath = os.path.dirname(self.filename)
#     #print(c_id, path, dirpath)
#     files = [path]
#     files.extend(glob("{0}/../{1}".format(dirpath, imagefile)))
#     files.extend(glob("{0}/../images/{1}".format(dirpath, imagefile)))
#
#     ifile = None
#     for f in files:
#         f = os.path.abspath(f)
#         if Path(f).is_file():
#             ifile = f
#             if f not in self.images:
#                 self.images.append(f)
#             continue
#
#
#     self.clips[c_id] = ifile


class lwoObj(object):
    def __init__(self, filename):
        self.name, self.ext = os.path.splitext(os.path.basename(filename))
        # self.file = os.path.abspath(filename)[-1]
        self.f = None
        self.filename = os.path.abspath(filename)
        self.layers = []
        self.surfs = {}
        self.clips = {}
        self.tags = []
        self.images = []
        self.header = None
        self.chunk_size = None
        self.chunk_name = None

    def read(
        self,
        ADD_SUBD_MOD=True,
        LOAD_HIDDEN=False,
        SKEL_TO_ARM=True,
        USE_EXISTING_MATERIALS=False,
    ):
        self.add_subd_mod = ADD_SUBD_MOD
        self.load_hidden = LOAD_HIDDEN
        self.skel_to_arm = SKEL_TO_ARM
        self.use_existing_materials = USE_EXISTING_MATERIALS

        self.f = open(self.filename, "rb")
        try:
            self.header, self.chunk_size, self.chunk_name = struct.unpack(
                ">4s1L4s", self.f.read(12)
            )
        except:
            print("Error parsing file header! Filename {0}".format(self.filename))
            self.f.close()
            return

        if self.chunk_name == b"LWO2":
            self.read_lwo2()
        elif self.chunk_name == b"LWOB" or self.chunk_name == b"LWLO":
            # LWOB and LWLO are the old format, LWLO is a layered object.
            self.read_lwob()
        else:
            print("Not a supported file type!")
            self.f.close()
            return
        self.f.close()

    def read_lwo2(self):
        """Read version 2 file, LW 6+."""
        self.handle_layer = True
        self.last_pols_count = 0
        self.just_read_bones = False
        print("Importing LWO: " + self.filename + "\nLWO v2 Format")

        while True:
            try:
                rootchunk = chunk.Chunk(self.f)
            except EOFError:
                break

            if rootchunk.chunkname == b"TAGS":
                read_tags(rootchunk.read(), self.tags)
            elif rootchunk.chunkname == b"LAYR":
                self.handle_layer = read_layr(
                    rootchunk.read(), self.layers, self.load_hidden
                )
            elif rootchunk.chunkname == b"PNTS" and self.handle_layer:
                read_pnts(rootchunk.read(), self.layers)
            elif rootchunk.chunkname == b"VMAP" and self.handle_layer:
                vmap_type = rootchunk.read(4)

                if vmap_type == b"WGHT":
                    read_weightmap(rootchunk.read(), self.layers)
                elif vmap_type == b"MORF":
                    read_morph(rootchunk.read(), self.layers, False)
                elif vmap_type == b"SPOT":
                    read_morph(rootchunk.read(), self.layers, True)
                elif vmap_type == b"TXUV":
                    read_uvmap(rootchunk.read(), self.layers)
                elif vmap_type == b"RGB " or vmap_type == b"RGBA":
                    read_colmap(rootchunk.read(), self.layers)
                elif vmap_type == b"NORM":
                    read_normmap(rootchunk.read(), self.layers)
                else:
                    rootchunk.skip()

            elif rootchunk.chunkname == b"VMAD" and self.handle_layer:
                vmad_type = rootchunk.read(4)

                if vmad_type == b"TXUV":
                    read_uv_vmad(rootchunk.read(), self.layers, self.last_pols_count)
                elif vmad_type == b"RGB " or vmad_type == b"RGBA":
                    read_color_vmad(rootchunk.read(), self.layers, self.last_pols_count)
                elif vmad_type == b"WGHT":
                    # We only read the Edge Weight map if it's there.
                    read_weight_vmad(rootchunk.read(), self.layers)
                elif vmad_type == b"NORM":
                    read_normal_vmad(rootchunk.read(), self.layers)
                else:
                    rootchunk.skip()

            elif rootchunk.chunkname == b"POLS" and self.handle_layer:
                face_type = rootchunk.read(4)
                self.just_read_bones = False
                # PTCH is LW's Subpatches, SUBD is CatmullClark.
                if (
                    face_type == b"FACE" or face_type == b"PTCH" or face_type == b"SUBD"
                ) and self.handle_layer:
                    self.last_pols_count = read_pols(rootchunk.read(), self.layers)
                    if face_type != b"FACE":
                        self.layers[-1].has_subds = True
                elif face_type == b"BONE" and self.handle_layer:
                    read_bones(rootchunk.read(), self.layers)
                    self.just_read_bones = True
                else:
                    rootchunk.skip()

            elif rootchunk.chunkname == b"PTAG" and self.handle_layer:
                tag_type, = struct.unpack("4s", rootchunk.read(4))
                if tag_type == b"SURF" and not self.just_read_bones:
                    # Ignore the surface data if we just read a bones chunk.
                    read_surf_tags(rootchunk.read(), self.layers, self.last_pols_count)

                elif self.skel_to_arm:
                    if tag_type == b"BNUP":
                        read_bone_tags(rootchunk.read(), self.layers, self.tags, "BNUP")
                    elif tag_type == b"BONE":
                        read_bone_tags(rootchunk.read(), self.layers, self.tags, "BONE")
                    else:
                        rootchunk.skip()
                else:
                    rootchunk.skip()
            elif rootchunk.chunkname == b"SURF":
                read_surf(rootchunk.read(), self.surfs)
            elif rootchunk.chunkname == b"CLIP":
                read_clip(rootchunk.read(), os.path.dirname(self.filename), self.clips)
            else:
                # if self.handle_layer:
                # print("Skipping Chunk:", rootchunk.chunkname)
                rootchunk.skip()


#     def read_lwob(self):
#         """Read version 1 file, LW < 6."""
#         self.last_pols_count = 0
#         print("Importing LWO: " + self.filename + "\nLWO v1 Format")
#
#         while True:
#             try:
#                 self.rootchunk = chunk.Chunk(self.f)
#             except EOFError:
#                 break
#
#             if self.rootchunk.chunkname == b'SRFS':
#                 self.read_tags()
#             elif self.rootchunk.chunkname == b'LAYR':
#                 self.read_layr_5()
#             elif self.rootchunk.chunkname == b'PNTS':
#                 if len(self.layers) == 0:
#                     # LWOB files have no LAYR chunk to set this up.
#                     nlayer = _obj_layer()
#                     nlayer.name = "Layer 1"
#                     self.layers.append(nlayer)
#                 self.read_pnts()
#             elif self.rootchunk.chunkname == b'POLS':
#                 self.read_pols_5()
#             elif self.rootchunk.chunkname == b'PCHS':
#                 self.read_pols_5()
#                 layers[-1].has_subds = True
#             elif self.rootchunk.chunkname == b'PTAG':
#                 tag_type, = struct.unpack("4s", self.rootchunk.read(4))
#                 if tag_type == b'SURF':
#                     read_surf_tags_5(self.rootchunk.read(), self.layers, self.last_pols_count)
#                 else:
#                     self.rootchunk.skip()
#             elif self.rootchunk.chunkname == b'SURF':
#                 self.read_surf_5()
#             else:
#                 # For Debugging \/.
#                 #if handle_layer:
#                     #print("Skipping Chunk: ", rootchunk.chunkname)
#                 self.rootchunk.skip()
