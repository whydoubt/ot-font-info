#!/usr/bin/env python3

import sys
from struct import unpack, iter_unpack
from datetime import datetime


verbose = False


def _verify_checksum(data, checksum):
    pass


_handlers = {}
def handles(tag):
    def real_handles(func):
        def wrapped(data):
            func(tag, data)
        _handlers[tag] = wrapped
        return func
    return real_handles

#
# Required tables for TrueType fonts
#

@handles(b'cmap')
def _cmap_handler(tag, data):
    '''Handler for the Character To Glyph Index Mapping Table

    https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6cmap.html
    https://docs.microsoft.com/en-us/typography/opentype/spec/cmap

    '''
    print('Character To Glyph Index Mapping Table [cmap]:')
    (version, num_tables) = unpack('>HH', data[:4])

    print(f'    Version: {version}')
    print(f'    Number of Encoding Tables: {num_tables}')

    table_offset = 4
    for _ in range(num_tables):
        (platform_id, platform_specific_id, offset) = unpack('>2HI',
                data[table_offset:table_offset+8])
        table_offset += 8

        print(f'    Encoding ({platform_id}, {platform_specific_id}):')

        (format_,) = unpack('>H', data[offset:offset+2])

        if format_ in {0, 2, 4, 6}:
            (length, language) = unpack('>2H', data[offset+2:offset+6])
            offset += 6
        elif format_ in {8, 10, 12, 13}:
            (length, language) = unpack('>2I', data[offset+4:offset+12])
            offset += 12
        elif format_ == 14:
            (length,) = unpack('>I', data[offset+2:offset+6])
            language = None
            offset += 6
        else:
            print('        Unknown Encoding Format: {format_}')
            continue

        print(f'        Encoding Format: {format_}')
        if language is not None:
            print(f'        Language: {language}')
        print('        Mapping:')

        if format_ == 0:
            for glyph_id_index in range(256):
                if glyph_id_index % 16 == 0:
                    print(' '*12, end='')
                print(f'{data[offset+glyph_id_index]:4d}', end='')
                if glyph_id_index % 16 == 15:
                    print()
        elif format_ == 4:
            (seg_count_x2, search_range, entry_selector,
                    range_shift) = unpack('>4H', data[offset:offset+8])
            offset += 8

            end_code = iter_unpack('>H', data[offset:offset+seg_count_x2])
            end_code = [x for (x,) in end_code]
            offset += seg_count_x2 + 2
            start_code = iter_unpack('>H', data[offset:offset+seg_count_x2])
            start_code = [x for (x,) in start_code]
            offset += seg_count_x2
            id_delta = iter_unpack('>h', data[offset:offset+seg_count_x2])
            id_delta = [x for (x,) in id_delta]
            offset += seg_count_x2
            id_range_offset = iter_unpack('>H', data[offset:offset+seg_count_x2])
            id_range_offset = [x for (x,) in id_range_offset]

            print(' '*12 + f'Segment Count \xd7 2: {seg_count_x2}')
            print(' '*12 + f'Search Range: {search_range}')
            print(' '*12 + f'Entry Selector: {entry_selector}')
            print(' '*12 + f'Range Shift: {range_shift}')
            print(' '*12 + f'List of (Start Code, End Code, Index Delta, Index Range Offset):')
            for i, (start, end, delta, range_offset) in enumerate(zip(
                    start_code, end_code, id_delta, id_range_offset)):
                if not verbose and i >= 12:
                    print(' '*16 + '...')
                    print(' '*16 + '[Use -v to see the full table]')
                    print(' '*16 + '...')
                    break

                print(' '*16 + f'({start},{end},{delta},{range_offset})', end='')
                if range_offset == 0:
                    start_glyph = (start + delta) % 0x10000
                    if start == end:
                        print(f' [{start} => {start_glyph}]')
                    else:
                        end_glyph = (end + delta) % 0x10000
                        print(f' [{start}..{end} => {start_glyph}..{end_glyph}]')
                else:
                    range_offset += offset + i*2
                    range_size = (end - start + 1) * 2
                    range_ = iter_unpack('>H', data[range_offset:range_offset+range_size])
                    range_ = [x+delta if x!=0 else 0 for (x,) in range_]
                    print(f' [{start}..{end} => {range_}]')
        elif format_ == 6:
            (first_code, entry_count) = unpack('>2H', data[offset:offset+4])
            offset += 4
            groups = iter_unpack('>H', data[offset:offset+entry_count*2])

            print(' '*12 + f'First Code: {first_code}')
            print(' '*12 + f'Number of Entries: {entry_count}')
            for index, (glyph_id,) in enumerate(groups):
                if index % 8 == 0:
                    print(' '*12, end='')
                print(f'{glyph_id:5d}', end='')
                if index % 8 == 7 or index == entry_count-1:
                    print()

        elif format_ == 12:
            (num_groups,) = unpack('>I', data[offset:offset+4])
            offset += 4
            groups = iter_unpack('>3I', data[offset:offset+num_groups*12])

            print(' '*12 + f'Number of Groups: {num_groups}')
            print(' '*12 + f'List of (Start Code, End Code, Start Glyph):')
            for i, (start, end, start_glyph) in enumerate(groups):
                if not verbose and i >= 12:
                    print(' '*16 + '...')
                    print(' '*16 + '[Use -v to see the full table]')
                    print(' '*16 + '...')
                    break

                print(' '*16 + f'({start},{end},{start_glyph})', end='')
                if start == end:
                    print(f' [{start} => {start_glyph}]')
                else:
                    end_glyph = end + start_glyph - start
                    print(f' [{start}..{end} => {start_glyph}..{end_glyph}]')

        else:
            print(' '*12 + '...')

