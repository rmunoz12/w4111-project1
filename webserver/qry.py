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
          "VALUES (%s, %s);"
    args = origin_uid, friend_uid
    return conn.execute(qry, args)


def delete_friend(conn, origin_uid, friend_uid):
    qry = "DELETE FROM friends " \
          "WHERE origin_uid = %s AND friend_uid = %s;"
    args = origin_uid, friend_uid
    return conn.execute(qry, args)


def artist_follows(conn, uid):
    qry = "SELECT a.aid, a.aname FROM artists a, follow f " \
          "WHERE f.uid = %s AND a.aid = f.aid;"
    args = uid
    return conn.execute(qry, args)


def not_followed(conn, uid):
    qry = "SELECT a.aid, a.aname FROM artists a " \
          "WHERE a.aid NOT IN " \
          "(SELECT f.aid FROM follow f " \
          "WHERE f.uid = %s);"
    args = uid
    return conn.execute(qry, args)


def add_artist(conn, uid, aid):
    qry = "INSERT INTO follow (uid, aid) " \
          "VALUES (%s, %s);"
    args = uid, aid
    return conn.execute(qry, args)


def delete_artist(conn, uid, aid):
    qry = "DELETE FROM follow " \
          "WHERE uid = %s AND aid = %s;"
    args = uid, aid
    return conn.execute(qry, args)


def uname(conn, uid):
    qry = "SELECT uname FROM users WHERE uid = %s;"
    args = uid
    return conn.execute(qry, args)


def aname(conn, aid):
    qry = "SELECT aname FROM artists WHERE aid = %s;"
    args = aid
    return conn.execute(qry, args)


def publish(conn, aid):
    qry = "SELECT a.albumid, a.albumname, p.since, a.artlink " \
          "FROM publish p, albums a " \
          "WHERE a.albumid = p.albumid AND p.aid = %s " \
          "ORDER BY since DESC;"
    args = aid
    return conn.execute(qry, args)


def list_album_songs(conn, albumid):
    qry = "SELECT * " \
          "FROM contain c, songs s " \
          "WHERE c.albumid = %s AND c.sid = s.sid;"
    args = albumid
    return conn.execute(qry, args)


def song_details(conn, sid):
    qry = "SELECT * " \
          "FROM songs s, genres g, contain c, albums alb, publish p, " \
          "     artists a " \
          "WHERE s.gid = g.gid AND s.sid = c.sid AND c.albumid = alb.albumid " \
          "      AND alb.albumid = p.albumid AND p.aid = a.aid " \
          "      AND s.sid = %s;"
    args = sid
    return conn.execute(qry, args)
