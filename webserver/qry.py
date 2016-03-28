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


def search_songs(conn, song):
    qry = "SELECT s.sid, s.sname, s.link, aa.albumname, a.aname " \
          "FROM songs s, contain c, albums aa, publish p, artists a " \
          "WHERE s.sid = c.sid AND c.albumid = aa.albumid " \
          "      AND aa.albumid = p.albumid AND p.aid = a.aid " \
          "      AND s.sname ILIKE %s"
    args = "%" + song + "%"
    return conn.execute(qry, args)

def playlist_songs(conn, pid, cid):
    qry = "SELECT s.sid, s.sname, s.link, aa.albumname, a.aname " \
          "FROM songs s, contain c, albums aa, added aaa, publish p, artists a, " \
          "     playlists pl " \
          "WHERE s.sid = c.sid AND c.albumid = aa.albumid " \
          "      AND aa.albumid = p.albumid AND p.aid = a.aid " \
          "      AND aaa.sid = s.sid AND aaa.pid = pl.pid " \
          "      AND pl.pid = %s AND pl.creater_uid = %s"
    args = pid, cid
    return conn.execute(qry, args)

def playlist_name(conn, pid, cid):
    qry = "SELECT pname FROM playlists WHERE pid = %s AND creater_uid = %s;"
    args = pid, cid
    return conn.execute(qry, args)


def add_playlist(conn, uid, creater_uid, pid):
    qry = "INSERT INTO subscribe (creater_uid, subscriber_uid, pid) VALUES (%s, %s, %s);"
    args = int(creater_uid), int(uid), int(pid)
    return conn.execute(qry, args)


def playlist_subscribed(conn, uid):
    qry = "SELECT p.pname, p.pid, p.creater_uid FROM subscribe s, playlists p WHERE s.pid = p.pid AND s.subscriber_uid = %s;"
    args = uid
    return conn.execute(qry, args)


def playlist_not_subscribed(conn, uid):
    qry = "SELECT p.pname, p.pid, p.creater_uid FROM playlists p " \
          "WHERE p.pid NOT IN " \
          "(SELECT s.pid FROM subscribe s " \
          "WHERE s.subscriber_uid = %s);"
    args = uid
    return conn.execute(qry, args)


def remove_playlist(conn, uid, pid, cid):
    qry = "DELETE FROM subscribe " \
          "WHERE subscriber_uid = %s AND pid = %s AND creater_uid = %s;"
    args = uid, pid, cid
    return conn.execute(qry, args)


def playlist_created(conn, uid):
    qry = "SELECT pname, pid, creater_uid FROM playlists WHERE creater_uid = %s;"
    args = uid
    return conn.execute(qry, args)

def createpl(conn, uid, plname):
    qry = "INSERT INTO playlists(pid, creater_uid, pname) VALUES ((SELECT max(pid)+1 FROM playlists), %s, %s);"
    args = uid, plname
    return conn.execute(qry, args)

def pidpl(conn):
    qry = "SELECT * FROM playlists WHERE pid = (SELECT max(pid) FROM playlists);"
    return conn.execute(qry)

def delete_playlist(conn, pid, cid):
    qry = "DELETE FROM subscribe " \
          "WHERE pid = %s AND creater_uid = %s; " \
          "DELETE FROM added " \
          "WHERE pid = %s AND uid = %s; " \
          "DELETE FROM Playlists " \
          "WHERE pid = %s AND creater_uid = %s;"
    args = pid, cid, pid, cid, pid, cid
    return conn.execute(qry, args)

def songsinpl(conn, pid):
    qry = "SELECT * FROM added WHERE pid = %s;"
    args = pid
    return conn.execute(qry, args)
    
def addtopl(conn, sid, pid):
  qry = "INSERT INTO added(pid, uid, sid) VALUES (%s, (SELECT creater_uid FROM playlists WHERE pid = %s), %s);"
  args = pid, pid, sid
  return conn.execute(qry, args)

def liked_songs(conn, uid):
    qry = "SELECT * " \
          "FROM likes l, songs s, contain c, albums alb, publish p, " \
          "     artists a " \
          "WHERE l.sid = s.sid AND s.sid = c.sid AND c.albumid = alb.albumid " \
          "      AND p.albumid = alb.albumid AND p.aid = a.aid " \
          "      AND l.uid = %s;"
    args = uid
    return conn.execute(qry, args)


def unlike(conn, uid, sid):
    qry = "DELETE FROM likes " \
          "WHERE uid = %s AND sid = %s;"
    args = uid, sid
    return conn.execute(qry, args)


def like(conn, uid, sid):
    qry = "INSERT INTO likes (uid, sid) " \
          "VALUES (%s, %s);"
    args = uid, sid
    return conn.execute(qry, args)


def remove_playlist_song(conn, cid, pid, sid):
    qry = "DELETE FROM added " \
          "WHERE uid = %s AND pid = %s AND sid = %s"
    args = cid, pid, sid
    return conn.execute(qry, args)


def max_uid(conn):
    qry = "SELECT max(uid) AS max_uid FROM users;"
    return conn.execute(qry)


def new_user(conn, uname):
    cursor = max_uid(conn)
    uid = cursor.first()['max_uid'] + 1
    cursor.close()
    qry = "INSERT INTO users (uid, uname) " \
          "VALUES (%s, %s);"
    args = uid, uname
    return conn.execute(qry, args), uid


def delete_user(conn, uid):
    qry = "DELETE FROM friends WHERE friend_uid = %s OR friends.origin_uid = %s; " \
          "DELETE FROM follow WHERE uid = %s; " \
          "DELETE FROM likes WHERE uid = %s; " \
          "DELETE FROM subscribe WHERE subscriber_uid = %s; " \
          "DELETE FROM added WHERE uid = %s; " \
          "DELETE FROM subscribe WHERE creater_uid = %s; " \
          "DELETE FROM users WHERE uid = %s;"
    args = uid, uid, uid, uid, uid, uid, uid, uid
    return conn.execute(qry, args)