@handles(b'glyf')
def _glyf_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'head')
def _head_handler(tag, data):
    '''Handler for the Global Font Information Header Table

    https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6head.html
    https://docs.microsoft.com/en-us/typography/opentype/spec/head

    '''
    print('Global Font Information Header Table [head]:')

    (version, font_revision,
        checksum_adjustment, magic_number, flags,
        units_per_em, created, modified,
        x_min, y_min, x_max, y_max,
        mac_style, lowest_rec_ppem, font_direction_hint,
        index_to_loc_format, glyph_data_format) = unpack(
                '>2i2I2H2q4h2H3h', data)
    # Convert times from seconds since 1904 Jan 01
    try:
        created_datetime = datetime.fromtimestamp(created - 2082844800)
    except (ValueError, OSError):
        created_datetime = 'Out of range'
    try:
        modified_datetime = datetime.fromtimestamp(modified - 2082844800)
    except (ValueError, OSError):
        modified_datetime = 'Out of range'

    print(f'    Version: {round(version/0x10000,5)}')
    print(f'    Font Revision: {round(font_revision/0x10000,5)}')
    print(f'    Checksum Adjustment: 0x{checksum_adjustment:08X}')
    print(f'    Magic Number: 0x{magic_number:08X}')
    print(f'    Flags: 0x{flags:04X}')
    print(f'    Units Per Em: {units_per_em}')
    print(f'    Time Created: {created} [{created_datetime}]')
    print(f'    Time Modified: {modified} [{modified_datetime}]')
    print(f'    Min/Max x: {x_min} {x_max}')
    print(f'    Min/Max y: {y_min} {y_max}')
    print(f'    Mac Style: 0x{mac_style:04X}')
    print(f'    Smallest Readable Size in Pixels: {lowest_rec_ppem}')
    print(f'    Font Direction Hint: {font_direction_hint}')
    print(f'    Index to Loc Format: {index_to_loc_format}')
    print(f'    Glyph Data Format: {glyph_data_format}')

