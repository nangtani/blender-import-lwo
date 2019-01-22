### Object Files

November 9, 2001

This document describes the LWO2 file format for 3D objects used by LightWave®. The LWO2 format is new for LightWave® 6.0. Also see the  [Object File Examples](http://static.lightwave3d.com/sdk/11-6/html/filefmts/lwo2ex/lwo2ex.html)  supplement.

-   [Introduction](#introduction)
-   [Data Types](#data-types)
-   [Chunks](#chunks)
-   [Envelope Subchunks](#envelope-subchunks)
-   [Clip Subchunks](#clip-subchunks)
-   [Surface Subchunks](#surface-subchunks)
    -   [Basic Surface Parameters](#basic-surface-parameters)
    -   [Surface Blocks](#surface-blocks)
        -   [Ordinal Strings](#ordinal-strings)
        -   [Block Headers](#block-headers)
        -   [Texture Mapping](#texture-mapping)
        -   [Image Maps](#image-maps)
        -   [Procedurals](#procedural-textures)
        -   [Gradients](#gradient-textures)
        -   [Shaders](#shaders)
-   [Chunk Index](#chunk-index)

## Introduction

The data in LightWave 3D® object files comprise the points, polygons and surfaces that describe the geometry and appearance of an object. "Polygons" here means any of several geometric elements (faces, curves or patches, for example) defined by an ordered list of points, and "surfaces" refers to the collection of attributes, sometimes called materials, that define the visual surface properties of polygons.

Object files can contain multiple layers, or parts, and each part can be a single connected mesh or several disjoint meshes. They may also contain one or more surface definitions with no points or polygons at all. Surface definitions can include references to other files (images, for example), plug-ins, and envelopes containing parameter values that vary over time.

This document outlines the object file format and provides a detailed reference for each of the components. The component descriptions include both a regular expression defining the syntax and a discussion of the contents. See also the  [Examples](http://static.lightwave3d.com/sdk/11-6/html/filefmts/lwo2ex/lwo2ex.html)  supplement, a more conversational introduction to the format that includes annotated listings of file contents as well as several sample files.

## Data Types

The atomic, or lowest-level, types used in object files are listed below. All of these are written in a byte order variously called big-endian, Motorola, or network order, with the most significant byte written first. The shorthand names (**I2**,  **F4**, etc.) will be used throughout this document.

##### _ID Tag_

> ID4

An ID tag is a sequence of 4 bytes containing 7-bit ASCII values, usually upper-case printable characters. These tags are used to identify the data that follows.  FORM,  SURF,  POLS, and  LWO2  are all examples of ID tags. ID tags can be interpreted as unsigned integers for comparison purposes.

##### _Signed Integer_

> I1, I2, I4

##### _Unsigned Integer_

> U1, U2, U4

Integers can be signed or unsigned and 1, 2 or 4 bytes in length. Signed integers are two's complement.

##### _Float_

> F4

4-byte IEEE floating-point values.

##### _String_

> S0

Names or other character strings are written as a series of ASCII character values followed by a zero (or null) byte. If the length of the string including the null terminating byte is odd, an extra null is added so that the data that follows will begin on an even byte boundary.

Several useful composite datatypes are built from these fundamental types.

##### _Variable-length Index_

> VX ::= index[[U2]](#unsigned-integer)  | (index + 0xFF000000)[[U4]](#unsigned-integer)

This is an index into an array of items (points or polygons), or a collection of items each uniquely identified by an integer (clips or envelopes). A VX is written as a variable length 2- or 4-byte element. If the index value is less than 65,280 (0xFF00), then the index is written as an unsigned two-byte integer. Otherwise the index is written as an unsigned four byte integer with bits 24-31 set. When reading an index, if the first byte encountered is 255 (0xFF), then the four-byte form is being used and the first byte should be discarded or masked out.

##### _Color_

> COL12 ::= red[[F4]](#float), green[[F4]](#float), blue[[F4]](#float)

A color is written as a triple of floats representing the levels of red, green and blue. The nominal level range is [0.0, 1.0], but values outside this range are also possible.

##### _Coordinate_

> VEC12 ::= X[[F4]](#float), Y[[F4]](#float), Z[[F4]](#float)

3D coordinates are written as an XYZ vector in floating point format. The values are distances along the X, Y, and Z axes.

##### _Percentage_

> FP4 ::= fraction[[F4]](#float)

Percentages are written as floats, with 1.0 representing 100%.

##### _Angle_

> ANG4 ::= radians[[F4]](#float)

Angles are specified as floating point values in radians.

##### _Filename_

> FNAM0 ::= name[[S0]](#string)

Filenames are written as strings in a platform-neutral format. For absolute (fully qualified) paths, the first node represents a disk or similar storage device, and its name is separated from the rest of the path by a colon. Other nodes in the path are separated by forward slashes.  disk:path/file  is an absolute path, and  path/subpath/file  is a relative path.

## Chunks

The object file format is derived from the metaformat for binary files described in "[EA IFF 85 Standard for Interchange Format Files](http://static.lightwave3d.com/sdk/11-6/html/filefmts/eaiff85.html)."  The basic structural element  in an IFF file is the  _chunk_. A chunk consists of an ID tag, a size, and  _size_  bytes of data. If the size is odd, the chunk is followed by a 0 pad byte, so that the next chunk begins on an even byte boundary. (The pad byte isn't counted in the size.)

> CHUNK ::= tag[[ID4]](#id-tag), length[[U4]](#unsigned-integer), data[...], pad[[U1]](#unsigned-integer) ?

Within some chunks, object files use  _subchunks_, which are just like chunks except that the size is a 2-byte integer.

> SUB-CHUNK ::= tag[[ID4]](#id-tag), length[[U2]](#unsigned-integer), data[...], pad[[U1]](#unsigned-integer)  ?

In this document, chunks will be written as a chunk ID followed by a data description inside curly brackets:  **ID-tag { data }**. Given this notation, we can say formally that an object file is a  FORM  chunk of type  LWO2.

> file ::= FORM { 'LWO2'[[ID4]](#id-tag), data[[CHUNK]]((#chunks))  * }

Informally, object files start with the four bytes "FORM" followed by a four-byte integer giving the length of the file (minus 8) and the four byte ID "LWO2". The remainder of the data is a collection of chunks, some of which will contain subchunks.

To be read, IFF files must be  _parsed_. The order in which chunks can occur in a file isn't fixed. Some chunks, however, contain data that depends on the contents of other chunks, and this fixes a  _relative_  order for the chunks involved. Chunks and subchunks also depend on context for their meaning. The  CHAN  subchunk in an envelope chunk isn't the same thing as the  CHAN  subchunk in a surface block. And you may encounter chunks that aren't defined here, which you should be prepared to skip gracefully if you don't understand them. You can do this by using the chunk size to seek to the next chunk.

The following is a list of the defined chunks that can be found in an object file. Full descriptions of the contents of  ENVL,  CLIP  and  SURF  chunks are deferred to sections that follow the chunk list and comprise the remainder of this document.

##### _Layer_

> LAYR { number[[U2]](#unsigned-integer), flags[[U2]](#unsigned-integer), pivot[[VEC12]]((#coordinate)), name[[S0]](#string), parent[[U2]](#unsigned-integer)  ? }

Signals the start of a new layer. All the data chunks which follow will be included in this layer until another layer chunk is encountered. If data is encountered before a layer chunk, it goes into an arbitrary layer. If the least significant bit of  flags  is set, the layer is hidden. The parent index indicates the default parent for this layer and can be -1 or missing to indicate no parent.

##### _Point List_

> PNTS { point-location[[VEC12]]((#coordinate))  * }

Lists (_x_,  _y_,  _z_) coordinate triples for a set of points. The number of points in the chunk is just the chunk size divided by 12. The  PNTS  chunk must precede the  [POLS](#discontinuous-vertex-mapping) chunks that refer to it. These chunks list points using a 0-based index into  PNTS.

The LightWave® coordinate system is left-handed, with +X to the right or east, +Y upward, and +Z forward or north. Object files don't contain explicit units, but by convention the unit is meters. Coordinates in  PNTS  are relative to the pivot point of the layer.

#####  _Vertex Mapping_

> VMAP { type[[ID4]](#id-tag), dimension[[U2]](#unsigned-integer), name[[S0]](#string),  
> ( vert[[VX]]((#variable-length-index)), value[[F4]](#float)  # dimension )* }

Associates a set of floating-point vectors with a set of points.  VMAPs begin with a type, a dimension (vector length) and a name. These are followed by a list of vertex/vector pairs. The vertex is given as an index into the most recent  [PNTS](#point-list) chunk, in  [VX]((#variable-length-index))  format. The vector contains  dimension  floating-point values. There can be any number of these chunks, but they should all have different types or names.

Some common type codes are

- **PICK**

    - Selection set. This is a  VMAP  of dimension 0 that marks points for quick selection by name during modeling. It has no effect on the geometry of the object.

- **WGHT**

    - Weight maps have a dimension of 1 and are generally used to alter the influence of deformers such as bones. Weights can be positive or negative, and the default weight for unmapped vertices is 0.0.

- **MNVW**

    - Subpatch weight maps affect the shape of geometry created by subdivision patching.

- **TXUV**

    - UV texture maps have a dimension of 2.

- **RGB**,  **RGBA**

    - Color maps, with a dimension of 3 or 4.

- **MORF**

    - These contain vertex displacement deltas.

- **SPOT**

    - These contain absolute vertex displacements (alternative vertex positions).

Other widely used map types will almost certainly appear in the future.

#####  _Polygon List_

> POLS { type[[ID4]](#id-tag), ( numvert+flags[[U2](#unsigned-integer)], vert[[VX](#variable-length-index)]  # numvert )* }

A list of polygons for the current layer. Possible polygon types include:

- **FACE**
 
    - "Regular" polygons, the most common.

- **CURV**

    - Catmull-Rom splines. These are used during modeling and are currently ignored by the renderer.

- **PTCH**

    - Subdivision patches. The  POLS  chunk contains the definition of the control cage polygons, and the patch is created by subdividing these polygons. The renderable geometry that results from subdivision is determined interactively by the user through settings within LightWave®. The subdivision method is undocumented.

- **MBAL**

    - Metaballs. These are single-point polygons. The points are associated with a  [VMAP]((#uv-vertex-map))  of type  MBAL  that contains the radius of influence of each metaball. The renderable polygonal surface constructed from a set of metaballs is inferred as an isosurface on a scalar field derived from the sum of the influences of all of the metaball points.

- **BONE**

    - Line segments representing the object's skeleton. These are converted to bones for deformation during rendering.

Each polygon is defined by a vertex count followed by a list of indexes into the most recent  [PNTS](#point-list) chunk. The maximum number of vertices is 1023. The 6 high-order bits of the vertex count are flag bits with different meanings for each polygon type. When reading  POLS, remember to mask out the  flags  to obtain  numverts. (For  CURV  polygon: The two low order flags are for continuity control point toggles. The four remaining high order flag bits are additional vertex count bits; this brings the maximum number of vertices for  CURV  polygons to 2^14 = 16383.)

When writing  POLS, the vertex list for each polygon should begin at a convex vertex and proceed clockwise as seen from the visible side of the polygon. LightWave® polygons are single-sided (although  [double-sidedness](#polygon-sidedness) is a possible surface property), and the normal is defined as the cross product of the first and last edges.

##### _Tag Strings_

> TAGS { tag-string[[S0]](#string)  * }

Lists the tag strings that can be associated with polygons by the  [PTAG]((#polygon-tag-mapping))  chunk.

##### _Polygon Tag Mapping_

> PTAG { type[[ID4]](#id-tag), ( poly[[VX]]((#variable-length-index)), tag[[U2]](#unsigned-integer)  )* }

Associates tags of a given type with polygons in the most recent  [POLS](#polygon-list) chunk. The most common polygon tag types are

-  **SURF**

    - The surface assigned to the polygon. The actual surface attributes are found by matching the name in the [TAGS]((#tag-strings))  chunk with the name in a [SURF](#surface-definition) chunk.
 
-  **PART**

    - The part the polygon belongs to. Parts are named groups of polygons analogous to point selection sets (but a polygon can belong to only one part).

-  **SMGP**

    - The smoothing group the polygon belongs to. Shading is only interpolated within a smoothing group, not across groups.

The polygon is identified by an index into the previous  [POLS](#polygon-list) chunk, and the tag is given by an index into the previous  [TAGS]((#tag-strings))  chunk. Not all polygons will have a value for every tag type. The behavior for polygons lacking a given tag depends on the type.

##### Discontinuous Vertex Mapping_

> VMAD { type[[ID4]](#id-tag), dimension[[U2]](#unsigned-integer), name[[S0]](#string),  
( vert[[VX]]((#variable-length-index)), poly[[VX]]((#variable-length-index)), value[[F4]](#float)  # dimension )* }

(Introduced with LightWave® 6.5.) Associates a set of floating-point vectors with the vertices of specific polygons.  VMADs are similar to  [VMAP]((#uv-vertex-map))s, but they assign vectors to polygon vertices rather than points. For a given mapping, a  [VMAP]((#uv-vertex-map))  always assigns only one vector to a point, while a  VMAD  can assign as many vectors to a point as there are polygons sharing the point.

The motivation for  VMADs is the problem of seams in UV texture mapping. If a UV map is topologically equivalent to a cylinder or a sphere, a seam is formed where the opposite edges of the map meet. Interpolation of UV coordinates across this discontinuity is aesthetically and mathematically incorrect. The  VMAD  substitutes an equivalent mapping that interpolates correctly. It only needs to do this for polygons in which the seam lies.

VMAD  chunks are paired with  [VMAP]((#uv-vertex-map))s of the same name, if they exist. The vector values in the  VMAD  will then replace those in the corresponding  [VMAP]((#uv-vertex-map)), but only for calculations involving the specified polygons. When the same points are used for calculations on polygons not specified in the  VMAD, the  [VMAP]((#uv-vertex-map))  values are used.

VMADs need not be associated with a  [VMAP]((#uv-vertex-map)). They can also be used simply to define a (discontinuous) per-polygon mapping. But not all mapping types are valid for  VMADs, since for some types it makes no sense for points to have more than one map value.  TXUV,  RGB,  RGBA  and  WGHT  types are supported for  VMADs, for example, while  MORF  and  SPOT  are not.  VMADs of unsupported types are preserved but never evaluated.

##### _Vertex Map Parameter_

> VMPA { UV subdivision type[[I4]](#signed-integer), sketch color[[I4]](#signed-integer)  }

Describes special properties of VMAPs.  
The UV subdivision type ids are:  

```
0 - linear  
1 - subpatch  
2 - subpatch linear corners  
3 - subpatch linear edges  
4 - subpatch disco edges
```
##### _Envelope Definition_

> [ENVL](#envelope-subchunks) { index[[VX]]((#variable-length-index)), attributes[[SUB-CHUNK]]((#chunks))  * }

An array of keys. Each  ENVL  chunk defines the value of a single parameter channel as a function of time. The index is used to identify this envelope uniquely and can have any non-zero value less than 0x1000000. Following the index is a collection of subchunks that describe the envelope. These are documented below, in the  [Envelope Subchunks](#envelope-subchunks) section.

##### _Image or Image Sequence_

> [CLIP](#clip-subchunks) { index[[U4]](#unsigned-integer), attributes[[SUB-CHUNK]]((#chunks))  * }

Describes an image or a sequence of images. Surface definitions specify images by referring to  CLIP  chunks. The term "clip" is used to describe these because they can be numbered sequences or animations as well as stills. The index identifies this clip uniquely and may be any non-zero value less than 0x1000000. The filename and any image processing modifiers follow as a variable list of subchunks, which are documented below in the  [Clip Subchunks](#clip-subchunks) section.

##### _Surface Definition_

> [SURF](#surface-sub-chunks) { name[[S0]](#string), source[[S0]](#string), attributes[[SUB-CHUNK]]((#chunks))  * }

Describes the shading attributes of a surface. The name uniquely identifies the surface. This is the string that's stored in  [TAGS]((#tag-strings))  and referenced by tag index in  [PTAG]((#polygon-tag-mapping)). If the source name is non-null, then this surface is derived from, or composed with, the source surface. The base attributes of the source surface can be overridden by this surface, and texture blocks can be added to the source surface. The material attributes follow as a variable list of subchunks documented below in the  [Surface Subchunks](#surface-sub-chunks) section.

##### _Bounding Box_

> BBOX { min[[VEC12]]((#coordinate)), max[[VEC12]]((#coordinate))  }

Store the bounding box for the vertex data in a layer. Optional. The  min  and  max  vectors are the lower and upper corners of the bounding box.

##### _Description Line_

> DESC { description-line[[S0]](#string)  }

Store an object description. Optional. This should be a simple line of upper and lowercase characters, punctuation and spaces which describes the contents of the object file. There should be no control characters in this text string and it should generally be kept short.

##### _Commentary Text_

> TEXT { comment[[S0]](#string)  }

Store comments about the object. Optional. The text is just like the  [DESC](#description-line) chunk, but it can be about any subject, it may contain newline characters and it does not need to be particularly short.

##### _Thumbnail Icon Image_

> ICON { encoding[[U2]](#unsigned-integer), width[[U2]](#unsigned-integer), data[[U1]](#unsigned-integer)  * }

An iconic or thumbnail image for the object which can be used when viewing the file in a browser. Currently the only suported  encoding  is 0, meaning uncompressed RGB byte triples. The  width  is the number of pixels in each row of the image, and the height (number of rows) is  (chunkSize - 4)/width. This chunk is optional.

## Envelope Subchunks

The  [ENVL](#envelope-definition) chunk contains a series of subchunks describing the keyframes, intervals and global attributes of a single envelope. Note that the  PRE,  KEY  and  TCB  IDs each include a trailing space when written in the file.

##### _Envelope Type_

> TYPE { user-format[[U1]](#unsigned-integer), type[[U1]](#unsigned-integer)  }

The type subchunk records the format in which the envelope is displayed to the user and a type code that identifies the components of certain predefined envelope triples. The user format has no effect on the actual values, only the way they're presented in LightWave®'s interface.

- **02**  - Float
- **03**  - Distance
- **04**  - Percent
- **05**  - Angle

The predefined envelope types include the following.

- **01, 02, 03**  - Position: X, Y, Z
- **04, 05, 06**  - Rotation: Heading, Pitch, Bank
- **07, 08, 09**  - Scale: X, Y, Z
- **0A, 0B, 0C**  - Color: R, G, B
- **0D, 0E, 0F**  - Falloff: X, Y, Z

##### _Pre-Behavior_

> PRE { type[[U2]](#unsigned-integer)  }

The pre-behavior for an envelope defines the signal value for times before the first key. The type code selects one of several predefined behaviors.

- **0 - Reset**

    - Sets the value to 0.0.

- **1 - Constant**

    - Sets the value to the value at the nearest key.

- **2 - Repeat**

    - Repeats the interval between the first and last keys (the primary interval).

- **3 - Oscillate**

    - Like Repeat, but alternating copies of the primary interval are time-reversed.

- **4 - Offset Repeat**

    - Like Repeat, but offset by the difference between the values of the first and last keys.

- **5 - Linear**

    - Linearly extrapolates the value based on the tangent at the nearest key.

##### _Post-Behavior_

> POST { type[[U2]](#unsigned-integer)  }

The post-behavior determines the signal value for times after the last key. The type codes are the same as for pre-behaviors.

##### _Keyframe Time and Value_

> KEY { time[[F4]](#float), value[[F4]](#float)  }

The value of the envelope at the specified time in seconds. The signal value between keyframes is interpolated. The time of a keyframe isn't restricted to integer frames.

##### _Interval Interpolation_

> SPAN { type[[ID4]](#id-tag), parameters[[F4]](#float)  * }

Defines the interpolation between the most recent  KEY  chunk and the  KEY  immediately before it in time. The  type  identifies the interpolation algorithm and can be  STEP,  LINE,  TCB  (Kochanek-Bartels),  HERM  (Hermite),  BEZI  (1D Bezier) or  BEZ2  (2D Bezier). Different parameters are stored for each of these.

##### _Plug-in Channel Modifiers_

> CHAN { server-name[[S0]](#string), flags[[U2]](#unsigned-integer), data[...] }

[Channel modifiers](http://static.lightwave3d.com/sdk/11-6/html/classes/channel.html)  can be associated with an envelope. Each channel chunk contains the name of the plug-in and some flag bits. Only the first flag bit is defined; if set, the plug-in is disabled. The data that follows this, if any, is owned by the plug-in.

##### _Channel Name_

> NAME { channel-name[[S0]](#string)  }

An optional name for the envelope. LightWave® itself ignores the names of surface envelopes, but plug-ins can browse the envelope database by name.

The source code in the  [sample/envelope](http://static.lightwave3d.com/sdk/11-6/sample/Layout/ChannelFilter/envelope/)  directory of the LightWave® plug-in SDK demonstrates interpolation and extrapolation of envelopes and shows how the contents of the  SPAN  subchunks define TCB, Bezier and Hermite curves.

## Clip Subchunks

The  [CLIP](#image-or-image-sequence)  chunk contains a series of subchunks describing a single, possibly time-varying image. The first subchunk has to be one of the source chunks:  STIL,  ISEQ,  ANIM,  XREF  or  STCC.

##### _Still Image_

> STIL { name[[FNAM0]]((#filename))  }

The source is a single still image referenced by a filename in neutral path format.

##### _Image Sequence_

> ISEQ { num-digits[[U1]](#unsigned-integer), flags[[U1]](#unsigned-integer), offset[[I2]](#signed-integer), reserved[[U2]](#unsigned-integer), start[[I2]](#signed-integer), end[[I2]](#signed-integer), prefix[[FNAM0]]((#filename)), suffix[[S0]](#string)  }

The source is a numbered sequence of still image files. Each filename contains a fixed number of decimal digits that specify a frame number, along with a prefix (the part before the frame number, which includes the path) and a suffix (the part after the number, typically a PC-style extension that identifies the file format). The prefix and suffix are the same for all files in the sequence.

The flags include bits for looping and interlace. The offset is added to the current frame number to obtain the digits of the filename for the current frame. The start and end values define the range of frames in the sequence.

##### _Plug-in Animation_

> ANIM { filename[[FNAM0]]((#filename)), server-name[[S0]](#string), flags[[U2]](#unsigned-integer), data[...] }

This chunk indicates that the source imagery comes from a plug-in animation loader. The loader is defined by the server name, a flags value, and the server's data.

##### _Reference (Clone)_

> XREF { index[[U4]](#unsigned-integer), string[[S0]](#string)  

The source is a copy, or instance, of another clip, given by the index. The string is a unique name for this instance of the clip.

##### _Color-cycling Still_

> STCC { lo[[I2]](#signed-integer), hi[[I2]](#signed-integer), name[[FNAM0]]((#filename))  

A still image with color-cycling is a source defined by a neutral-format name and cycling parameters.  lo  and  hi  are indexes into the image's color table. Within this range, the color table entries are shifted over time to cycle the colors in the image. If  lois less than  hi, the colors cycle forward, and if  hi  is less than  lo, they go backwards.

Except for the  TIME  subchunk, the subchunks after the source subchunk modify the source image and are applied as filters layered on top of the source image.

##### _Time_

> TIME { start-time[[FP4]](#percentage), duration[[FP4]](#percentage), frame-rate[[FP4]](#percentage)  }

Defines source times for an animated clip.

##### _Color Space RGB_

> CLRS { flags[[U2]](#signed-integer4), colorspace[[U2]](#signed-integer4), filename[[FNAM0]]((#filename))  }

Contains the color space of the texture. If the flag is 0, then the color space is contained in the following 2 bytes. That color space is defined by the LWCOLORSPACE enum. If the flag is set to 1, then the file name of the color space is save as a local string.

##### _Color Space Alpha_

> CLRA { flags[[U2]](#signed-integer4), colorspace[[U2]](#signed-integer4), filename[[FNAM0]]((#filename))  }

Contains the color space of the texture alpha. If the flag is 0, then the color space is contained in the following 2 bytes. That color space is defined by the LWCOLORSPACE enum. If the flag is set to 1, then the file name of the color space is save as a local string.

##### _Image Filtering_

> FILT { flags[[U2]](#signed-integer4)  }

Contains the index to the current image filtering.

##### _Image Dithering_

> DITH { flags[[U2]](#signed-integer4)  }

Contains the index to the current image dithering.

##### _Contrast_

> CONT { contrast-delta[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

RGB levels are altered in proportion to their distance from 0.5. Positive deltas move the levels toward one of the extremes (0.0 or 1.0), while negative deltas move them toward 0.5. The default is 0.

##### _Brightness_

> BRIT { brightness-delta[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

The delta is added to the RGB levels. The default is 0.

##### _Saturation_

> SATR { saturation-delta[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

The saturation of an RGB color is defined as  (max - min)/max, where  max  and  min  are the maximum and minimum of the three RGB levels. This is a measure of the intensity or purity of a color. Positive deltas turn up the saturation by increasing the  maxcomponent and decreasing the  min  one, and negative deltas have the opposite effect. The default is 0.

##### _Hue_

> HUE { hue-rotation[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

The hue of an RGB color is an angle defined as

> r is max: 1/3 (g - b)/(r - min)  
> g is max: 1/3 (b - r)/(g - min) + 1/3  
> b is max: 1/3 (r - g)/(b - min) + 2/3

with values shifted into the [0, 1] interval when necessary. The levels between 0 and 1 correspond to angles between 0 and 360 degrees. The hue delta rotates the hue. The default is 0.

##### _Gamma Correction_

> GAMM { gamma[[F4]](#float), envelope[[VX]]((#variable-length-index))  }

Gamma correction alters the distribution of light and dark in an image by raising the RGB levels to a small power. By convention, the gamma is stored as the inverse of this power. A gamma of 0.0 forces all RGB levels to 0.0. The default is 1.0.

##### _Negative_

> NEGA { enable[[U2]](#unsigned-integer)  }

If non-zero, the RGB values are inverted, (1.0 - r, 1.0 - g, 1.0 - b), to form a negative of the image.

##### _Plug-in Image Filters_

> IFLT { server-name[[S0]](#string), flags[[U2]](#unsigned-integer), data[...] }

Plug-in image filters can be used to pre-filter an image before rendering. The filter has to be able to exist outside of the special environment of rendering in order to work here (it can't depend on functions or data that are only available during rendering). Filters are given by a server name, an enable flag, and data bytes that belong to the plug-in.

##### _Plug-in Pixel Filters_

> PFLT { server-name[[S0]](#string), flags[[U2]](#unsigned-integer), data[...] }

Pixel filters may also be used as clip modifiers, and they are stored and used in a way that is exactly like image filters.

## Surface Subchunks

The subchunks found in  [SURF](#surface-definition) chunks can be divided into two types. Basic surface parameters are stored in simple subchunks with no nested subchunks, while texture and shader data is stored in surface blocks containing nested subchunks.

### Basic Surface Parameters

The following surface subchunks define the base characteristics of a surface. These are the "start" values for the surface, prior to texturing and plug-in shading, and correspond to the options on the main window of the LightWave® Surface Editor. Even if textures and shaders completely obscure the base appearance of the surface in final rendering, these settings are still used for previewing and real-time rendering.

##### _Base Color_

> COLR { base-color[[COL12]]((#color)), envelope[[VX]]((#variable-length-index))  }

The base color of the surface, which is the color that lies under all the other texturing attributes.

##### _Base Shading Values_

> DIFF, LUMI, SPEC, REFL, TRAN, TRNL { intensity[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

The base level of the surface's diffuse, luminosity, specular, reflection, transparency, or translucency settings. Except for diffuse, if any of these subchunks is absent for a surface, a value of zero is assumed. The default diffuse value is 1.0.

##### _Specular Glossiness_

> GLOS { glossiness[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

Glossiness controls the falloff of specular highlights. The intensity of a specular highlight is calculated as cos_n_  _a_, where  _a_  is the angle between the reflection and view vectors. The power  _n_  is the specular exponent. The  GLOS  chunk stores a glossiness  _g_  as a floating point fraction related to  _n_  by:  _n_  = 2(10_g_  + 2). A glossiness of 20% (0.2) gives a specular exponent of 24, or 16, equivalent to the "Low" glossiness preset in versions of LightWave® prior to 6.0. Likewise 40% is 64 or "Medium," 60% is 256 or "High," and 80% is 1024 or "Maximum." The  GLOS  subchunk is only meaningful when the specularity in  [SPEC](#base-shading-values)  is non-zero. If  GLOS  is missing, a value of 40% is assumed.

##### _Diffuse Sharpness_

> SHRP { sharpness[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

Diffuse sharpness models non-Lambertian surfaces. The sharpness refers to the transition from lit to unlit portions of the surface, where the difference in diffuse shading is most obvious. For a sharpness of 0.0, diffuse shading of a sphere produces a linear gradient. A sharpness of 50% (0.5) corresponds to the fixed "Sharp Terminator" switch in versions of LightWave® prior to 6.0. It produces planet-like shading on a sphere, with a brightly lit day side and a rapid falloff near the day/night line (the terminator). 100% sharpness is more like the Moon, with no falloff until just before the terminator.

##### _Bump Intensity_

> BUMP { strength[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

Bump strength scales the height of the bumps in the gradient calculation. Higher values have the effect of increasing the contrast of the bump shading. The default value is 1.0.

##### _Polygon Sidedness_

> SIDE { sidedness[U2](#unsigned-integer) }

The sidedness of a polygon can be 1 for front-only, or 3 for front and back. If missing, single-sided polygons are assumed.

##### _Max Smoothing Angle_

> SMAN { max-smoothing-angle[[ANG4]]((#angle))  }

The maximum angle between adjacent polygons that will be smooth shaded. Shading across edges at higher angles won't be interpolated (the polygons will appear to meet at a sharp seam). If this chunk is missing, or if the value is <= 0, then the polygons are not smoothed.

##### _Reflection Options_

> RFOP { reflection-options[[U2]](#unsigned-integer)  }

Reflection options is a numeric code that describes how reflections are handled for this surface and is only meaningful if the reflectivity in  [REFL](#base-shading-values) is non-zero.

- **0 - Backdrop Only**

    - Only the backdrop is reflected.

- **1 - Raytracing + Backdrop**

    - Objects in the scene are reflected when raytracing is enabled. Rays that don't intercept an object are assigned the backdrop color.

- **2 - Spherical Map**

    - If an image is provided in an  [RIMG](#reflection-map-image) subchunk, the image is reflected as if it were spherically wrapped around the scene.

- **3 - Raytracing + Spherical Map**

    - Objects in the scene are reflected when raytracing is enabled. Rays that don't intercept an object are assigned a color from the image map.

If there is no  RFOP  subchunk, a value of 0 is assumed.

##### _Reflection Map Image_

> RIMG { image[[VX]]((#variable-length-index))  }

A surface reflects this image as if it were spherically wrapped around the scene. The  RIMG  is only used if the reflection options in  [RFOP](#base-shading-values) is non-zero. The image is the index of a  [CLIP](#image-or-image-sequence)  chunk, or zero to indicate no image.

##### _Reflection Map Image Seam Angle_

> RSAN { seam-angle[[ANG4]]((#angle)), envelope[[VX]]((#variable-length-index))  }

This angle is the heading angle of the reflection map seam. If missing, a value of zero is assumed.

##### _Reflection Blurring_

> RBLR { blur-percentage[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

The amount of blurring of reflections. The default is zero.

##### _Refractive Index_

> RIND { refractive-index[[F4]](#float), envelope[[VX]]((#variable-length-index))  }

The surface's index of refraction. This is used to bend refraction rays when raytraced refraction is enabled in the scene. The value is the ratio of the speed of light in a vacuum to the speed of light in the material (always >= 1.0 in the real world). The default is 1.0.

##### _Transparency Options_

> TROP { transparency-options[[U2]](#unsigned-integer)  }

The transparency options are the same as the reflection options in  [RFOP]((#reflection-options)), but for refraction.

##### _Refraction Map Image_

> TIMG { image[[VX]]((#variable-length-index))  }

Like  [RIMG]((#reflection-map-image)), but for refraction.

##### _Refraction Blurring_

> TBLR { blur-percentage[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

The amount of refraction blurring. The default is zero.

##### _Color Highlights_

> CLRH { color-highlights[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

Specular highlights are ordinarily the color of the incident light. Color highlights models the behavior of dialectric and conducting materials, in which the color of the specular highlight tends to be closer to the color of the material. A higher color highlight value blends more of the surface color and less of the incident light color.

##### _Color Filter_

> CLRF { color-filter[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

The color filter percentage determines the amount by which rays passing through a transparent surface are tinted by the color of the surface.

##### _Additive Transparency_

> ADTR { additive[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

Additive transparency is a simple rendering trick that works independently of the mechanism associated with the  [TRAN](#TRAN) and related settings. The color of the surface is added to the color of the scene elements behind it in a proportion controlled by the additive value.

##### _Glow Effect_

> GLOW { type[[U2]](#unsigned-integer), intensity[[F4]](#float), intensity-envelope[[VX]]((#variable-length-index)), size[[F4]](#float), size-envelope[[VX]]((#variable-length-index))  }

The glow effect causes a surface to spread and affect neighboring areas of the image. The type can be 0 for Hastings glow, and 1 for image convolution. The size and intensity define how large and how strong the effect is.

You may also encounter glow information written in a  GVAL  subchunk containing only the intensity and its envelope (the subchunk length is 6).

##### _Render Outlines_

> LINE { flags[[U2]](#unsigned-integer), ( size[[F4]](#float), size-envelope[[VX]]((#variable-length-index)), ( color[[COL12]]((#color)), color-envelope[[VX]]((#variable-length-index))  )? )? }

The line effect draws the surface as a wireframe of the polygon edges. Currently the only flag defined is an enable switch in the low bit. The size is the thickness of the lines in pixels, and the color, if not given, is the base color of the surface. Note that you may encounter  LINE  subchunks with no color information (these will have a subchunk length of 8 bytes) and possibly without size information (subchunk length 2).

##### _Alpha Mode_

> ALPH { mode[[U2]]((#unsigned-integer)), value[[FP4]](#percentage)  }

The alpha mode defines the alpha channel output options for the surface.

- **0 - Unaffected by Surface**

    - The surface has no effect on the alpha channel when rendered.

- **1 - Constant Value**

    - The alpha channel will be written with the constant value following the mode in the subchunk.

- **2 - Surface Opacity**

    - The alpha value is derived from surface opacity, which is the default if the  ALPH  chunk is missing.

- **3 - Shadow Density**

    - The alpha value comes from the shadow density.

##### _Vertex Color Map_

> VCOL { intensity[[FP4]](#percentage), envelope[[VX]]((#variable-length-index)), vmap-type[[ID4]](#id-tag), name[[S0]](#string)  }

The vertex color map subchunk identifies an  RGB  or  RGBA  [VMAP]((#uv-vertex-map))  that will be used to color the surface.

### Surface Blocks

A surface may contain any number of  _blocks_  which hold texture layers or shaders. Each block is defined by a subchunk with the following format.

> BLOK { header[[SUB-CHUNK]]((#chunks)), attributes[[SUB-CHUNK]]((#chunks))  * }

Since this regular expression hides much of the structure of a block, it may be helpful to visualize a typical texture block in outline form.

-   block
    -   header
        -   ordinal string
        -   channel
        -   enable flag
        -   opacity...
    -   texture mapping
        -   center
        -   size...
    -   other attributes...

The first subchunk is the header. The subchunk ID specifies the block type, and the subchunks within the header subchunk define properties that are common to all block types. The ordinal string defines the sorting order of the block relative to other blocks. The header is followed by other subchunks specific to each type. For some texture layers, one of these will be a texture mapping subchunk that defines the mapping from object to texture space. All of these components are explained in the following sections.

#### Ordinal Strings

Each  BLOK  represents a texture layer applied to one of the surface channels, or a shader plug-in applied to the surface. If more than one layer is applied to a channel, or more than one shader is applied to the surface, we need to know the evaluation order of the layers or shaders, or in what order they are "stacked." The ordinal string defines this order.

Readers can simply compare ordinal strings using the C  strcmp  function to sort the  BLOKs into the correct order. Writers of  LWO2  files need to generate valid ordinal strings that put the texture layers and shaders in the right order. See the  [Object Examples](http://static.lightwave3d.com/sdk/11-6/html/filefmts/lwo2ex/lwo2ex.html#imap)  supplement for an example function that generates ordinal strings.

To understand how LightWave® uses these, imagine that instead of strings, it used floating-point fractions as the ordinals. Whenever LightWave® needed to insert a new block between two existing blocks, it would find the new ordinal for the inserted block as the average of the other two, so that a block inserted between ordinals 0.5 and 0.6 would have an ordinal of 0.55.

But floating-point ordinals would limit the number of insertions to the (fixed) number of bits used to represent the mantissa. Ordinal strings are infinite-precision fractions written in base 255, using the ASCII values 1 to 255 as the digits (0 isn't used, since it's the special character that marks the end of the string).

Ordinals can't end on a 1, since that would prevent arbitrary insertion of other blocks. A trailing 1 in this system is like a trailing 0 in decimal, which can lead to situations like this,

   0.5    "\x80"
   0.50   "\x80\x01"

where there's no daylight between the two ordinals for inserting another block.

#### Block Headers

Every block contains a header subchunk.

> block-header { ordinal[[S0]](#string), block-attributes[[SUB-CHUNK]]((#chunks))  * }

The ID of the header subchunk identifies the block type and can be one of the following.

- **IMAP**  - an image map texture  
- **PROC**  - a procedural texture  
- **GRAD**  - a gradient texture  
- **SHDR**  - a shader plug-in

The header contains an ordinal string (described above) and subchunks that are common to all block types.

##### _Channel_

> CHAN { texture-channel[[ID4]](#id-tag)  }

This is required in all texture layer blocks and can have a value of  [COLR](#base-color),  [DIFF](#base-shading-values),  [LUMI](#base-shading-values),  [SPEC](#base-shading-values),  [GLOS](#specular-glosiness),  [REFL](#base-shading-values),  [TRAN](#base-shading-values),  [RIND](#refractive-index),  [TRNL](#base-shading-values), or  [BUMP]((#brightness)), The texture layer is applied to the corresponding surface attribute. If present in a shader block, this value is ignored.

##### _Enable State_

> ENAB { enable[[U2]](#unsigned-integer)  }

True if the texture layer or shader should be evaluated during rendering. If  ENAB  is missing, the block is assumed to be enabled.

##### _Opacity_

> OPAC { type[[U2]](#unsigned-integer), opacity[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

Opacity is valid only for texture layers. It specifies how opaque the layer is with respect to the layers before it (beneath it) on the same channel, or how the layer is combined with the previous layers. The types can be

- 0 - Normal  
- 1 - Subtractive  
- 2 - Difference  
- 3 - Multiply  
- 4 - Divide  
- 5 - Alpha  
- 6 - Texture Displacement  
- 7 - Additive

Alpha opacity uses the current layer as an alpha channel. The previous layers are visible where the current layer is white and transparent where the current layer is black. Texture Displacement distorts the underlying layers. If  OPAC  is missing, 100% Additive opacity is assumed.

##### _Displacement Axis_

> AXIS { displacement-axis[[U2]](#unsigned-integer)  }

For displacement mapping, defines the plane from which displacements will occur. The value is 0, 1 or 2 for the X, Y or Z axis.

#### Texture Mapping

Image map and procedural textures employ the  TMAP  subchunk to define the mapping they use to get from object or world coordinate space to texture space.

> TMAP { attributes[[SUB-CHUNK]]((#chunks))  * }

The  TMAP  subchunk contains a set of attribute chunks which describe the different aspects of this mapping.

##### _Position, Orientation and Size_

> CNTR, SIZE, ROTA { vector[[VEC12]]((#coordinate)), envelope[[VX]]((#variable-length-index))  }

These subchunks each consist of a vector for the texture's size, center and rotation. The size and center are normal positional vectors in meters, and the rotation is a vector of heading, pitch and bank in radians. If missing, the center and rotation are assumed to be zero. The size should always be specified if it si to be used for any given mapping.

##### _Reference Object_

> OREF { object-name[[S0]](#string)  }

Specifies a reference object for the texture. The reference object is given by name, and the scene position, rotation and scale of the object are combined with the previous chunks to compute the texture mapping. If the object name is "(none)" or  OREF  is missing, no reference object is used.

##### _Falloff_

> FALL { type[[U2]](#unsigned-integer), vector[[VEC12]]((#coordinate)), envelope[[VX]]((#variable-length-index))  }

Texture effects may fall off with distance from the texture center if this subchunk is present. The vector represents a rate per unit distance along each axis. The type can be

- **0 - Cubic**

    - Falloff is linear along all three axes independently.

- **1 - Spherical**

    - Falloff is proportional to the Euclidean distance from the center.

- **2 - Linear X** 
- **3 - Linear Y** 
- **4 - Linear Z**

    - Falloff is linear only along the specified axis. The other two vector components are ignored.

##### _Coordinate System_

> CSYS { type[[U2]](#unsigned-integer)  }

The coordinate system can be 0 for object coordinates (the default if the chunk is missing) or 1 for world coordinates.

#### Image Maps

Texture blocks with a header type of  IMAP  are image maps. These use an image to modulate one of the surface channels. In addition to the basic parameters listed below, the block may also contain a  [TMAP](#texture-mapping)  chunk.

##### _Projection Mode_

> PROJ { projection-mode[[U2]](#unsigned-integer)  }

The projection defines how 2D coordinates in the image are transformed into 3D coordinates in the scene. In the following list of projections, image coordinates are called  _r_  (horizontal) and  _s_  (vertical).

- **0 - Planar**

    - The image is projected on a plane along the major axis (specified in the  [AXIS]((#major-axis))  subchunk).  _r_  and  _s_  map to the other two axes.

- **1 - Cylindrical**

    - The image is wrapped cylindrically around the major axis.  _r_  maps to longitude (angle around the major axis).

- **2 - Spherical**

    - The image is wrapped spherically around the major axis.  _r_  and  _s_map to longitude and latitude.

- **3 - Cubic**

    - Like Planar, but projected along all three axes. The dominant axis of the geometric normal selects the projection axis for a given surface spot.

- **4 - Front Projection**

T    - he image is projected on the current camera's viewplane.  _r_  and  _s_map to points on the viewplane.

- **5 - UV**

    - _r_  and  _s_  map to points (_u_,  _v_) defined for the geometry using a vertex map (identified in the  BLOK's  [VMAP](#uv-vertex-map) subchunk).

##### _Major Axis_

> AXIS { texture-axis[[U2]](#unsigned-integer)  }

The major axis used for planar, cylindrical and spherical projections. The value is 0, 1 or 2 for the X, Y or Z axis.

##### _Image Map_

> IMAG { texture-image[[VX]]((#variable-length-index))  }

The  CLIP  index of the mapped image.

##### _Image Wrap Options_

> WRAP { width-wrap[[U2]](#unsigned-integer), height-wrap[[U2]](#unsigned-integer)  }

Specifies how the color of the texture is derived for areas outside the image.

- **0 - Reset**

    - Areas outside the image are assumed to be black. The ultimate effect of this depends on the opacity settings. For an additive texture layer on the color channel, the final color will come from the preceding layers or from the base color of the surface.

- **1 - Repeat**

    - The image is repeated or tiled.

- **2 - Mirror**

    - Like repeat, but alternate tiles are mirror-reversed.

- **3 - Edge**

    - The color is taken from the image's nearest edge pixel.

If no wrap options are specified, 1 is assumed.

##### _Image Wrap Amount_

> WRPW, WRPH { cycles[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

For cylindrical and spherical projections, these parameters control how many times the image repeats over each full interval.

##### _UV Vertex Map_

> VMAP { txuv-map-name[[S0]](#string)  }

For UV projection, which depends on texture coordinates at each vertex, this selects the name of the  TXUV  [vertex map]((#uv-vertex-map))  that contains those coordinates.

##### _Antialiasing Strength_

> AAST { flags[[U2]](#unsigned-integer), antialising-strength[[FP4]](#percentage)  }

The low bit of the flags word is an enable flag for texture antialiasing. The antialiasing strength is proportional to the width of the sample filter, so larger values sample a larger area of the image.

##### _Pixel Blending_

> PIXB { flags[[U2]](#unsigned-integer)  }

Pixel blending enlarges the sample filter when it would otherwise be smaller than a single image map pixel. If the low-order flag bit is set, then pixel blending is enabled.

##### _Sticky Projection_

> STCK { on-off[[U2]](#unsigned-integer), time[[FP4]](#percentage)  }

The "sticky" or fixed projection time for front projection image maps. When on, front projections will be fixed at the given time.

##### _Texture Amplitude_

> TAMP { amplitude[[FP4]](#percentage), envelope[[VX]]((#variable-length-index))  }

Appears in image texture layers applied to the bump channel. Texture amplitude scales the bump height derived from the pixel values. The default is 1.0.

#### Procedural Textures

Texture blocks of type  PROC  are procedural textures that modulate the value of a surface channel algorithmically.

##### _Axis_

> AXIS { axis[[U2]](#unsigned-integer)  }

If the procedural has an axis, it may be defined with this chunk using a value of 0, 1 or 2.

##### _Basic Value_

> VALU { value[[FP4]](#percentage)  # (1, 3) }

Procedurals are often modulations between the current channel value and another value, given here. This may be a scalar or a vector.

##### _Algorithm and Parameters_

> FUNC { algorithm-name[[S0]](#string), data[...] }

The  FUNC  subchunk names the procedural and stores its parameters. The name will often map to a plug-in name. The variable-length data following the name belongs to the procedural.

#### Gradient Textures

Texture blocks of type  GRAD  are gradient textures that modify a surface channel by mapping an input parameter through an arbitrary transfer function. Gradients are represented to the user as a line containing keys. Each key is a color, and the gradient function is an interpolation of the keys in RGB space. The input parameter selects a point on the line, and the output of the texture is the value of the gradient at that point.

##### _Parameter Name_

> PNAM { parameter[[S0]](#string)  }

The input parameter. Possible values include

- "Previous Layer"  
- "Bump"  
- "Slope"  
- "Incidence Angle"  
- "Light Incidence"  
- "Distance to Camera"  
- "Distance to Object"  
- "X Distance to Object"  
- "Y Distance to Object"  
- "Z Distance to Object"  
- "Weight Map"

##### _Item Name_

 > INAM { item-name[[S0]](#string)  }

The name of a scene item. This is used when the input parameter is derived from a property of an item in the scene.

##### _Gradient Range_

> GRST, GREN { input-range[[FP4]](#percentage)  }

The start and end of the input range. These values only affect the display of the gradient in the user interface. They don't affect rendering.

##### _Repeat Mode_

> GRPT { repeat-mode[[U2]](#unsigned-integer)  }

The repeat mode. This is currently undefined.

##### _Key Values_

> FKEY { ( input[[FP4]](#percentage), output[[FP4]](#percentage)  # 4 )* }

The transfer function is defined by an array of keys, each with an input value and an RGBA output vector. Given an input value, the gradient can be evaluated by selecting the keys whose positions bracket the value and interpolating between their outputs. If the input value is lower than the first key or higher than the last key, the gradient value is the value of the closest key.

##### _Key Parameters_

> IKEY { interpolation[[U2]](#unsigned-integer)  * }

An array of integers defining the interpolation for the span preceding each key. Possible values include

- 0 - Linear  
- 1 - Spline  
- 2 - Step

#### Shaders

Shaders are  [BLOK]((#surface-block))  subchunks with a header type of  SHDR. They are applied to a surface after all basic channels and texture layers are evaluated, and in the order specified by the ordinal sequence. The only header chunk they support is  ENAB  and they need only one data chunk to describe them.

##### _Shader Algorithm_

> FUNC { algorithm-name[[S0]](#string), data[...] }

Just like a procedural texture layer, a shader is defined by an algorithm name (often a plug-in), followed by data owned by the shader.

## Chunk Index

- [AAST](#antialiasing-strength)  Image Map Antialiasing Strength  
- [ADTR](#additive-transparency)  Surface Additive Transparency  
- [ALPH](#alpha-mode)  Surface Alpha Mode  
- [ANIM](#plug-in-animation)  Clip Animation  
- [AXIS](#displacement-axis)  Displacement Axis  
- [AXIS](#major-axis)  Image Map Major Axis  
- [AXIS](#axis)  Procedural Texture Axis  

- [BBOX](#bounding-box)  Bounding Box  
- [BLOK](#surface-blocks)  Surface Block  
- [BRIT](#brightness)  Clip Brightness  
- [BUMP](#bump-intensity)  Surface Bump Intensity  

- [CHAN](#plug-in-channel-modifiers)  Channel Plug-in  
- [CHAN](#channel)  Texture Layer Channel  
- [CLIP](#image-or-image-sequence)  Image, Image Sequence  
- [CLRA](#color-space-alpha)  Color Space Alpha  
- [CLRF](#color-filter) Surface Color Filter  
- [CLRH](#color-highlights) Surface Color Highlights  
- [CLRS](#color-space-rgb) Color Space RGB  
- [CNTR](#position,-orientation-and-size) Texture Center  
- [COLR](#base-color) Surface Base Color  
- [CONT](#contrast) Clip Contrast  
- [CSYS](#coordinate-system) Texture Coordinate System  

- [DESC](#description-line) Description Line  
- [DIFF](#base-shading-values) Surface Diffuse  
- [DITH](#image-dithering) Image Dithering  

- [ENAB](#enable-state) Surface Block Enable  
- [ENVL](#envelope-definition) Envelope  

- [FALL](#falloff) Texture Falloff  
- [FILT](#image-filtering) Image Filtering  
- [FKEY](#key-values) Gradient Key Values  
- [FORM](#in-this-document) IFF Format File  
- [FUNC](#algorithm-and-parameters) Procedural Texture Algorithm  
- [FUNC](#shader-algorithm) Surface Shader Algorithm  

- [GAMM](#gamma-correction) Clip Gamma Correction  
- [GLOS](#specular-glossiness) Surface Specular Glossiness  
- [GLOW](#glow-effect) Surface Glow Effect  
- [GREN](#gradient-range) Gradient End  
- [GRPT](#repeat-mode) Gradient Repeat Mode  
- [GRST](#gradient-range) Gradient Start  

- [HUE](#hue)Clip Hue  

- [ICON](#thumbnail-icon-image) Thumbnail Icon Image  
- [IFLT](#plug-in-image-filters) Clip Image Filter  
- [IKEY](#key-parameters) Gradient Key Parameters  
- [IMAG](#image-map) Image Map Image  
- [INAM](#item-name) Gradient Item Name  
- [ISEQ](#image-sequence) Clip Image Sequence  

- [KEY](#keyframe-time-and-value)Keyframe Time and Value  

- [LAYR](#layer) Layer  
- [LINE](#render-outlines) Surface Render Outlines  
- [LUMI](#base-shading-values) Surface Luminosity  

- [NAME](#channel-name) Envelope Channel Name  
- [NEGA](#negative) Clip Negative  

- [OPAC](#opacity) Texture Layer Opacity  
- [OREF](#reference-object) Texture Reference Object  
- [PFLT](#plug-in-pixel-filters) Clip Pixel Filter  
- [PIXB](#pixel-blending) Image Map Pixel Blending  
- [PNAM](#parameter-name) Gradient Parameter Name  
- [PNTS](#point-list) Point List  
- [POLS](#polygon-list) Polygon List  
- [POST](#post-behavior) Envelope Post-Behavior  
- [PRE](#pre-behavior)Envelope Pre-Behavior  
- [PROJ](#projection-mode) Image Map Projection Mode  
- [PTAG]((#polygon-tag-mapping))  Polygon Tag Mapping  

- [RBLR](#reflection-blurring) Reflection Blurring  
- [REFL](#base-shading-values) Surface Reflectivity  
- [RFOP](#reflection-options) Surface Reflection Options  
- [RIMG](#reflection-map-image) Surface Reflection Map Image  
- [RIND](#refractive-index) Surface Refractive Index  
- [ROTA](#position,-orientation-and-size) Texture Rotation  
- [RSAN](#reflection-map-image-seam-angle) Surface Reflection Map Image Seam Angle  

- [SPAN](#interval-interpolation) Envelope Interval Interpolation  
- [SATR](#saturation) Clip Saturation  
- [SHRP](#diffuse-sharpness) Surface Diffuse Sharpness  
- [SIDE](#polygon-sidedness) Surface Polygon Sidedness  
- [SIZE](#position,-orientation-and-size) Texture Size  
- [SMAN](#max-smoothing-angle) Surface Max Smoothing Angle  
- [SPEC](#base-shading-values) Surface Specularity  
- [STCC](#color-cycling-still) Clip Color-cycling Still  
- [STCK](#sticky-projection) Sticky Projection  
- [STIL](#still-image) Clip Still Image  
- [SURF](#surface-definition) Surface Definition  

- [TAGS]((#tag-strings))  Tag Strings  
- [TAMP](#texture-amplitude) Image Map Texture Amplitude  
- [TBLR](#refraction-blurring) Refraction Blurring  
- [TEXT](#commentary-text) Commentary Text  
- [TIME](#time) Clip Time  
- [TIMG](#refraction-map-image) Surface Refraction Map Image  
- [TMAP](#tmap) Texture Mapping  
- [TRAN](#base-shading-values) Surface Transparency  
- [TRNL](#base-shading-values) Surface Translucency  
- [TROP](#transparency-options) Surface Transparency Options  
- [TYPE](#envelope-type) Envelope Type  

- [VALU](#basic-value) Procedural Texture Value  
- [VCOL](#vertex-color-map) Surface Vertex Color Map  
- [VMAD](#discontinuous-vertex-mapping) Discontinuous Vertex Map  
- [VMAP]((#uv-vertex-map))  Vertex Map  
- [VMAP](#uv-vertex-map) Image Map UV Vertex Map  

- [WRAP](#image-wrap-options) Image Map Wrap Options  
- [WRPW](#image-wrap-amount) Image Map Width Wrap Amount  
- [WRPH](#image-wrap-amount) Image Map Height Wrap Amount  

- [XREF](#reference-clone) Clip Reference (Clone)

[Original Link](http://static.lightwave3d.com/sdk/11-6/html/filefmts/lwo2.html) 

[Wayback Link](https://web.archive.org/web/20151028210222/http://static.lightwave3d.com/sdk/11-6/html/filefmts/lwo2.html)

