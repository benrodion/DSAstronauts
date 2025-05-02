from app.helpers import check_bad_password

def test_check_bad_password():
    
    assert check_bad_password("abc 123") == "Password cannot contain spaces."
    assert check_bad_password("    ") == "Password cannot contain spaces."
    assert check_bad_password("") == "Password must be at least 4 characters."
    assert check_bad_password("abc") == "Password must be at least 4 characters."
    assert check_bad_password("abcd") == None
