FETCH_USER_INFO = """
    SELECT * FROM users WHERE user_id = :id
"""

FETCH_USER_FRIENDS = """
    WITH userFriends AS (
    SELECT DISTINCT U.user_id, U.first_name, U.last_name FROM Users U, Friends F WHERE (U.user_id = F.user_id OR U.user_id = F.friend_id) AND (F.user_id = :id or F.friend_id = :id)
), friendNames AS (
    SELECT U.first_name, U.last_name FROM userFriends U WHERE U.user_id != :id
) SELECT * FROM friendNames;
"""

FETCH_USER_POSTS = """
    SELECT * FROM posts WHERE user_id = :id
"""


FETCH_USER_LOCATIONS = """
    SELECT I.zipcode, L.country, L.state_name, L.city FROM located_in I, locations L WHERE user_id = :id AND I.zipcode = L.zipcode
"""

FETCH_USER_PROFILES = """
    SELECT * FROM profiles WHERE user_id = :id
"""

def fetch_user_info(id):
    query = FETCH_USER_INFO
    return query


def fetch_user_friends(id):
    query = FETCH_USER_FRIENDS
    return query


def fetch_user_posts(id):
    query = FETCH_USER_POSTS
    return query


def fetch_user_locations(id):
    query = FETCH_USER_LOCATIONS
    return query


def fetch_user_profiles(id):
    query = FETCH_USER_PROFILES
    return query
