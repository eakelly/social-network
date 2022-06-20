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
    SELECT * FROM posts WHERE user_id = {user_id}
"""

def fetch_user_info(id):
    query = FETCH_USER_INFO
    query = query.format(user_id = id)
    return query


def fetch_user_friends(id):
    query = FETCH_USER_FRIENDS
    query = query.format(user_id = id)
    return query


def fetch_user_posts(id):
    query = FETCH_USER_POSTS
    query = query.format(user_id = id)
    return query
