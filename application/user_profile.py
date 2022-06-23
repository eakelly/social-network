FETCH_USER_INFO = """
    SELECT * FROM users WHERE user_id = :userid
"""

FETCH_PROFILE_INFO = """
    SELECT * FROM profiles WHERE user_id = :userid AND profile_id = :profileid
"""

FETCH_PROFILE_POSTS = """
    SELECT * FROM posts WHERE user_id = :userid AND profile_id = :profileid
"""

def fetch_user_info(userid):
    query = FETCH_USER_INFO
    return query


def fetch_profile(userid, profileid):
    query = FETCH_PROFILE_INFO
    return query


def fetch_profile_posts(userid, profileid):
    query = FETCH_PROFILE_POSTS
    return query