@handles(b'hhea')
def _hhea_handler(tag, data):
    '''Handler for the Horizontal Header Layout Table

    https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6hhea.html
    https://docs.microsoft.com/en-us/typography/opentype/spec/hhea

    '''
    print('Horizontal Header Layout Table [hhea]:')

    (version, ascender, descender, line_gap,
        advance_width_max, min_left_side_bearing, min_right_side_bearing,
        x_max_extent, caret_slope_rise, caret_slope_run, caret_offset,
        metric_data_format, number_of_h_metrics) = unpack(
                '>i3hH6h8xhH', data)

    print(f'    Version: {round(version/0x10000,5)}')
    print(f'    Ascender: {ascender}')
    print(f'    Descender: {descender}')
    print(f'    Line Gap: {line_gap}')
    print(f'    Maximum Advance Width: {advance_width_max}')
    print(f'    Minimum Left Side Bearing: {min_left_side_bearing}')
    print(f'    Minimum Right Side Bearing: {min_right_side_bearing}')
    print(f'    Maximum x Extent: {x_max_extent}')
    print(f'    Caret Slope Rise/Run: {caret_slope_rise} {caret_slope_run}')
    print(f'    Caret Offset: {caret_offset}')
    print(f'    Metric Data Format: {metric_data_format}')
    print(f'    Number of hMetric entries in \'hmtx\' table: {number_of_h_metrics}')

@handles(b'hmtx')
def _hmtx_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'loca')
def _loca_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'maxp')
def _maxp_handler(tag, data):
    '''Handler for the Maximum Profile Table

    https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6maxp.html
    https://docs.microsoft.com/en-us/typography/opentype/spec/maxp

    '''
    print('Maximum Profile Table [maxp]:')

    (version, num_glyphs) = unpack('>iH', data[:6])

    print(f'    Version: {round(version/0x10000,5)}')
    print(f'    Number of Glyphs: {num_glyphs}')

    if version >= 0x10000:
        (max_points, max_contours, max_composite_points, max_composite_contours,
            max_zones, max_twilight_points, max_storage, max_function_defs,
            max_instruction_defs, max_stack_elements, max_size_of_instructions,
            max_component_elements, max_component_depth) = unpack('>13H', data[6:])
        print(f'    Maximum Points in Non-Composite Glyph: {max_points}')
        print(f'    Maximum Contours in Non-Composite Glyph: {max_contours}')
        print(f'    Maximum Points in Composite Glyph: {max_composite_points}')
        print(f'    Maximum Contours in Composite Glyph: {max_composite_contours}')
        print(f'    Maximum Zones Used: {max_zones}')
        print(f'    Maximum Points Used in Z0: {max_twilight_points}')
        print(f'    Number of Storage Area locations: {max_storage}')
        print(f'    Number of FDEFs: {max_function_defs}')
        print(f'    Number of IDEFs: {max_instruction_defs}')
        print(f'    Maximum Stack Depth: {max_stack_elements}')
        print(f'    Maximum Glyph Instruction Byte Count: {max_size_of_instructions}')
        print(f'    Maximum Top Level Components: {max_component_elements}')
        print(f'    Maximum Recursion Levels: {max_component_depth}')

