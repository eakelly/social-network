FETCH_USER_INFO = """
    SELECT * FROM users WHERE user_id = {user_id}
"""

FETCH_USER_FRIENDS = """
    WITH userFriends AS (
    SELECT DISTINCT U.user_id, U.first_name, U.last_name FROM Users U, Friends F WHERE (U.user_id = F.user_id OR U.user_id = F.friend_id) AND (F.user_id = {user_id} or F.friend_id = {user_id})
), friendNames AS (
    SELECT U.first_name, U.last_name FROM userFriends U WHERE U.user_id != {user_id}
) SELECT * FROM friendNames;
"""

FETCH_USER_POSTS = """
    SELECT * FROM user_posts WHERE user_id = {user_id}
"""

def fetch_user_info():
    query = FETCH_USER_INFO
    return query


def fetch_user_friends():
    query = FETCH_USER_FRIENDS
    return query


def fetch_user_posts():
    query = FETCH_USER_POSTS
    return query