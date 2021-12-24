e = '400: {"error":"partial write: field type conflict: input field \"dal_piek\" on measurement \"Slimme_meter\" is type float, already exists as type string dropped=43"}'

if "dropped" in str(e):
    parse_error = str(e)
    linedropped = int(parse_error[parse_error.index('=')+1:parse_error.index('}')-1])
    print(linedropped)