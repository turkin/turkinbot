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

def sql_table(con):
	cursorObj = con.cursor()
	cursorObj.execute("CREATE TABLE IF NOT EXISTS words (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, word TEXT, quantity INTEGER DEFAULT 1);")
	cursorObj.execute("CREATE TABLE IF NOT EXISTS prohibited_words (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, word TEXT);")
	cursorObj.execute("CREATE TABLE IF NOT EXISTS prohibited_words_user (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, word TEXT, user TEXT, quantity INTEGER DEFAULT 1);")
	cursorObj.execute("CREATE TABLE IF NOT EXISTS esta_para (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, phrase TEXT);")
	con.commit()

def sql_insert(con, sql, entities):
	cursorObj = con.cursor()
	cursorObj.execute(sql, entities)
	con.commit()

def sql_update(con, sql):
	cursorObj = con.cursor()
	cursorObj.execute(sql)
	con.commit()

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

def add_prohibited_word(con, prohibited_word):
	cursorObj = con.cursor()
	cursorObj.execute('SELECT word FROM prohibited_words WHERE word = (?)', (prohibited_word,))
	row=cursorObj.fetchone()
	if row is None:
		cursorObj.execute("INSERT INTO prohibited_words(word) VALUES (?)", (prohibited_word,))
		con.commit()
		return 1
	else:
		return 0

def del_prohibited_word(con, prohibited_word):
	cursorObj = con.cursor()
	cursorObj.execute('SELECT word FROM prohibited_words WHERE word = (?)', (prohibited_word,))
	row=cursorObj.fetchone()
	if row is not None:
		cursorObj.execute("DELETE FROM prohibited_words WHERE word = (?)", (prohibited_word,))
		con.commit()
		return 1
	else:
		return 0

def add_prohibited_word_user(con, prohibited_word, user):
	cursorObj = con.cursor()
	cursorObj.execute('''SELECT * FROM prohibited_words_user WHERE user=? AND word=?;''', (str(user), str(prohibited_word)))
	row=cursorObj.fetchone()
	if row is None:
		cursorObj.execute("INSERT INTO prohibited_words_user(word,user) VALUES (?,?)", (str(prohibited_word),str(user)))
		con.commit()
		return 1
	else:
		cursorObj.execute("UPDATE prohibited_words_user SET quantity = quantity + 1 WHERE (word=(?) AND user=(?))", (str(prohibited_word),str(user)))
		con.commit()
		return int(row[3])+1

client = discord.Client()

welcome_words = ["hola", "buen dia", "buen día", "buenos días", "buenos dias"]
welcome_replys = [
  "Buenas",
  "Hoy se muere alguien",
  "Buen dia",
  "Buenos Dias",
  "Se despertó el palomo",
  "Ya se sentía el olor a trolo",
  "Llegó el pelmazo"
]

famoso_replys = [
  "Saleeeeee",
  "De unaaaa",
  "Está para morder un limón",
  "Sin chuker por favor!",
  "Famoso doggy style",
  "Subiendo"
]

con = sql_connection()
sql_table(con)

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	message.content=unidecode.unidecode(message.content.lower())

	if message.content.startswith("/ayuda"):
		await message.channel.send("Comandos:\n/agregarprohibida\n/borrarprohibida\n/listarprohibidas\n/agregarestapara\n/borrarestapara\n/listarestapara")

	if any(word in message.content for word in welcome_words):
		await message.channel.send(random.choice(welcome_replys))

	if "famoso" in message.content:
		await message.channel.send(random.choice(famoso_replys))

	if "heroica" in message.content:
		await message.channel.send(random.choice(famoso_replys))
	
	sql = "SELECT word FROM prohibited_words"
	rows=sql_fetch(con,sql)
	for row in rows:
		if any(word in message.content for word in row):
			quant = add_prohibited_word_user(con, row[0], message.author)
			await message.channel.send("@" + str(message.author.name) +  " dijiste la palabra prohibida '" + str(row[0]) + "' " + str(quant) + " veces." )

	if message.content.startswith("/agregarprohibida"):
		prohibited_word = message.content.split("/agregarprohibida ",1)[1]
		if add_prohibited_word(con, prohibited_word) == 1:
			await message.channel.send("Se agregó la palabra " + prohibited_word +  " a la lista de palabras prohibidas.")
		else:
			await message.channel.send("La palabra " + prohibited_word +  " ya está en la lista de palabras prohibidas.")
	elif message.content.startswith("/borrarprohibida"):
		prohibited_word = message.content.split("/borrarprohibida ",1)[1]
		if del_prohibited_word(con, prohibited_word) == 1:
			await message.channel.send("Se borró la palabra " + prohibited_word +  " de la lista de palabras prohibidas.")
		else:
			await message.channel.send("La palabra " + prohibited_word +  " no estaba en la lista de palabras prohibidas.")
	elif message.content.startswith("/listarprohibidas"):
		sql = "SELECT word FROM words;"
		row = sql_fetch(con, sql)
		text="Palabras prohibidas:\n"
		for row in rows:
			text=text+str(row[0])+"\n"
		await message.channel.send(text)

	if message.content.startswith("/agregarestapara"):
		esta_para_word = message.content.split("/agregarestapara ",1)[1]
		sql='INSERT INTO esta_para(phrase) VALUES (?)'
		entities=(esta_para_word,)
		sql_insert(con, sql, entities)
		await message.channel.send("Se agregó la frase " + esta_para_word +  " a la lista de frases.")
	elif message.content.startswith("/borrarestapara"):
		esta_para_word = message.content.split("/borrarestapara ",1)[1]
		sql='DELETE FROM esta_para WHERE phrase = (?)'
		entities=(esta_para_word,)
		sql_insert(con, sql, entities)
		await message.channel.send("Se borró la frase " + esta_para_word +  " de la lista de frases.")
	elif message.content.startswith("/listarestapara"):
		sql = "SELECT phrase FROM esta_para;"
		rows = sql_fetch(con, sql)
		text="Está para:\n"
		for row in rows:
			text=text+"-"+str(row[0])+"\n"
		await message.channel.send(text)

	if "hello" in message.content:
		sql = "SELECT word FROM words WHERE word = 'hello';"
		row = sql_row_count(con, sql)
		if row is None:
			sql = 'INSERT INTO words(word, quantity) VALUES(?, ?)'
			entities=("hello",1)
			sql_insert(con, sql, entities)
		else:
			sql = "UPDATE words SET quantity = quantity + 1 WHERE word='hello';"
			sql_update(con, sql)
		sql="SELECT * FROM words WHERE word = 'hello'"
		rows=sql_fetch(con,sql)
		for row in rows:
			await message.channel.send("hello")

client.run('')



