from typing import Dict, Optional
import re

def get_delimiters(edi_dirty_contents: str) -> Dict[str, Optional[str]]:
    # ------------- Get start of ISA (in case there are leading characters before "ISA")
    try:
        isa_start_index = edi_dirty_contents.index('ISA')
        edi_clean_contents = edi_dirty_contents[isa_start_index:]
    except ValueError:
        raise ValueError("Fatal: Could not find 'ISA' segment in the provided EDI content.")

    # ------------- Get Element Separator
    # Element Separator is at position 3 (0-based index)
    element_separator = edi_clean_contents[3]

    # ------------- Get Segment Terminator
    gs_pattern = f'GS{element_separator}'
    gs_index = edi_clean_contents.index(gs_pattern)
    segment_terminator = (edi_clean_contents[105]
                          if gs_index == 106
                          else edi_clean_contents.split(element_separator, 17)[16][1])

    # ------------- Get clean ISA and GS elements
    isa_line, gs_line = [_.strip() for _ in edi_clean_contents.split(segment_terminator, 2)[:2]]
    isa_elements = isa_line.split(element_separator)
    gs_elements = gs_line.split(element_separator)

    # ------------- Get Compound Separator
    compound_separator = isa_elements[16]

    # ------------- Get X12 Release
    version_string = gs_elements[8]  # e.g. "004010X222A1" or "00401"
    version_digits = re.search(r'\d+', version_string)
    if not version_digits:
        raise ValueError(f"Fatal: Could not parse X12 release from GS08 value: '{version_string}'")
    x12_release = int(version_digits.group())

    # ------------- Get Repetition Separator
    repetition_separator = isa_elements[11] if x12_release > 4010 else None

    # ------------- Build delimiter dictionary
    delimiters = {
        'element': element_separator,
        'segment': segment_terminator,
        'compound': compound_separator,
        'repetition': repetition_separator,
    }

    return delimiters
