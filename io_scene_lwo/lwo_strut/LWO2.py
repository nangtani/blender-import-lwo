import struct
import chunk

from .lwoBase import LWOBase, _obj_layer, _obj_surf, _surf_texture, _surf_position


class LWO2(LWOBase):
    """Read version 2 file, LW 6+."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_types = [b"LWO2"]
        self.last_pols_count = 0
        self.just_read_bones = False

    def read_vx(self, pointdata):
        """Read a variable-length index."""
        if 0 == len(pointdata):
            self.error("Incomplete lwo file, no more valid points: {self.filename}")
        if pointdata[0] != 255:
            index = pointdata[0] * 256 + pointdata[1]
            size = 2
        else:
            index = pointdata[1] * 65536 + pointdata[2] * 256 + pointdata[3]
            size = 4

        return index, size

    def read_clip(self):
        """Read texture clip path"""
        bytes = self.bytes2
        (c_id, ) = struct.unpack(">L", bytes[0:4])
        orig_path, path_len = self.read_lwostring(bytes[10:])
        self.clips[c_id] = orig_path

    def read_layr(self):
        """Read the object's layer data."""
        bytes = self.bytes2
        new_layr = _obj_layer()
        new_layr.index, flags = struct.unpack(">HH", bytes[0:4])

        if flags > 0 and not self.ch.load_hidden:
            return False

        self.info("Reading Object Layer")
        offset = 4
        pivot = struct.unpack(">fff", bytes[offset : offset + 12])
        # Swap Y and Z to match Blender's pitch.
        new_layr.pivot = [pivot[0], pivot[2], pivot[1]]
        offset += 12
        layr_name, name_len = self.read_lwostring(bytes[offset:])
        offset += name_len

        if layr_name:
            new_layr.name = layr_name
        else:
            new_layr.name = f"Layer {new_layr.index + 1}"

        if len(bytes) == offset + 2:
            (new_layr.parent_index,) = struct.unpack(
                ">h", bytes[offset : offset + 2]
            )

        self.layers.append(new_layr)

    def read_weightmap(self):
        """Read a weight map's values."""
        bytes = self.bytes2
        chunk_len = len(bytes)
        offset = 2
        name, name_len = self.read_lwostring(bytes[offset:])
        offset += name_len
        weights = []

        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(bytes[offset : offset + 4])
            offset += pnt_id_len
            (value,) = struct.unpack(">f", bytes[offset : offset + 4])
            offset += 4
            weights.append([pnt_id, value])

        self.layers[-1].wmaps[name] = weights

    def read_morph(self, is_abs):
        """Read an endomorph's relative or absolute displacement values."""
        bytes = self.bytes2
        chunk_len = len(bytes)
        offset = 2
        name, name_len = self.read_lwostring(bytes[offset:])
        offset += name_len
        deltas = []

        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(bytes[offset : offset + 4])
            offset += pnt_id_len
            pos = struct.unpack(">fff", bytes[offset : offset + 12])
            offset += 12
            pnt = self.layers[-1].pnts[pnt_id]

            if is_abs:
                deltas.append([pnt_id, pos[0], pos[2], pos[1]])
            else:
                # Swap the Y and Z to match Blender's pitch.
                deltas.append(
                    [pnt_id, pnt[0] + pos[0], pnt[1] + pos[2], pnt[2] + pos[1]]
                )

            self.layers[-1].morphs[name] = deltas

    def read_colmap(self):
        """Read the RGB or RGBA color map."""
        bytes = self.bytes2
        chunk_len = len(bytes)
        (dia,) = struct.unpack(">H", bytes[0:2])
        offset = 2
        name, name_len = self.read_lwostring(bytes[offset:])
        offset += name_len
        colors = {}

        if dia == 3:
            while offset < chunk_len:
                pnt_id, pnt_id_len = self.read_vx(bytes[offset : offset + 4])
                offset += pnt_id_len
                col = struct.unpack(">fff", bytes[offset : offset + 12])
                offset += 12
                colors[pnt_id] = (col[0], col[1], col[2])
        elif dia == 4:
            while offset < chunk_len:
                pnt_id, pnt_id_len = self.read_vx(bytes[offset : offset + 4])
                offset += pnt_id_len
                col = struct.unpack(">ffff", bytes[offset : offset + 16])
                offset += 16
                colors[pnt_id] = (col[0], col[1], col[2])

        if name in self.layers[-1].colmaps:
            if "PointMap" in self.layers[-1].colmaps[name]:
                self.layers[-1].colmaps[name]["PointMap"].update(colors)
            else:
                self.layers[-1].colmaps[name]["PointMap"] = colors
        else:
            self.layers[-1].colmaps[name] = dict(PointMap=colors)

    def read_normmap(self):
        """Read vertex normal maps."""
        bytes = self.bytes2
        chunk_len = len(bytes)
        offset = 2
        name, name_len = self.read_lwostring(bytes[offset:])
        offset += name_len
        vnorms = {}

        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(bytes[offset : offset + 4])
            offset += pnt_id_len
            norm = struct.unpack(">fff", bytes[offset : offset + 12])
            offset += 12
            vnorms[pnt_id] = [norm[0], norm[2], norm[1]]

        self.layers[-1].vnorms = vnorms

    def read_color_vmad(self):
        """Read the Discontinuous (per-polygon) RGB values."""
        bytes = self.bytes2
        chunk_len = len(bytes)
        (dia,) = struct.unpack(">H", bytes[0:2])
        offset = 2
        name, name_len = self.read_lwostring(bytes[offset:])
        offset += name_len
        colors = {}
        abs_pid = len(self.layers[-1].pols) - self.last_pols_count

        if dia == 3:
            while offset < chunk_len:
                pnt_id, pnt_id_len = self.read_vx(bytes[offset : offset + 4])
                offset += pnt_id_len
                pol_id, pol_id_len = self.read_vx(bytes[offset : offset + 4])
                offset += pol_id_len

                # The PolyID in a VMAD can be relative, this offsets it.
                pol_id += abs_pid
                col = struct.unpack(">fff", bytes[offset : offset + 12])
                offset += 12
                if pol_id in colors:
                    colors[pol_id][pnt_id] = (col[0], col[1], col[2])
                else:
                    colors[pol_id] = dict({pnt_id: (col[0], col[1], col[2])})
        elif dia == 4:
            while offset < chunk_len:
                pnt_id, pnt_id_len = self.read_vx(bytes[offset : offset + 4])
                offset += pnt_id_len
                pol_id, pol_id_len = self.read_vx(bytes[offset : offset + 4])
                offset += pol_id_len

                pol_id += abs_pid
                col = struct.unpack(">ffff", bytes[offset : offset + 16])
                offset += 16
                if pol_id in colors:
                    colors[pol_id][pnt_id] = (col[0], col[1], col[2])
                else:
                    colors[pol_id] = dict({pnt_id: (col[0], col[1], col[2])})

        if name in self.layers[-1].colmaps:
            if "FaceMap" in self.layers[-1].colmaps[name]:
                self.layers[-1].colmaps[name]["FaceMap"].update(colors)
            else:
                self.layers[-1].colmaps[name]["FaceMap"] = colors
        else:
            self.layers[-1].colmaps[name] = dict(FaceMap=colors)

    def read_uvmap(self):
        """Read the simple UV coord values."""
        bytes = self.bytes2
        chunk_len = len(bytes)
        offset = 2
        name, name_len = self.read_lwostring(bytes[offset:])
        offset += name_len
        uv_coords = {}

        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(bytes[offset : offset + 4])
            offset += pnt_id_len
            pos = struct.unpack(">ff", bytes[offset : offset + 8])
            offset += 8
            uv_coords[pnt_id] = (pos[0], pos[1])

        if name in self.layers[-1].uvmaps_vmap:
            if "PointMap" in self.layers[-1].uvmaps_vmap[name]:
                self.layers[-1].uvmaps_vmap[name]["PointMap"].update(uv_coords)
            else:
                self.layers[-1].uvmaps_vmap[name]["PointMap"] = uv_coords
        else:
            self.layers[-1].uvmaps_vmap[name] = dict(PointMap=uv_coords)

    def read_uv_vmad(self):
        """Read the Discontinuous (per-polygon) uv values."""
        bytes = self.bytes2
        chunk_len = len(bytes)
        offset = 2
        name, name_len = self.read_lwostring(bytes[offset:])
        offset += name_len
        uv_coords = {}
        abs_pid = len(self.layers[-1].pols) - self.last_pols_count

        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(bytes[offset : offset + 4])
            offset += pnt_id_len
            pol_id, pol_id_len = self.read_vx(bytes[offset : offset + 4])
            offset += pol_id_len

            pol_id += abs_pid
            pos = struct.unpack(">ff", bytes[offset : offset + 8])
            offset += 8
            if pol_id in uv_coords:
                uv_coords[pol_id][pnt_id] = (pos[0], pos[1])
            else:
                uv_coords[pol_id] = dict({pnt_id: (pos[0], pos[1])})

        if name in self.layers[-1].uvmaps_vmad:
            if "FaceMap" in self.layers[-1].uvmaps_vmad[name]:
                self.layers[-1].uvmaps_vmad[name]["FaceMap"].update(uv_coords)
            else:
                self.layers[-1].uvmaps_vmad[name]["FaceMap"] = uv_coords
        else:
            self.layers[-1].uvmaps_vmad[name] = dict(FaceMap=uv_coords)

    def read_weight_vmad(self):
        """Read the VMAD Weight values."""
        bytes = self.bytes2
        chunk_len = len(bytes)
        offset = 2
        name, name_len = self.read_lwostring(bytes[offset:])
        if name != "Edge Weight":
            return  # We just want the Catmull-Clark edge weights

        offset += name_len
        # Some info: LW stores a face's points in a clock-wize order (with the
        # normal pointing at you). This gives edges a 'direction' which is used
        # when it comes to storing CC edge weight values. The weight is given
        # to the point preceding the edge that the weight belongs to.
        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(bytes[offset : offset + 4])
            offset += pnt_id_len
            pol_id, pol_id_len = self.read_vx(bytes[offset : offset + 4])
            offset += pol_id_len
            (weight,) = struct.unpack(">f", bytes[offset : offset + 4])
            offset += 4

            face_pnts = self.layers[-1].pols[pol_id]
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

            self.layers[-1].edge_weights[f"{second_pnt} {pnt_id}"] = weight

    def read_normal_vmad(self):
        """Read the VMAD Split Vertex Normals"""
        bytes = self.bytes2
        chunk_len = len(bytes)
        offset = 2
        name, name_len = self.read_lwostring(bytes[offset:])
        lnorms = {}
        offset += name_len

        while offset < chunk_len:
            pnt_id, pnt_id_len = self.read_vx(bytes[offset : offset + 4])
            offset += pnt_id_len
            pol_id, pol_id_len = self.read_vx(bytes[offset : offset + 4])
            offset += pol_id_len
            norm = struct.unpack(">fff", bytes[offset : offset + 12])
            offset += 12
            if not (pol_id in lnorms.keys()):
                lnorms[pol_id] = []
            lnorms[pol_id].append([pnt_id, norm[0], norm[2], norm[1]])

        self.info(f"LENGTH {len(lnorms.keys())}")
        self.layers[-1].lnorms = lnorms

    def read_pols(self):
        """Read the layer's polygons, each one is just a list of point indexes."""
        self.info(f"    Reading Layer ({self.layers[-1].name}) Polygons")
        bytes = self.bytes2
        offset = 0
        pols_count = len(bytes)
        old_pols_count = len(self.layers[-1].pols)

        while offset < pols_count:
            (pnts_count,) = struct.unpack(">H", bytes[offset : offset + 2])
            offset += 2
            all_face_pnts = []
            for j in range(pnts_count):
                face_pnt, data_size = self.read_vx(bytes[offset : offset + 4])
                offset += data_size
                all_face_pnts.append(face_pnt)
            all_face_pnts.reverse()  # correct normals

            self.layers[-1].pols.append(all_face_pnts)

        self.last_pols_count = len(self.layers[-1].pols) - old_pols_count

    def read_bones(self):
        """Read the layer's skelegons."""
        self.info(f"    Reading Layer ({self.layers[-1].name}) Bones")
        bytes = self.bytes2
        offset = 0
        bones_count = len(bytes)

        while offset < bones_count:
            (pnts_count,) = struct.unpack(">H", bytes[offset : offset + 2])
            offset += 2
            all_bone_pnts = []
            for j in range(pnts_count):
                bone_pnt, data_size = self.read_vx(bytes[offset : offset + 4])
                offset += data_size
                all_bone_pnts.append(bone_pnt)

            self.layers[-1].bones.append(all_bone_pnts)

    def read_bone_tags(self, type):
        """Read the bone name or roll tags."""
        bytes = self.bytes2
        offset = 0
        chunk_len = len(bytes)

        if "BONE" == type:
            bone_dict = self.layers[-1].bone_names
        elif "BNUP" == type:
            bone_dict = self.layers[-1].bone_rolls
        else:
            return

        while offset < chunk_len:
            pid, pid_len = self.read_vx(bytes[offset : offset + 4])
            offset += pid_len
            (tid,) = struct.unpack(">H", bytes[offset : offset + 2])
            offset += 2
            bone_dict[pid] = self.tags[tid]

    def read_position(self, subbytes, offset, subchunk_len):
        p = _surf_position()
        suboffset = 0

        while suboffset < subchunk_len:
            (subsubchunk_name,) = struct.unpack(
                "4s", subbytes[offset + suboffset : offset + suboffset + 4]
            )
            suboffset += 4
            (slen,) = struct.unpack(
                ">H", subbytes[offset + suboffset : offset + suboffset + 2]
            )
            suboffset += 2

            if b"CNTR" == subsubchunk_name:
                p.cntr = struct.unpack(">fffh", subbytes[offset + suboffset : offset + suboffset + 14])
                if 20 == slen:
                    _ = struct.unpack(">hf", subbytes[offset + suboffset + 14 : offset + suboffset + slen])
            elif b"SIZE" == subsubchunk_name:
                p.size = struct.unpack(
                    ">fffh", subbytes[offset + suboffset : offset + suboffset + 14]
                )
                if 20 == slen:
                    _ = struct.unpack(">hf", subbytes[offset + suboffset + 14 : offset + suboffset + slen])
            elif b"ROTA" == subsubchunk_name:
                p.rota = struct.unpack(
                    ">fffH", subbytes[offset + suboffset : offset + suboffset + 14]
                )
                if 20 == slen:
                    _ = struct.unpack(">hf", subbytes[offset + suboffset + 14 : offset + suboffset + slen])
            elif b"FALL" == subsubchunk_name:
                p.fall = struct.unpack(
                    ">hfffh", subbytes[offset + suboffset : offset + suboffset + slen]
                )
            elif b"OREF" == subsubchunk_name:
                p.oref, name_len = self.read_lwostring(subbytes[offset + suboffset :])
            elif b"CSYS" == subsubchunk_name:
                (p.csys,) = struct.unpack(
                    ">h", subbytes[offset + suboffset : offset + suboffset + slen]
                )
            suboffset += slen
        return p

    def read_texture(self, subbytes, offset, subchunk_len, num = 0):
        texture = _surf_texture()
        ordinal, ord_len = self.read_lwostring(subbytes[offset + 4 + num :])
        
        suboffset = 6 + ord_len
        while suboffset < subchunk_len:
            (subsubchunk_name,) = struct.unpack(
                "4s", subbytes[offset + suboffset : offset + suboffset + 4]
            )
            suboffset += 4
            (subsubchunk_len,) = struct.unpack(
                ">H", subbytes[offset + suboffset : offset + suboffset + 2]
            )
            suboffset += 2
            #self.debug(f"xx {num} {} {subsubchunk_len}")
                        
            if b"TMAP" == subsubchunk_name:
                texture.position = self.read_position(
                    subbytes, (offset + suboffset), subsubchunk_len
                )
            elif b"CHAN" == subsubchunk_name:
                (texture.channel,) = struct.unpack(
                    "4s",
                    subbytes[offset + suboffset : offset + suboffset + 4],
                )
                texture.channel = texture.channel.decode("ascii")
            elif b"OPAC" == subsubchunk_name:
                (texture.opactype,) = struct.unpack(
                    ">H",
                    subbytes[offset + suboffset : offset + suboffset + 2],
                )
                (texture.opac,) = struct.unpack(
                    ">f",
                    subbytes[offset + suboffset + 2 : offset + suboffset + 6],
                )
            elif b"ENAB" == subsubchunk_name:
                (texture.enab,) = struct.unpack(
                    ">H",
                    subbytes[offset + suboffset : offset + suboffset + 2],
                )
            elif b"IMAG" == subsubchunk_name:
                (texture.clipid,) = struct.unpack(
                    ">H",
                    subbytes[offset + suboffset : offset + suboffset + 2],
                )
            elif b"PROJ" == subsubchunk_name:
                (texture.projection,) = struct.unpack(
                    ">H",
                    subbytes[offset + suboffset : offset + suboffset + 2],
                )
            elif b"VMAP" == subsubchunk_name:
                texture.uvname, name_len = self.read_lwostring(
                    subbytes[offset + suboffset :]
                )
            elif b"FUNC" == subsubchunk_name:  # This is the procedural
                texture.func, name_len = self.read_lwostring(
                    subbytes[offset + suboffset :]
                )
            elif b"NEGA" == subsubchunk_name:
                (texture.nega,) = struct.unpack(
                    ">H",
                    subbytes[offset + suboffset : offset + suboffset + 2],
                )
            elif b"AXIS" == subsubchunk_name:
                (texture.axis,) = struct.unpack(
                    ">H",
                    subbytes[offset + suboffset : offset + suboffset + 2],
                )
            elif b"WRAP" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name} {subchunk_len}")                 
            elif b"WRPW" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"WRPH" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"AAST" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"PIXB" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"VALU" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"TAMP" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"STCK" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"PNAM" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"INAM" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"GRST" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"GREN" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"GRPT" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"IKEY" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"FKEY" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            elif b"GVER" == subsubchunk_name:
                self.debug(f"Unimplemented SubSubBlock: {subsubchunk_name}")                                
            else:
                self.error(f"Unsupported SubSubBlock: {subsubchunk_name} {subbytes[offset + suboffset:]}")  
                raise
            suboffset += subsubchunk_len

        return texture

    def read_surf_tags(self):
        """Read the list of PolyIDs and tag indexes."""
        self.info(f"    Reading Layer ({self.layers[-1].name}) Surface Assignments")
        bytes = self.bytes2
        offset = 0
        chunk_len = len(bytes)

        # Read in the PolyID/Surface Index pairs.
        abs_pid = len(self.layers[-1].pols) - self.last_pols_count
        if 0 == len(self.layers[-1].pols):
            return
        if abs_pid < 0:
            raise Exception(
                len(self.layers[-1].pols), self.last_pols_count, self.layers[-1].pols
            )
        while offset < chunk_len:
            pid, pid_len = self.read_vx(bytes[offset : offset + 4])
            offset += pid_len
            (sid,) = struct.unpack(">H", bytes[offset : offset + 2])
            offset += 2
            if sid not in self.layers[-1].surf_tags:
                self.layers[-1].surf_tags[sid] = []
            self.layers[-1].surf_tags[sid].append(pid + abs_pid)

    def read_surf(self):
        """Read the object's surface data."""
        bytes = self.bytes2
        if len(self.surfs) == 0:
            self.info("Reading Object Surfaces")

        surf = _obj_surf()
        name, name_len = self.read_lwostring(bytes)
        if len(name) != 0:
            surf.name = name

        #self.debug(f"{name}, {name_len}")
        # We have to read this, but we won't use it...yet.
        s_name, s_name_len = self.read_lwostring(bytes[name_len:])
        offset = name_len + s_name_len
        block_size = len(bytes)
        while offset < block_size:
            (subchunk_name,) = struct.unpack("4s", bytes[offset : offset + 4])
            offset += 4
            (subchunk_len,) = struct.unpack(">H", bytes[offset : offset + 2])
            offset += 2
            #self.debug(f"read_surf {subchunk_name}, {subchunk_len}")
            

            # Now test which subchunk it is.
            if b"COLR" == subchunk_name:
                surf.colr = struct.unpack(">fff", bytes[offset : offset + 12])
                # Don't bother with any envelopes for now.

            elif b"DIFF" == subchunk_name:
                (surf.diff,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"LUMI" == subchunk_name:
                (surf.lumi,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"SPEC" == subchunk_name:
                (surf.spec,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"REFL" == subchunk_name:
                (surf.refl,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"RBLR" == subchunk_name:
                (surf.rblr,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"TRAN" == subchunk_name:
                (surf.tran,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"RIND" == subchunk_name:
                (surf.rind,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"TBLR" == subchunk_name:
                (surf.tblr,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"TRNL" == subchunk_name:
                (surf.trnl,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"GLOS" == subchunk_name:
                (surf.glos,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"SHRP" == subchunk_name:
                (surf.shrp,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"SMAN" == subchunk_name:
                (s_angle,) = struct.unpack(">f", bytes[offset : offset + 4])
                # self.debug(s_angle)
                if s_angle > 0.0:
                    surf.smooth = True
            elif b"BUMP" == subchunk_name:
                (surf.bump,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"BLOK" == subchunk_name:
                (block_type,) = struct.unpack("4s", bytes[offset : offset + 4])
                (num,) = struct.unpack(">H", bytes[offset + 4 : offset + 6])
                texture = None
                if (
                       b"IMAP" == block_type
                    or b"PROC" == block_type
                    or b"SHDR" == block_type
                    or b"GRAD" == block_type
                ):
                    delta = 0
                    if 44 == num: # FIXME, don't know why this hack is needed
                        delta = 2
                    texture = self.read_texture(bytes, offset, subchunk_len, delta)
                else:
                    self.error(f"Unimplemented texture type: {block_type}")
                
                if None is not texture:
                    texture.type = block_type.decode("ascii")
                    if texture.channel not in surf.textures.keys():
                        surf.textures[texture.channel] = []
                    surf.textures[texture.channel].append(texture)
#                     if texture.channel not in surf.textures2:
#                         surf.textures2[texture.channel] = []
#                     surf.textures2[texture.channel].append(texture)
            elif b"VERS" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")
            elif b"NODS" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"GVAL" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"NVSK" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"CLRF" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"CLRH" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"ADTR" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"SIDE" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"RFOP" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"RIMG" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"TIMG" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"TROP" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"ALPH" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"BUF1" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"BUF2" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"BUF3" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"BUF4" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"LINE" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"NORM" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"RFRS" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"VCOL" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"RFLS" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"CMNT" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"FLAG" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"RSAN" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"LCOL" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"LSIZ" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            elif b"TSAN" == subchunk_name:
                self.debug(f"Unimplemented SubChunk: {subchunk_name}")  
            else:
                self.error(f"Unsupported SubBlock: {subchunk_name}")    

            offset += subchunk_len

        self.surfs[surf.name] = surf

    def parse_tags(self):
        chunkname = self.rootchunk.chunkname
        if b"TAGS" == chunkname:
            self.read_tags()
        elif b"LAYR" == chunkname:
            self.read_layr()
        elif b"PNTS" == chunkname:
            self.read_pnts()
        elif b"VMAP" == chunkname:
            vmap_type = self.rootchunk.read(4)

            if vmap_type == b"WGHT":
                self.read_weightmap()
            elif vmap_type == b"MORF":
                self.read_morph(False)
            elif vmap_type == b"SPOT":
                self.read_morph(True)
            elif vmap_type == b"TXUV":
                self.read_uvmap()
            elif vmap_type == b"RGB " or vmap_type == b"RGBA":
                self.read_colmap()
            elif vmap_type == b"NORM":
                self.read_normmap()
            elif vmap_type == b"PICK":
                self.rootchunk.skip()  # SKIPPING
            else:
                self.debug(f"Skipping vmap_type: {vmap_type}")
                self.rootchunk.skip()

        elif b"VMAD" == chunkname:
            vmad_type = self.rootchunk.read(4)

            if vmad_type == b"TXUV":
                self.read_uv_vmad()
            elif vmad_type == b"RGB " or vmad_type == b"RGBA":
                self.read_color_vmad()
            elif vmad_type == b"WGHT":
                # We only read the Edge Weight map if it's there.
                self.read_weight_vmad()
            elif vmad_type == b"NORM":
                self.read_normal_vmad()
            else:
                self.debug(f"Skipping vmad_type: {vmad_type}")
                self.rootchunk.skip()

        elif b"POLS" == chunkname:
            face_type = self.rootchunk.read(4)
            self.just_read_bones = False
            # PTCH is LW's Subpatches, SUBD is CatmullClark.
            if (
                face_type == b"FACE" or face_type == b"PTCH" or face_type == b"SUBD"
            ):
                self.read_pols()
                if face_type != b"FACE":
                    self.layers[-1].has_subds = True
            elif face_type == b"BONE":
                self.read_bones()
                self.just_read_bones = True
            else:
                self.debug(f"Skipping face_type: {face_type}")
                self.rootchunk.skip()

        elif b"PTAG" == chunkname:
            (tag_type,) = struct.unpack("4s", self.rootchunk.read(4))
            if tag_type == b"SURF" and not self.just_read_bones:
                # Ignore the surface data if we just read a bones chunk.
                self.read_surf_tags()

            elif self.ch.skel_to_arm:
                if tag_type == b"BNUP":
                    self.read_bone_tags("BNUP")
                elif tag_type == b"BONE":
                    self.read_bone_tags("BONE")
                elif tag_type == b"PART":
                    self.rootchunk.skip()  # SKIPPING
                elif tag_type == b"COLR":
                    self.rootchunk.skip()  # SKIPPING
                else:
                    self.debug(f"Skipping tag: {tag_type}")
                    self.rootchunk.skip()
            else:
                self.debug(f"Skipping tag_type: {tag_type}")
                self.rootchunk.skip()
        elif b"SURF" == chunkname:
            self.read_surf()
        elif b"CLIP" == chunkname:
            self.read_clip()
        elif b"BBOX" == chunkname:
            self.rootchunk.skip()  # SKIPPING
            self.debug(f"Unimplemented Chunk: {chunkname}")  
        elif b"VMPA" == chunkname:
            self.rootchunk.skip()  # SKIPPING
            self.debug(f"Unimplemented Chunk: {chunkname}")  
        elif b"PNTS" == chunkname:
            self.rootchunk.skip()  # SKIPPING
            self.debug(f"Unimplemented Chunk: {chunkname}")  
        elif b"POLS" == chunkname:
            self.rootchunk.skip()  # SKIPPING
            self.debug(f"Unimplemented Chunk: {chunkname}")  
        elif b"PTAG" == chunkname:
            self.rootchunk.skip()  # SKIPPING
            self.debug(f"Unimplemented Chunk: {chunkname}")  
        elif b"ENVL" == chunkname:
            self.rootchunk.skip()  # SKIPPING
            self.debug(f"Unimplemented Chunk: {chunkname}")  
        else:
            self.error(f"Skipping Chunk: {chunkname}")       
            self.rootchunk.skip()
 
