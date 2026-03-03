from typing import Dict, Optional

def get_delimiters(edi_dirty_contents: str) -> Dict[str, Optional[str]]:
    # ------------- Get start of ISA (In case there are leading characters)
    try:
        isa_start_index = edi_dirty_contents.index('ISA')
        edi_clean_contents = edi_dirty_contents[isa_start_index:]
    except ValueError:
        raise ValueError("Fatal: Could not find 'ISA' segment in the provided EDI content.")

    # ------------- Get Element Separator 
    element_separator = edi_clean_contents[3]

    # ------------- Get Segment Terminator
    gs_search_str = f'GS{element_separator}'
    try:
        gs_location = edi_clean_contents.index(gs_search_str)
    except ValueError:
        raise ValueError("Fatal: Could not find 'GS' segment to determine delimiters.")

    segment_terminator = (
        edi_clean_contents[105] 
        if gs_location == 106 
        else edi_clean_contents.split(element_separator, 17)[16][1]
    )

    # ------------- Get clean ISA and GS elements
    # Using the split limit to avoid processing the whole file
    isa_line, gs_line = [_.strip() for _ in edi_clean_contents.split(segment_terminator, 2)[:2]]
    isa_elements = isa_line.split(element_separator)
    gs_elements = gs_line.split(element_separator)

    # ------------- Get Compound Separator (ISA16)
    compound_separator = isa_elements[16]
    
    # ------------- Get X12 Release (GS08)
    try:
        x12_release = int(gs_elements[8])
    except (IndexError, ValueError):
        x12_release = 0

    # ------------- Get Repetition Separator (ISA11)
    repetition_separator = isa_elements[11] if x12_release > 4010 else None

    # ------------- Create the delimiter dictionary
    delimiters = {
        'element': element_separator,
        'segment': segment_terminator,
        'compound': compound_separator,
        'repetition': repetition_separator
    }

    # ------------- Validation: Ensure delimiters are unique
    # We filter out None (for older X12 versions) before checking uniqueness
    active_delims = [v for v in delimiters.values() if v is not None]
    if len(active_delims) != len(set(active_delims)):
        raise ValueError(f"Fatal: Non-unique delimiters detected: {delimiters}")
    
    return delimiters
