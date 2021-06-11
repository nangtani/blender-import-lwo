import struct
import chunk

from .lwoBase import LWOBase, _lwo_base, _obj_layer, _obj_surf

#, _obj_surf, _surf_texture, _surf_position
class _surf_texture_5(_lwo_base):
    __slots__ = ("id", "image", "X", "Y", "Z")

    def __init__(self):
        self.clipid = id(self)
        self.rev = 5
        self.image = None
        self.X = False
        self.Y = False
        self.Z = False


class LWO1(LWOBase):
    """Read version 1 file, LW < 6."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_types = [b"LWOB", b"LWLO"]

    def read_layr(self):
        """Read the object's layer data."""
        bytes = self.bytes2
        # XXX: Need to check what these two exactly mean for a LWOB/LWLO file.
        new_layr = _obj_layer()
        new_layr.index, flags = struct.unpack(">HH", bytes[0:4])

        self.info("Reading Object Layer")
        offset = 4
        layr_name, name_len = self.read_lwostring(bytes[offset:])
        offset += name_len

        if name_len > 2 and layr_name != "noname":
            new_layr.name = layr_name
        else:
            new_layr.name = f"Layer {new_layr.index}"

        self.layers.append(new_layr)

    def read_pols(self):
        """
        Read the polygons, each one is just a list of point indexes.
        But it also includes the surface index.
        """
        bytes = self.bytes2
        self.info(f"    Reading Layer ({self.layers[-1].name}) Polygons")
        offset = 0
        chunk_len = len(bytes)
        old_pols_count = len(self.layers[-1].pols)
        poly = 0

        while offset < chunk_len:
            (pnts_count,) = struct.unpack(">H", bytes[offset : offset + 2])
            offset += 2
            all_face_pnts = []
            for j in range(pnts_count):
                (face_pnt,) = struct.unpack(">H", bytes[offset : offset + 2])
                offset += 2
                all_face_pnts.append(face_pnt)
            all_face_pnts.reverse()

            self.layers[-1].pols.append(all_face_pnts)
            (sid,) = struct.unpack(">h", bytes[offset : offset + 2])
            offset += 2
            sid = abs(sid) - 1
            if sid not in self.layers[-1].surf_tags:
                self.layers[-1].surf_tags[sid] = []
            self.layers[-1].surf_tags[sid].append(poly)
            poly += 1

        return len(self.layers[-1].pols) - old_pols_count

    def read_surf(self):
        """Read the object's surface data."""
        bytes = self.bytes2
        if len(self.surfs) == 0:
            self.info("Reading Object Surfaces 5")

        surf = _obj_surf()
        name, name_len = self.read_lwostring(bytes)
        if len(name) != 0:
            surf.name = name

        offset = name_len
        chunk_len = len(bytes)
        while offset < chunk_len:
            (subchunk_name,) = struct.unpack("4s", bytes[offset : offset + 4])
            offset += 4
            (subchunk_len,) = struct.unpack(">H", bytes[offset : offset + 2])
            offset += 2

            # Now test which subchunk it is.
            if b"COLR" == subchunk_name:
                color = struct.unpack(">BBBB", bytes[offset : offset + 4])
                surf.colr = [color[0] / 255.0, color[1] / 255.0, color[2] / 255.0]

            elif b"DIFF" == subchunk_name:
                (surf.diff,) = struct.unpack(">h", bytes[offset : offset + 2])
                surf.diff /= 256.0  # Yes, 256 not 255.

            elif b"LUMI" == subchunk_name:
                (surf.lumi,) = struct.unpack(">h", bytes[offset : offset + 2])
                surf.lumi /= 256.0

            elif b"SPEC" == subchunk_name:
                (surf.spec,) = struct.unpack(">h", bytes[offset : offset + 2])
                surf.spec /= 256.0

            elif b"REFL" == subchunk_name:
                (surf.refl,) = struct.unpack(">h", bytes[offset : offset + 2])
                surf.refl /= 256.0

            elif b"TRAN" == subchunk_name:
                (surf.tran,) = struct.unpack(">h", bytes[offset : offset + 2])
                surf.tran /= 256.0

            elif b"RIND" == subchunk_name:
                (surf.rind,) = struct.unpack(">f", bytes[offset : offset + 4])

            elif b"GLOS" == subchunk_name:
                (surf.glos,) = struct.unpack(">h", bytes[offset : offset + 2])

            elif b"SMAN" == subchunk_name:
                (s_angle,) = struct.unpack(">f", bytes[offset : offset + 4])
                if s_angle > 0.0:
                    surf.smooth = True

            elif subchunk_name in [b"CTEX", b"DTEX", b"STEX", b"RTEX", b"TTEX", b"BTEX", b"LTEX"]:
                texture = None

            elif b"TIMG" == subchunk_name:
                path, path_len = self.read_lwostring(bytes[offset:])
                if path == "(none)":
                    offset += path_len
                    continue

                texture = _surf_texture_5()
                self.clips[texture.clipid] = path
                surf.textures_5.append(texture)
                
                if texture.clipid not in surf.textures2:
                    surf.textures2[texture.clipid] = []
                surf.textures2[texture.clipid].append(texture)

            elif b"TFLG" == subchunk_name:
                if texture:
                    (mapping,) = struct.unpack(">h", bytes[offset : offset + 2])
                    if mapping & 1:
                        texture.X = True
                    elif mapping & 2:
                        texture.Y = True
                    elif mapping & 4:
                        texture.Z = True
            elif b"FLAG" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"VLUM" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"VDIF" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"VSPC" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"VRFL" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"VTRN" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"RFLT" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"ALPH" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TOPC" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TWRP" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TSIZ" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TCTR" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TAAS" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TVAL" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TFP0" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TAMP" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"RIMG" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TCLR" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TFAL" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TVEL" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TREF" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TALP" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"EDGE" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"GLOW" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TIP0" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TFP1" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TFP2" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"TFP3" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"SPBF" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"SHDR" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"SDAT" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            elif b"IMSQ" == subchunk_name:
                self.debug(f"Unimplemented SubBlock: {subchunk_name}")  
            else:
                self.error(f"Unsupported SubBlock: {subchunk_name}")
                #self.debug(f"Unsupported SubBlock: {subchunk_name}")

            offset += subchunk_len

        self.surfs[surf.name] = surf
    
    def parse_tags(self):
        chunkname = self.rootchunk.chunkname
        if b"SRFS" == chunkname:
            self.read_tags()
        elif b"LAYR" == chunkname:
            self.read_layr()
        elif b"PNTS" == chunkname:
            if len(self.layers) == 0:
                # LWOB files have no LAYR chunk to set this up.
                nlayer = _obj_layer()
                nlayer.name = "Layer 1"
                self.layers.append(nlayer)
            self.read_pnts()
        elif b"POLS" == chunkname:
            self.last_pols_count = self.read_pols()
        elif b"PCHS" == chunkname:
            self.last_pols_count = self.read_pols()
            self.layers[-1].has_subds = True
        elif b"PTAG" == chunkname:
            (tag_type,) = struct.unpack("4s", self.rootchunk.read(4))
            if tag_type == b"SURF":
                raise Exception("Missing commented out function")
            #                     read_surf_tags_5(
            #                         self.rootchunk.read(), self.layers, self.last_pols_count
            #                     )
            else:
                self.rootchunk.skip()
        elif b"SURF" == chunkname:
            self.read_surf()
        else:
            # For Debugging \/.
            # if handle_layer:
            self.error(f"Skipping Chunk: {chunkname}")
            self.rootchunk.skip()
