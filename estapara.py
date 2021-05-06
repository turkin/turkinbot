import discord
import os
import sqlite3
from sqlite3 import Error
import random
import unidecode

def sql_connection():
	try:
		con = sqlite3.connect('turkinbot.db')
		return con
	except Error:
		print(Error)

def sql_fetch(con, sql):
	cursorObj = con.cursor()
	cursorObj.execute(sql)
	rows = cursorObj.fetchall()
	return rows

def sql_row_count(con, sql):
	cursorObj = con.cursor()
	cursorObj.execute(sql)
	row_count = cursorObj.fetchone()
	return row_count

client = discord.Client()

con = sql_connection()

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))
	sql = "SELECT phrase FROM esta_para"
	rows=sql_fetch(con,sql)
	channel = client.get_channel(839236929806401540)
	await channel.send("Está para " + str(random.choice(rows)[0]))
	exit();

client.run('')

