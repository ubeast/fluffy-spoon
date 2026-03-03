import pytest
from your_module import get_delimiters  # Replace with your actual module name

# ------------- Sample EDI content helpers

def build_isa(element_sep='*', segment_term='~', repetition_sep='^', compound_sep=':', version='00501'):
    """Build a minimal valid ISA + GS segment string for testing."""
    isa = (
        f"ISA{element_sep}"
        f"00{element_sep}"
        f"          {element_sep}"
        f"00{element_sep}"
        f"          {element_sep}"
        f"ZZ{element_sep}"
        f"SENDER         {element_sep}"
        f"ZZ{element_sep}"
        f"RECEIVER       {element_sep}"
        f"230101{element_sep}"
        f"1200{element_sep}"
        f"{repetition_sep}{element_sep}"
        f"00501{element_sep}"
        f"000000001{element_sep}"
        f"0{element_sep}"
        f"P{element_sep}"
        f"{compound_sep}{segment_term}"
    )
    gs = (
        f"GS{element_sep}"
        f"PO{element_sep}"
        f"SENDER{element_sep}"
        f"RECEIVER{element_sep}"
        f"20230101{element_sep}"
        f"1200{element_sep}"
        f"1{element_sep}"
        f"X{element_sep}"
        f"{version}{segment_term}"
    )
    return isa + '\n' + gs


# ------------- Tests

class TestGetDelimiters:

    def test_standard_delimiters(self):
        edi = build_isa(element_sep='*', segment_term='~', repetition_sep='^', compound_sep=':', version='00501')
        result = get_delimiters(edi)
        assert result['element'] == '*'
        assert result['segment'] == '~'
        assert result['compound'] == ':'
        assert result['repetition'] == '^'

    def test_repetition_separator_none_for_4010(self):
        edi = build_isa(version='004010X222A1')
        result = get_delimiters(edi)
        assert result['repetition'] is None

    def test_repetition_separator_present_for_5010(self):
        edi = build_isa(version='005010X222A1', repetition_sep='^')
        result = get_delimiters(edi)
        assert result['repetition'] == '^'

    def test_leading_characters_before_isa(self):
        edi = build_isa()
        result = get_delimiters('JUNK_DATA\n' + edi)
        assert result['element'] == '*'
        assert result['segment'] == '~'

    def test_missing_isa_raises_value_error(self):
        with pytest.raises(ValueError, match="Could not find 'ISA' segment"):
            get_delimiters("THIS IS NOT EDI CONTENT")

    def test_invalid_version_raises_value_error(self):
        # Manually corrupt the GS08 field
        edi = build_isa(version='BADVERSION')
        # Strip all digits from version to trigger the error
        edi = edi.replace('BADVERSION', 'NODIGITS')
        with pytest.raises(ValueError, match="Could not parse X12 release"):
            get_delimiters(edi)

    def test_custom_element_separator(self):
        edi = build_isa(element_sep='|', segment_term='~')
        result = get_delimiters(edi)
        assert result['element'] == '|'

    def test_returns_all_keys(self):
        edi = build_isa()
        result = get_delimiters(edi)
        assert set(result.keys()) == {'element', 'segment', 'compound', 'repetition'}
