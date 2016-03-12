def friends(conn, origin_uid):
    qry = "SELECT f.friend_uid, u.uname FROM friends f, users u " \
          "WHERE f.origin_uid = %s AND f.friend_uid = u.uid;"
    args = origin_uid
    cursor = conn.execute(qry, args)
    return cursor

def uname(conn, uid):
    qry = "SELECT uname FROM users WHERE uid = %s"
    args = uid
    return conn.execute(qry, args)