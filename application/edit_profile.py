EDIT_PROFILE_INFO = """
    UPDATE proile SET bio = :bio WHERE user_id = :userid AND profile_id = :profileid
"""

def edit_profile_info(userid, profileid, bio):
    query = EDIT_PROFILE_INFO
    return query
