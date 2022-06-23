FETCH_USER_INFO = """
    SELECT * FROM users WHERE user_id = {user_id}
"""

FETCH_PROFILE_INFO = """
    SELECT * FROM profiles WHERE user_id = {user_id} AND profile_id = {profile_id}
"""

FETCH_PROFILE_POSTS = """
    SELECT * FROM posts WHERE user_id = {user_id} AND profile_id = {profile_id}
"""

def fetch_user_info(userid):
    query = FETCH_USER_INFO
    query = query.format(user_id = userid)
    return query


def fetch_profile(userid, profileid):
    query = FETCH_PROFILE_INFO
    query = query.format(user_id = userid, profile_id = profileid)
    return query


def fetch_profile_posts(userid, profileid):
    query = FETCH_PROFILE_POSTS
    query = query.format(user_id = userid, profile_id = profileid)
    return query
