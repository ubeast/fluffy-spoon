from typing import Dict, Optional

def get_delimiters(edi_dirty_contents: str) -> Dict[str, Optional[str]]:

    try:
        isa_start_index = edi_dirty_contents.index('ISA')
        edi_clean_contents = edi_dirty_contents[isa_start_index:]
    except ValueError:
        raise ValueError("Fatal: Could not find 'ISA' segment in the provided EDI content.")

    # Element Separator is in position 4 (python is zero based so we use 3)
    element_separator = edi_clean_contents[3]


    gs_location = f'GS{element_separator}'
    gs_location = edi_clean_contents.index(gs_location)
    segment_terminator = (edi_clean_contents[105] 
                         if gs_location == 106
                         else edi_clean_contents.split(element_separator, 17)[16][1])

    isa_line, gs_line = [_.strip() for _ in edi_clean_contents.split(segment_terminator, 2)[:2]]
    isa_elements = isa_line.split(element_separator)
    gs_elements = gs_line.split(element_separator)

    compound_seperator = isa_elements[16]
    
    x12_release = int(gs_elements[8])


    repetition_seperator = isa_elements[11] if x12_release > 4010 else None

    delimiters = {'element': element_separator,
                  'segment': segment_terminator,
                  'compound': compound_seperator,
                  'repetition': repetition_seperator
    }
    
    return delimiters