@handles(b'name')
def _name_handler(tag, data):
    '''Handler for the Naming Table

    https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6name.html
    https://docs.microsoft.com/en-us/typography/opentype/spec/name

    '''
    print('Naming Table [name]:')

    name_id_list = [
        'Copyright notice',
        'Font Family name',
        'Font Subfamily name',
        'Unique font identifier',
        'Full font name',
        'Version string',
        'PostScript name',
        'Trademark',
        'Manufacturer Name',
        'Designer',
        'Description',
        'URL Vendor',
        'URL Designer',
        'License Description',
        'License Info URL',
        'Reserved(15)',
        'Typographic Family name',
        'Typographic Subfamily name',
        'Compatible Full',
        'Sample text',
        'PostScript CID findfont name',
        'WWS Family Name',
        'WWS Subfamily Name',
        'Light Background Palette',
        'Dark Background Palette',
        'Variations PostScript Name Prefix',
    ]

    (format_, count, string_offset) = unpack('>3H', data[:6])

    print(f'    Format: {format_}')
    print(f'    Number of Name Records: {count}')
    print('    Name Records:')

    table_offset = 6
    for _ in range(count):
        (platform_id, platform_specific_id, language_id, name_id,
            length, offset) = unpack('>6H', data[table_offset:table_offset+12])
        table_offset += 12
        name_offset = string_offset + offset
        name = data[name_offset:name_offset+length]
        if name_id < 26:
            name_id = name_id_list[name_id]

        encoding = (platform_id, platform_specific_id)
        try:
            if encoding in {(0, 0), (0, 3), (3, 0), (3, 1)}:
                name = name.decode('utf-16-be')
            elif encoding == (1, 0):
                name = name.decode('mac_roman')
            elif encoding == (1, 1):
                name = name.decode('x_mac_japanese')
            elif encoding == (1, 3):
                name = name.decode('x_mac_korean')
        except UnicodeDecodeError:
            name = f'[Decode error] {name}'

        print(f'        ({platform_id},{platform_specific_id},'
                       f'0x{language_id:X},{name_id}): {name}')

    if format_ == 1:
        (lang_tag_count,) = unpack('>H', data[table_offset:table_offset+2])

        print(f'    Number of Language Tag Records: {lang_tag_count}')
        print('    Language Tag Records:')

        table_offset += 2
        for i in range(lang_tag_count):
            (length, offset) = unpack('>2H', data[table_offset:table_offset+4])
            table_offset += 4
            lang_tag_offset = string_offset + offset
            lang_tag = data[lang_tag_offset:lang_tag_offset+length]

            print(f'        0x{0x8000+i:X}: {lang_tag}')

@handles(b'post')
def _post_handler(tag, data):
    '''Handle PostScript Table

    https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6post.html
    https://docs.microsoft.com/en-us/typography/opentype/spec/post

    '''
    print('PostScript Table [post]:')

    (version, italic_angle, underline_position, underline_thickness,
            is_fixed_pitch, min_mem_type_42, max_mem_type_42,
            min_mem_type_1, max_mem_type_1) = unpack('>2i2h5I', data[:32])
    offset = 32

    print(f'    Version: {round(version/0x10000,5)}')
    print(f'    Italic Angle: {round(italic_angle/0x10000,5)}')
    print(f'    Underline Position: {underline_position}')
    print(f'    Underline Thickness: {underline_thickness}')
    print(f'    Is Fixed Pitch: {is_fixed_pitch}')
    print(f'    Minimum Memory for Type 42: {min_mem_type_42}')
    print(f'    Maximum Memory for Type 42: {max_mem_type_42}')
    print(f'    Minimum Memory for Type 1: {min_mem_type_1}')
    print(f'    Maximum Memory for Type 1: {max_mem_type_1}')

    if version == 0x10000:
        print(f'    Using standard names table')
    if version == 0x20000:
        (num_glyphs,) = unpack('>H', data[offset:offset+2])
        offset += 2
        glyph_name_index = iter_unpack('>H', data[offset:offset+num_glyphs*2])
        offset += num_glyphs * 2
        names = list(range(258))
        while offset < len(data):
            name_size = data[offset]
            names.append(data[offset+1:offset+1+name_size])
            offset += name_size + 1
        glyph_name_list = [names[x] for (x,) in glyph_name_index]

        print(f'    Number of Glyphs: {num_glyphs}')
        if num_glyphs <= 96 or verbose:
            print(f'    Glyph Names: {glyph_name_list}')
        else:
            print('    ... [Use -v to see the glyph names list] ...')
    # Microsoft documentation indicates a value of 0x25000 for representing
    # version 2.5, but this is not consistent with other uses of version.
    if version == 0x28000:
        pass
    if version == 0x30000:
        pass
    if version == 0x40000:
        pass

#
# Optional tables for TrueType fonts
#

@handles(b'cvt ')
def _cvt__handler(tag, data):
    '''Handle Control Values Table

    https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6cvt.html
    https://docs.microsoft.com/en-us/typography/opentype/spec/cvt

    '''
    print('Control Values Table [cvt ]:')
    print(f'    Number of Control Values: {len(data)//4}')

