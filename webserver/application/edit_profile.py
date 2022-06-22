EDIT_PROFILE_INFO = """
    UPDATE proile SET bio = {bio} WHERE user_id = {user_id} AND profile_id = {profile_id}
"""

def edit_profile_info(userid, profileid, bio):
    query = EDIT_PROFILE_INFO
    query = query.format(user_id = userid, profile_id=profileid, bio=bio)
    return query
