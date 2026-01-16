def from_list_remove_duplicates_preserve_order(raw_list: list) -> list:
    
    collection_bin: set = set()
    no_dupes = []
    
    for element in raw_list:
        if element not in collection_bin:
            collection_bin.add(element)
            no_dupes.append(element)
    return no_dupes