@handles(b'fpgm')
def _fpgm_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'hdmx')
def _hdmx_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'kern')
def _kern_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'OS/2')
def _OS_2_handler(tag, data):
    '''Handle OS/2 and Windows Metrics Table

    https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6OS2.html
    https://docs.microsoft.com/en-us/typography/opentype/spec/os2

    '''
    print('OS/2 and Windows Metrics Table [OS/2]:')

    if len(data) < 68:
        print(f'WARNING: \'OS/2\' block of {len(data)} bytes, expected at least 68')
        return

    (version, avg_char_width, weight_class, width_class, type_,
        subscript_x_size, subscript_y_size,
        subscript_x_offset, subscript_y_offset,
        superscript_x_size, superscript_y_size,
        superscript_x_offset, superscript_y_offset,
        strikeout_size, strikeout_position,
        family_class, panose,
        unicode_range_1, unicode_range_2, unicode_range_3, unicode_range_4,
        vend_id, selection, first_char_index, last_char_index) = unpack(
                '>Hh2H12h10s4I4s3H', data[:68])
    selection_breakout = []
    if selection & 1:
        selection_breakout.append('ITALIC')
    if selection & 2:
        selection_breakout.append('UNDERSCORE')
    if selection & 4:
        selection_breakout.append('NEGATIVE')
    if selection & 8:
        selection_breakout.append('OUTLINED')
    if selection & 0x10:
        selection_breakout.append('STRIKEOUT')
    if selection & 0x20:
        selection_breakout.append('BOLD')
    if selection & 0x40:
        selection_breakout.append('REGULAR')
    if selection & 0x80:
        selection_breakout.append('USE_TYPO_METRICS')
    if selection & 0x100:
        selection_breakout.append('WWS')
    if selection & 0x200:
        selection_breakout.append('OBLIQUE')
    selection_breakout = ' '.join(selection_breakout)

    print(f'    Version: {version}')
    print(f'    Average Character Width: {avg_char_width}')
    print(f'    Weight Class: {weight_class}')
    print(f'    Width Class: {width_class}')
    print(f'    Type: {type_}')
    print(f'    Subscript: {subscript_x_size}\xd7{subscript_y_size}'
                      f' @ {subscript_x_offset},{subscript_y_offset}')
    print(f'    Superscript: {superscript_x_size}\xd7{superscript_y_size}'
                      f' @ {superscript_x_offset},{superscript_y_offset}')
    print(f'    Strikeout: {strikeout_size} @ {strikeout_position}')
    print(f'    Family Class: {family_class}')
    print('    Panose: ', end='')
    print(' '.join([bytes([b]).hex() for b in panose]))
    print(f'    Unicode Range: {unicode_range_4:08X}:{unicode_range_3:08X}:'
                             f'{unicode_range_2:08X}:{unicode_range_1:08X}'
                             ' (bit0 last)')
    print(f'    Vendor ID: {vend_id}')
    print(f'    Selection: {selection} [{selection_breakout}]')
    print(f'    Character Index Range: {first_char_index} to {last_char_index}')

    if len(data) >= 78:
        (typo_ascender, typo_descender, typo_line_gap,
            win_ascent, win_descent) = unpack('>3h2H', data[68:78])
        print(f'    Typographic Ascender: {typo_ascender}')
        print(f'    Typographic Descender: {typo_descender}')
        print(f'    Typographic Line Gap: {typo_line_gap}')
        print(f'    Windows Ascender: {win_ascent}')
        print(f'    Windows Descender: {win_descent}')

    if version >= 1 and len(data) >= 86:
        (code_page_range_1, code_page_range_2) = unpack('>2I', data[78:86])
        print(f'    Code Page Character Range: {code_page_range_2:08X}:'
                                             f'{code_page_range_1:08X}'
                                             ' (bit0 last)')

    if version >= 2 and len(data) >= 96:
        (x_height, cap_height, default_char, break_char,
            max_context) = unpack('>2h3H', data[86:96])
        if default_char == 0:
            default_char = 'glyph 0'
        else:
            default_char = f'U+{default_char:04X}'

        print(f'    \'x\' Height: {x_height}')
        print(f'    Capital Height: {cap_height}')
        print(f'    Default Character: {default_char}')
        print(f'    Break Character: U+{break_char:04X}')
        print(f'    Maximum Context: {max_context}')

    if version >= 5 and len(data) >= 100:
        (lower_optical_point_size,
            upper_optical_point_size) = unpack('>2H', data[96:100])
        print(f'    Lower Optical Point Size: {lower_optical_point_size} TWIPs')
        print(f'    Upper Optical Point Size: {upper_optical_point_size} TWIPs')

