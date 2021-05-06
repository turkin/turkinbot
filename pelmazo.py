import discord
import os
import sqlite3
from sqlite3 import Error
import random
from random import choice
import unidecode
from discord.ext import commands

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

intents = discord.Intents.all()
client = discord.Client(intents=intents)

con = sql_connection()

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))	


	guild = client.get_guild(839236929806401537)
	memberList = guild.members
	channel = client.get_channel(839236929806401540)
	await channel.send("El palomo del dia es: " + str(random.choice(memberList).name))

	exit();

client.run('')