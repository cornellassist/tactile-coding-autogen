def validate(text, translation, cpl, bh, ph, ms, es):
    errors = ""

    # get longest translated braille word
    strings = translation.split('⠀')
    max_length = len(max(strings, key=len))

    if text == "":
        errors += "\nText input can not be blank"
    
    try:
        cpl_int = int(cpl)
        if cpl_int < max_length:
            errors += "\nCharacters per line must be an integer greater than " + str(max_length)
    except ValueError:
        errors += "\nCharacters per line must be an integer greater than " + str(max_length)

    try:
        bh_float = float(bh)
        if bh_float <= 0.4-1e-9:
            errors += "\nBraille height must be a value greater than or equal to 0.4"
    except ValueError:
        errors += "\nBraille height must be a value greater than or equal to 0.4"

    try:
        ph_float = float(ph)
        if ph_float <= 0.1-1e-9:
            errors += "\nPlate height must be a value greater than or equal to 0.1"
    except ValueError:
        errors += "\nPlate height must be a value greater than or equal to 0.1"

    try:
        ms_float = float(ms)
        if ms_float <= 0.1-1e-9:
            errors += "\nMargin size must be a value greater than or equal to 0.1"
    except ValueError:
        errors += "\nMargin size must be a value greater than or equal to 0.1"

    try:
        es_float = float(es)
        if es_float <= 0.01-1e-9:
            errors += "\nExport scale must be a value greater than or equal to 0.01"
    except ValueError:
        errors += "\nExport scale must be a value greater than or equal to 0.01"

    if errors:
        error_list = errors[1:]
        return error_list
    else:
        return ""