@handles(b'prep')
def _prep_handler(tag, data):
    '''Handler for PreProgram Table, containing the control value program

    https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6prep.html

    '''
    print('PreProgram Table [prep]:')

    bytestring = ' '.join([bytes([b]).hex() for b in data])
    if len(bytestring) > 70 and not verbose:
        bytestring = bytestring[:66] + '...'

    print(f'    Length: {len(data)}')
    print(f'    Data: {bytestring}')

#
# Additional tables defined in TrueType reference manual
#

@handles(b'acnt')
def _acnt_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'ankr')
def _ankr_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'bdat')
def _bdat_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'bhed')
def _bhed_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'bloc')
def _bloc_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'bsln')
def _bsln_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'cvar')
def _cvar_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'EBSC')
def _EBSC_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'fdsc')
def _fdsc_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'feat')
def _feat_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'fmtx')
def _fmtx_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'fond')
def _fond_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'fvar')
def _fvar_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'gasp')
def _gasp_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'gcid')
def _gcid_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'gvar')
def _gvar_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'just')
def _just_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'kerx')
def _kerx_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'lcar')
def _lcar_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'ltag')
def _ltag_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'meta')
def _meta_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'mort')
def _mort_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'morx')
def _morx_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'opbd')
def _opbd_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'prop')
def _prop_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'sbix')
def _sbix_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'trak')
def _trak_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'vhea')
def _vhea_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'vmtx')
def _vmtx_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'xref')
def _xref_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'Zapf')
def _Zapf_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

#
# Other tables seen in the wild
#

@handles(b'avar')
def _avar_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'BASE')
def _BASE_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'BDF ')
def _BDF__handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'CBDT')
def _CBDT_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'CBLC')
def _CBLC_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'COLR')
def _COLR_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'CPAL')
def _CPAL_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'DSIG')
def _DSIG_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'EBDT')
def _EBDT_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'EBLC')
def _EBLC_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'edt0')
def _edt0_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'Feat')
def _Feat_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'FFTM')
def _FFTM_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'GDEF')
def _GDEF_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'Glat')
def _Glat_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'Gloc')
def _Gloc_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'GPOS')
def _GPOS_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'GSUB')
def _GSUB_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'HVAR')
def _HVAR_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'JSTF')
def _JSTF_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'LINO')
def _LINO_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'LTSH')
def _LTSH_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'MATH')
def _MATH_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'MTfn')
def _MTfn_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'PCLT')
def _PCLT_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'PfEd')
def _PfEd_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'Silf')
def _Silf_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'Sill')
def _Sill_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'Silt')
def _Silt_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'TSIV')
def _TSIV_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'VDMX')
def _VDMX_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')

@handles(b'webf')
def _webf_handler(tag, data):
    print(f'{tag} table contains {len(data)} bytes')


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '-v':
        verbose = True
        sys.argv.pop(1)

    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} [-v] font.ttf')
        exit()

    with open(sys.argv[1], 'rb') as f:
        (scaler_type, num_tables, search_range, entry_selector,
                range_shift) = unpack('>IHHHH', f.read(12))
        tables = []
        for _ in range(num_tables):
            tables.append(unpack('>4sIII', f.read(16)))

        for tag, checksum, offset, length in tables:
            if tag in _handlers:
                f.seek(offset)
                data = f.read(length)
                _verify_checksum(data, checksum)
                _handlers[tag](data)
            else:
                print(f'Table {tag} has no handler. Ignoring.')
