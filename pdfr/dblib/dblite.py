#!/usr/bin/env python
""" DB adapter for using sqlite3. The goal is to abstract all of the
    db work to this file and use a class that the application doesn't """
    
import sqlite3
from contextlib import closing
import time


class Adapter():
    def __init__(self, app):
        self.app = app
        self.dbname = app.config['DATABASE']
        self.errors = []
        self.db = None

    def connect(self):
        self.db = sqlite3.connect(self.dbname)

    def init_db(self):
        self.connect()
        with closing( self.db ) as db:
            with self.app.open_resource('schema.sql') as f:
                db.cursor().executescript(f.read())
        #self.commit()

    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()

    def getEntries(self, limit=11, offset=0):
        curse = self.db.execute('select id,title,user,link,timestamp from documents order by id desc limit ? offset ?', (limit, offset))
        return [dict(id=row[0], title=row[1], user=row[2], link=row[3], posted=row[4]) for row in curse.fetchall()]

    def newEntry(self, form):
        self.db.execute(
            'insert into documents (title,user,source,published,link,comment,timestamp) values (?, ?, ?, ?, ?, ?, ?)',
            [
                form['title'], form['user'], form['source'], form['published'], form['link'], form['comment'],
                time.strftime("%a, %d %b %Y %H:%M:%S %Z")
            ]
        )
        self.commit()

    def getEntry(self, entry_no):
        curse = self.db.execute(
            'select title,user,link,source,published,comment,timestamp from documents where id=?',
            (str(entry_no), )
        )
        row = curse.fetchone()
        return dict(
            title=row[0], user=row[1], link=row[2], source=row[3],
            published=row[4], comment=row[5], id=entry_no, posted=row[6]
        )

    def updateEntry(self,entry_no, form):
        self.db.execute('UPDATE documents SET title=?,user=?,source=?,published=?,link=?,comment=? WHERE id=?',[
            form['title'], form['user'], form['source'], form['published'], form['link'], form['comment'], entry_no
            ]
        )
        self.commit()

    def deleteEntry(self, entry_no):
        self.db.execute('delete from documents where id=?', (str(entry_no), ))
        self.commit()



