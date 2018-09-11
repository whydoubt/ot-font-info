#!/usr/bin/env python3

import sys
from struct import unpack


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
    pass

@handles(b'glyf')
def _glyf_handler(tag, data):
    pass

@handles(b'head')
def _head_handler(tag, data):
    pass

@handles(b'hhea')
def _hhea_handler(tag, data):
    pass

@handles(b'hmtx')
def _hmtx_handler(tag, data):
    pass

@handles(b'loca')
def _loca_handler(tag, data):
    pass

@handles(b'maxp')
def _maxp_handler(tag, data):
    pass

@handles(b'name')
def _name_handler(tag, data):
    pass

@handles(b'post')
def _post_handler(tag, data):
    pass

#
# Optional tables for TrueType fonts
#

@handles(b'cvt ')
def _cvt__handler(tag, data):
    pass

@handles(b'fpgm')
def _fpgm_handler(tag, data):
    pass

@handles(b'hdmx')
def _hdmx_handler(tag, data):
    pass

@handles(b'kern')
def _kern_handler(tag, data):
    pass

@handles(b'OS/2')
def _OS_2_handler(tag, data):
    pass

@handles(b'prep')
def _prep_handler(tag, data):
    pass

#
# Additional tables defined in TrueType reference manual
#

@handles(b'acnt')
def _acnt_handler(tag, data):
    pass

@handles(b'ankr')
def _ankr_handler(tag, data):
    pass

@handles(b'bdat')
def _bdat_handler(tag, data):
    pass

@handles(b'bhed')
def _bhed_handler(tag, data):
    pass

@handles(b'bloc')
def _bloc_handler(tag, data):
    pass

@handles(b'bsln')
def _bsln_handler(tag, data):
    pass

@handles(b'cvar')
def _cvar_handler(tag, data):
    pass

@handles(b'EBSC')
def _EBSC_handler(tag, data):
    pass

@handles(b'fdsc')
def _fdsc_handler(tag, data):
    pass

@handles(b'feat')
def _feat_handler(tag, data):
    pass

@handles(b'fmtx')
def _fmtx_handler(tag, data):
    pass

@handles(b'fond')
def _fond_handler(tag, data):
    pass

@handles(b'fvar')
def _fvar_handler(tag, data):
    pass

@handles(b'gasp')
def _gasp_handler(tag, data):
    pass

@handles(b'gcid')
def _gcid_handler(tag, data):
    pass

@handles(b'gvar')
def _gvar_handler(tag, data):
    pass

@handles(b'just')
def _just_handler(tag, data):
    pass

@handles(b'kerx')
def _kerx_handler(tag, data):
    pass

@handles(b'lcar')
def _lcar_handler(tag, data):
    pass

@handles(b'ltag')
def _ltag_handler(tag, data):
    pass

@handles(b'meta')
def _meta_handler(tag, data):
    pass

@handles(b'mort')
def _mort_handler(tag, data):
    pass

@handles(b'morx')
def _morx_handler(tag, data):
    pass

@handles(b'opbd')
def _opbd_handler(tag, data):
    pass

@handles(b'prop')
def _prop_handler(tag, data):
    pass

@handles(b'sbix')
def _sbix_handler(tag, data):
    pass

@handles(b'trak')
def _trak_handler(tag, data):
    pass

@handles(b'vhea')
def _vhea_handler(tag, data):
    pass

@handles(b'vmtx')
def _vmtx_handler(tag, data):
    pass

@handles(b'xref')
def _xref_handler(tag, data):
    pass

@handles(b'Zapf')
def _Zapf_handler(tag, data):
    pass

#
# Other tables seen in the wild
#

@handles(b'avar')
def _avar_handler(tag, data):
    pass

@handles(b'BASE')
def _BASE_handler(tag, data):
    pass

@handles(b'BDF ')
def _BDF__handler(tag, data):
    pass

@handles(b'CBDT')
def _CBDT_handler(tag, data):
    pass

@handles(b'CBLC')
def _CBLC_handler(tag, data):
    pass

@handles(b'COLR')
def _COLR_handler(tag, data):
    pass

@handles(b'CPAL')
def _CPAL_handler(tag, data):
    pass

@handles(b'DSIG')
def _DSIG_handler(tag, data):
    pass

@handles(b'EBDT')
def _EBDT_handler(tag, data):
    pass

@handles(b'EBLC')
def _EBLC_handler(tag, data):
    pass

@handles(b'edt0')
def _edt0_handler(tag, data):
    pass

@handles(b'Feat')
def _Feat_handler(tag, data):
    pass

@handles(b'FFTM')
def _FFTM_handler(tag, data):
    pass

@handles(b'GDEF')
def _GDEF_handler(tag, data):
    pass

@handles(b'Glat')
def _Glat_handler(tag, data):
    pass

@handles(b'Gloc')
def _Gloc_handler(tag, data):
    pass

@handles(b'GPOS')
def _GPOS_handler(tag, data):
    pass

@handles(b'GSUB')
def _GSUB_handler(tag, data):
    pass

@handles(b'HVAR')
def _HVAR_handler(tag, data):
    pass

@handles(b'JSTF')
def _JSTF_handler(tag, data):
    pass

@handles(b'LINO')
def _LINO_handler(tag, data):
    pass

@handles(b'LTSH')
def _LTSH_handler(tag, data):
    pass

@handles(b'MATH')
def _MATH_handler(tag, data):
    pass

@handles(b'MTfn')
def _MTfn_handler(tag, data):
    pass

@handles(b'PCLT')
def _PCLT_handler(tag, data):
    pass

@handles(b'PfEd')
def _PfEd_handler(tag, data):
    pass

@handles(b'Silf')
def _Silf_handler(tag, data):
    pass

@handles(b'Sill')
def _Sill_handler(tag, data):
    pass

@handles(b'Silt')
def _Silt_handler(tag, data):
    pass

@handles(b'TSIV')
def _TSIV_handler(tag, data):
    pass

@handles(b'VDMX')
def _VDMX_handler(tag, data):
    pass

@handles(b'webf')
def _webf_handler(tag, data):
    pass


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
