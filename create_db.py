import sqlite3

# Comando sql para criar tabela dos autores
create_autores_string = """
CREATE TABLE "authors" (
"nome" TEXT PRIMARY KEY,
"nasc" INTEGER,
"pais" TEXT
)"""


# Comando sql para criar tabela dos livros
create_livros_string = """
CREATE TABLE "books" (
"id" INTEGER PRIMARY KEY AUTOINCREMENT,
"titulo" TEXT NOT NULL,
"autor" TEXT,
"ano" INTEGER,
"genero" TEXT
)"""


with sqlite3.connect('booksdb.db') as connie:
    c = connie.cursor()
    c.execute('DROP TABLE IF EXISTS books')
    c.execute('DROP TABLE IF EXISTS authors')
    c.execute(create_livros_string)
    c.execute(create_autores_string)

