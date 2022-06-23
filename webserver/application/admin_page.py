FETCH_LOCATIONS = """
    SELECT * FROM locations 
"""

GET_AVERAGE_AGE_OF_FRIENDS = """
WITH userFriendsA AS (
    SELECT U.user_id, F.friend_id FROM friends F, users U WHERE U.user_id = F.user_id
), userFriendsAAges AS (
    SELECT A.user_id, AVG(U.age) AS avg_age FROM userFriendsA A, Users U WHERE U.user_id = A.friend_id GROUP BY A.user_id
), userFriendsB AS (
    SELECT U.user_id, F.user_id AS friend_id FROM friends F, users U WHERE U.user_id = F.friend_id
), userFriendsBAges AS (
    SELECT B.user_id, AVG(U.age) AS avg_age FROM userFriendsB B, Users U WHERE U.user_id = B.friend_id GROUP BY B.user_id
), combinedFriendAgeAverages AS (
    SELECT * FROM userFriendsAAges A UNION SELECT * FROM userFriendsBAges B
) SELECT C.user_id, AVG(C.avg_age) AS avg_age_of_friends  FROM combinedFriendAgeAverages C GROUP BY C.user_id
"""

GET_POST_AVG_FOR_AGE_30 = """
With users30UnderPosts AS (
    SELECT COUNT(*) AS post_count, U.user_id AS user_id FROM Users U, Posts P WHERE U.user_id = P.user_id AND U.age <= 30 GROUP BY U.user_id
),usersOver30Posts AS (
    SELECT COUNT(*) AS post_count, U.user_id AS user_id FROM Users U, Posts P WHERE U.user_id = P.user_id AND U.age > 30 GROUP BY U.user_id
), averagePostsForAgeGroups AS (
    SELECT (SELECT AVG(post_count) FROM users30UnderPosts) AS leq_30_post_avg, (SELECT AVG(post_count) FROM usersOver30Posts) AS over_30_post_avg
) SELECT * FROM averagePostsForAgeGroups
"""


def fetch_locations():
    query = FETCH_LOCATIONS
    return query


def get_avg_age_of_friends():
    query = GET_AVERAGE_AGE_OF_FRIENDS
    return query


def get_post_stats():
    query = GET_POST_AVG_FOR_AGE_30
    return query