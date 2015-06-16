#!/usr/bin/env python

import sqlite3
import traceback
import os
import Jmatch


def connect(row=False):
	"""Get connection and cursor at the same time"""
	try:
		conn = sqlite3.connect(Jmatch.app.config["DB"])
		if row:
			conn.row_factory = sqlite3.Row
		cursor = conn.cursor()
		return conn, cursor
	except Exception as e:
		traceback.print_exc()
		raise


def rebuild():
	conn, cur = connect()
	rebuildSql = open(Jmatch.app.config["SQL"], 'r')
	cur.executescript(rebuildSql.read())
	conn.commit()
	conn.close()
	rebuildSql.close()


def insert(table, columns, values):
	try:
		conn, cur = connect(row=True)
		sql = "insert into %s (%s) values (%s)" % (table, ", ".join(columns), ", ".join(["'"+v.__str__()+"'" for v in values]))
		cur.execute(sql)
		cur.execute("select * from %s where rowid=last_insert_rowid()" % table)
		return cur.fetchone()
	finally:
		conn.commit()
		conn.close()


def select(table, columns, values):
	try:
		conn, cur = connect(row=True)
		sql = "select * from %s where %s" % (table, "and".join([columns[i]+"='"+str(values[i])+"'" for i in range(len(columns))]))
		cur.execute(sql)
		return cur.fetchall()
	finally:
		conn.close()


def selectAll(table):
	try:
		conn, cur = connect(row=True)
		cur.execute("select * from "+table)
		return cur.fetchall()
	finally:
		conn.close()


def verifyUser(username='', password='', accesstoken=''):
	try:
		conn, cur = connect()
		if accesstoken != '':
			cur.execute("select id from users where accesstoken=?", (accesstoken,))
			return cur.fetchone()[0]
		else:	
			cur.execute("select accesstoken from users where username=? and password=?", (username, password))
			return cur.fetchone()[0]
	except:
		traceback.print_exc()
		return None
	finally:
		conn.close()


def history(uid):
	try:
		conn, cur = connect(row=True)
		cur.execute("""
			select * 
			from (
				select matches.id as mid, games.name as game, matches.createdTime, 'win' as result
				from matches, games
				where exists (
					select * 
					from winners 
					where winners.mid = matches.id and
					winners.uid = ?
				)
				union
				select matches.id as mid, games.name as game, matches.createdTime, 'lose' as result
				from matches, games
				where exists (
					select * 
					from losers 
					where losers.mid = matches.id and
					losers.uid = ?
				)
			) as A
			order by A.createdTime desc
		""", (uid, uid,))
		return cur.fetchall()
	finally:
		conn.close()


def available_opponet(uid):
	try:
		conn, cur = connect(row=True)
		cur.execute("""
			select lobby.uid uid, A.wins wins
			from (
				select ranks.id uid, games.id gid, ranks.wins wins
				from ranks join games
				on ranks.game = games.name
			) A, lobby
			where A.gid = lobby.gid and A.uid = lobby.uid
		""")
		return cur.fetchall()
	finally:
		conn.close()


def check(table, columns, values):
	try:
		conn, cur = connect(row=True)
		sql = "select * from %s where %s" % (table, "and".join([columns[i]+"='"+str(values[i])+"'" for i in range(len(columns))]))
		cur.execute(sql)
		return cur.fetchone()!=None
	finally:
		conn.close()


def delete(table, columns, values):
	try:
		conn, cur = connect(row=True)
		sql = "select * from %s where %s" % (table, "and".join([columns[i]+"='"+str(values[i])+"'" for i in range(len(columns))]))
		cur.execute(sql)
		old = cur.fetchall()
		sql = "delete from %s where %s" % (table, "and".join([columns[i]+"='"+str(values[i])+"'" for i in range(len(columns))]))
		cur.execute(sql)
		return old
	finally:
		conn.commit()
		conn.close()
