def friends(conn, origin_uid):
    qry = "SELECT f.friend_uid, u.uname FROM friends f, users u " \
          "WHERE f.origin_uid = %s AND f.friend_uid = u.uid;"
    args = origin_uid
    cursor = conn.execute(qry, args)
    return cursor


def not_friends(conn, origin_uid):
    qry = "SELECT u.uid, u.uname FROM users u " \
          "WHERE u.uid NOT IN " \
          "(SELECT f.friend_uid FROM friends f " \
          "WHERE f.origin_uid = %s " \
          "UNION SELECT %s);"
    args = origin_uid, origin_uid
    return conn.execute(qry, args)


def add_friend(conn, origin_uid, friend_uid):
    qry = "INSERT INTO friends (origin_uid, friend_uid) " \
          "VALUES (%s, %s)"
    args = origin_uid, friend_uid
    return conn.execute(qry, args)


def uname(conn, uid):
    qry = "SELECT uname FROM users WHERE uid = %s;"
    args = uid
    return conn.execute(qry, args)
