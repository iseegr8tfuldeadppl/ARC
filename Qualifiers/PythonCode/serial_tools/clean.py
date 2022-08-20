def Clean(b):
    if b!=None:
        #string_n = b.decode('utf-8', errors='replace')  # decode byte string into Unicode
        try:
            return b.decode().rstrip()  # decode byte string into Unicode
        except UnicodeDecodeError:
            return "UnicodeDecodeError error man"
