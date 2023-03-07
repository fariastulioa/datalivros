from stat import FILE_ATTRIBUTE_SYSTEM
from flask import Flask,render_template,request,redirect,url_for,flash, make_response, Response, send_file
import sqlite3
import os
import pandas as pd
from io import BytesIO
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from cycler import cycler
from numpy import arange
import seaborn as sns
import json
from flask import escape, Markup
from io import StringIO
import base64

from bokeh.embed import components
from bokeh.plotting import figure

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

from flask import Flask, render_template, send_file, make_response, request

plt.rc('image', cmap='Set3')
plt.rcParams['axes.prop_cycle'] = cycler('color', plt.get_cmap('Set3').colors)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Stats to add to general stats page:

# top authors
# avg author age (general/by genre)
# avg year
# top genres
# oldest, newest books
# oldest, newest authors


# CREATE, READ, UPDATE, DELETE
"""
# Tabela Livros
genero
ano
autor
titulo
id_livro

# Tabela Autores
nome (autores.nome == livros.autor)
nasc
pais

"""

cols = ['titulo', 'autor', 'ano', 'genero']
db_path = 'booksdb.db'
a_cols = ['nome', 'nasc', 'pais']



def get_top_x(table_name, col_names, x, order_col):
    with sqlite3.connect(db_path) as connie:
        c = connie.cursor
        col_names = ", ".join(col_names)
        sql_execute_string = f"SELECT {col_names} FROM {table_name} GROUP BY {order_col} ORDER BY COUNT({order_col}) DESC LIMIT {x}"
        c.execute(sql_execute_string)
        top_x_info = c.fetchall()
        return(top_x_info)


def delete_data(condition, table_name):
    
    with sqlite3.connect(db_path) as connie:
        c = connie.cursor()
        sql_execute_string = f"DELETE FROM {table_name} WHERE {condition}"
        c.execute(sql_execute_string)



def remove_book(book_id):
    execute_string = f"DELETE FROM books WHERE id = {book_id}"
    get_name_string = f"SELECT titulo FROM books WHERE id = {book_id}"
    with sqlite3.connect(db_path) as connie:
        c = connie.cursor()
        c.execute(get_name_string)
        deletado = c.fetchall()
        c.execute(execute_string)

    return(deletado)


def remove_author(nome_autor):
    execute_string = f"DELETE FROM authors WHERE nome = {nome_autor}"
    with sqlite3.connect(db_path) as connie:
        c = connie.cursor()
        c.execute(execute_string)
    return(nome_autor)


def alter_book(book_id, titulo, autor, ano, genero):
    execute_string = f"""UPDATE books SET "titulo" = "{titulo}", "autor" = '{autor}', ano = {ano}, "genero"= "{genero}" WHERE "id" = {book_id}"""
    with sqlite3.connect(db_path) as connie:
        c = connie.cursor()
        c.execute(execute_string)


def alter_author(nome_autor, nasc, pais):
    execute_string = f"""UPDATE authors SET "nome" = "{nome_autor}", nasc = {nasc}, "pais" = '{pais}' WHERE "nome" = '{nome_autor}'"""
    with sqlite3.connect(db_path) as connie:
        c = connie.cursor()
        c.execute(execute_string)

def query_all_data():
    with sqlite3.connect(db_path) as connie:
        c = connie.cursor()
        c.execute("""
SELECT * FROM books
""")
        all_data = c.fetchall()

    return(all_data)


def query_authors():
    with sqlite3.connect(db_path) as connie:
        c = connie.cursor()
        c.execute("""
SELECT * FROM authors
""")
        all_data = c.fetchall()
        
    return(all_data)


@app.route("/")
@app.route("/home")
def home():

    all_data = query_all_data()
    below_data = query_authors()
    return render_template("home.html",all_data=all_data, below_data=below_data, **request.args)



@app.route("/add_book",methods=['POST','GET'])
def add_book():
    if request.method=='POST':

        titulo=request.form['titulo']
        autor=request.form['autor']
        ano=request.form['ano']
        genero=request.form['genero']
        
        campos = ",".join(cols)

        qmarks = ",".join((['?'] * 4))

        execute_string = f"INSERT INTO books({campos}) values ({qmarks})"


        with sqlite3.connect(db_path) as connie:
            c = connie.cursor()
            c.execute(execute_string, (titulo, autor, ano, genero))
        
        message = "Livro adicionado com sucesso!"
        return redirect(url_for("home", message=message))
    else:
        all_data = query_all_data()
        return render_template("add_book.html",all_data=all_data)


@app.route("/update_book", methods=['POST', 'GET'])
def update_book():
    if request.method=='POST':
        id=request.form['id']
        titulo=request.form['titulo']
        autor=request.form['autor']
        ano=request.form['ano']
        genero=request.form['genero']
        
        alter_book(id, titulo, autor, ano, genero)
        
        message = f"Livro alterado com sucesso!"
        return redirect(url_for("home",message=message))
    else:
        all_data = query_all_data()
        return render_template("update_book.html", all_data=all_data)


@app.route("/delete_book", methods=['POST', 'GET'])
def delete_book():
    if request.method=='POST':
        id = request.form['id']
        deletado = str(remove_book(id))[2:-3]


        
        message = f"Livro {deletado} removido com sucesso!"
        return redirect(url_for("home", message=message))
    else:
        all_data = query_all_data()
        return render_template("delete_book.html",all_data=all_data)


@app.route("/add_author", methods=['GET', 'POST'])
def add_author():
    if request.method=='POST':

        nome_autor=request.form['nome_autor']
        nasc=request.form['nasc']
        pais=request.form['pais']

        execute_string = f"INSERT INTO authors(nome, nasc, pais) VALUES ('{nome_autor}', {nasc}, '{pais}')"

        with sqlite3.connect(db_path) as connie:
            c = connie.cursor()
            c.execute(execute_string)
        
        message = "Autor adicionado com sucesso!"
        return redirect(url_for("home", message=message))
    else:
        all_data = query_authors()
        return render_template("add_author.html",all_data=all_data)


@app.route("/update_author", methods=['GET', 'POST'])
def update_author():
    if request.method=='POST':
        nome_autor=request.form['nome_autor']
        nasc=request.form['nasc']
        pais=request.form['pais']

        
        alter_author(nome_autor, nasc, pais)
        
        message = f"Autor alterado com sucesso!"
        return redirect(url_for("home",message=message))
    else:
        all_data = query_authors()
        return render_template("update_author.html", all_data=all_data)


@app.route("/delete_author", methods=['POST', 'GET'])
def delete_author():
    if request.method=='POST':
        nome_autor = request.form['nome_autor']
        deletado = str(remove_author(nome_autor))[2:-3]
        message = f"Autor {deletado} removido com sucesso!"
        return redirect(url_for("home", message=message))
    else:
        all_data=query_authors()
        return render_template("delete_author.html", all_data=all_data)



@app.route("/views", methods=['GET', 'POST'])
def views():
    if request.method=='GET':
        return (render_template('views.html'))
    else:
        choice = int(request.form.get('pickone'))
        print(choice)
        match choice:
            case 1:
                return render_template("top_autores.html")
            case 2:
                return render_template("top_generos.html")
            case 3:
                return render_template("cronolivros.html")
            case 4:
                return render_template("cronoautores.html")
            case 5:
                return render_template("countries.html")
            case 6:
                return render_template("stats.html")
            
        return (render_template('views.html'))

@app.route("/topautores")
def topautores():
    # grafico de barras com total de livros por autor (top autores)
    pass


@app.route("/topgeneros")
def topgeneros():
    # grafico de barras com total de livros por genero (top generos)
    pass


@app.route("/cronolivros",methods=['POST','GET'])
def cronolivros():
    df = df_from_sql(query_all_books)
    
    x = df.groupby('ano').size().index
    y = df.groupby('ano').size().values
        
    df['decada'] = 10 * (df['ano'] // 10)
    
    xd = df.groupby('decada').size().index
    yd = df.groupby('decada').size().values
    
    
    p1 = figure(height=400, sizing_mode="stretch_width")
    p1.vbar(x=x, top=y, width=0.7)
    p1.xgrid.grid_line_color= None
    script1, div1 = components(p1)
    
    p2 = figure(height=400, sizing_mode="stretch_width")
    p2.vbar(x=xd, top=yd, width=0.7)
    p2.xgrid.grid_line_color= None
    script2, div2 = components(p1)
    
    
    # aqui deveria retornar-se uma imagem com o grafico
    return (render_template('cronolivros.html', script1=Markup(script1), script2=Markup(script2),div1=Markup(div1),div2=Markup(div2)))

@app.route('/plot/livrosporano')
def plot_livrosporano():
    df = df_from_sql(query_all_books)
    
    x = df.groupby('ano').size().index
    y = df.groupby('ano').size().values
    
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Número de livros")
    axis.set_xlabel("Ano")
    axis.grid(True)
    axis.plot(x, y)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/livrospordecada')
def plot_livrospordecada():
    df = df_from_sql(query_all_books)
    
    df['decada'] = 10 * (df['ano'] // 10)
    
    xd = df.groupby('decada').size().index
    yd = df.groupby('decada').size().values
    
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Número de livros")
    axis.set_xlabel("Década")
    axis.grid(True)
    axis.plot(xd, yd)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/g1')
def g1():

    
    return json.dumps(bokeh.embed.json_item(item_text, "myplot"))



@app.route("/cronoautores")
def cronoautores():
    # grafico barras com nascimeento dos autores por decada
    # grafico idade dos autores na publicacao do livro
    # Total count de cada ano X ano
    
    pass


@app.route("/stats")
def stats():
    # mostrar dados interessantes
    # top genero, top autor de cada genero, top autor, livro mais velho, livro mais recente, genero menos lido
    # idade media na publicacao do livro
    # media idade por genero
    # autor mais velho
    # autor mais novo
    # media livro por autor
    pass


@app.route("/about")
def about():
    return(render_template("about.html"))






def df_from_sql(query):
    with sqlite3.connect(db_path) as connie:
        df = pd.read_sql_query(query, connie)
        print(df.head())
        print(type(df))
    return(df)

query_all_books = "SELECT * FROM books"


books_df = df_from_sql(query_all_books)
books_df.sort_values(inplace=True, by="ano")

oldest_book = books_df.iloc[0]
newest_book = books_df.iloc[-1]
print(oldest_book)
print(newest_book)

avg_book_year = books_df['ano'].mean()
print(avg_book_year)

authors_df = df_from_sql("SELECT * FROM authors")

authors_df.sort_values(inplace=True, by='nasc')

oldest_author = authors_df.iloc[0]
newest_author = authors_df.iloc[-1]
print(oldest_author)
print(newest_author)


bookcounts_per_author = books_df['autor'].value_counts(ascending=True)

avg_year_by_genre = books_df.groupby(['genero'])['ano'].mean()
print(avg_year_by_genre)

avg_books_per_author = bookcounts_per_author.mean()
print(avg_books_per_author)

author_most_books = books_df['autor'].mode()
print(author_most_books)
most_books = bookcounts_per_author[-1]

query_both_string = """
SELECT * FROM books
INNER JOIN authors ON books.autor = authors.nome;
"""

both_df = df_from_sql(query_both_string)
print(both_df)

both_df['idade'] = both_df['ano'] - both_df['nasc']
avg_age_by_genre = both_df.groupby(['genero'])['idade'].mean()
print(avg_age_by_genre)

bookcounts_per_country = both_df['pais'].value_counts(ascending=True)


country_most_books = bookcounts_per_country.iloc[-1]
print(country_most_books)

books_df.sort_values(inplace=True, by='ano')

oldest_book = books_df.iloc[0][['titulo', 'autor', 'ano']]
newest_book = books_df.iloc[-1][['titulo', 'autor', 'ano']]
print(oldest_book)
print(newest_book)

both_df.sort_values(inplace=True, by='idade')

highest_age = both_df.iloc[0][['titulo', 'autor', 'idade']]
lowest_age = both_df.iloc[-1][['titulo', 'autor', 'idade']]
print(highest_age)
print(lowest_age)

# TEMPLATES DE GRAFICOS PARA EXPOR NO HTML


def total_per_year(df):

    x = df.groupby('ano').size().index
    y = df.groupby('ano').size().values

    
    fig, ax = plt.subplots(figsize=(15,12))
    ax.tick_params(axis='both', which='major', labelsize=14)
    
    ax.bar(x, y)
    ax.axhline(y=y.mean(), color='tab:orange', linestyle='dashed', label='Média', linewidth=0.4)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_yticks(arange(0, y.max()+1, step=1))
    fig.tight_layout()
    ax.set_in_layout(True)
    
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.bar(x, y)
    plt.axhline(y=y.mean(), color='tab:orange', linestyle='dashed', label='Média', linewidth=0.4)
    plt.gca().spines['right'].set_color('none')
    plt.gca().spines['top'].set_color('none')
    plt.yticks(arange(0, y.max()+1, step=1))
    plt.tight_layout()
    plt.figure(figsize=(15,12),dpi=80)
    
    
    return((fig,plt))


def total_per_decade(df):

    df['decada'] = 10 * (df['ano'] // 10)
    
    x = df.groupby('decada').size().index
    y = df.groupby('decada').size().values

    
    fig, ax = plt.subplots(figsize=(15,12))
    ax.tick_params(axis='both', which='major', labelsize=14)

    ax.bar(x, y, width=1, linewidth=0.5)
    ax.axhline(y=y.mean(), color='tab:orange', linestyle='dashed', label='Média', linewidth=0.4)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_yticks(arange(0, y.max()+1, step=5))
    fig.tight_layout()
    ax.set_in_layout(True)
    
    
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.bar(x, y)
    plt.axhline(y=y.mean(), color='tab:orange', linestyle='dashed', label='Média', linewidth=0.4)
    plt.gca().spines['right'].set_color('none')
    plt.gca().spines['top'].set_color('none')
    plt.yticks(arange(0, y.max()+1, step=1))
    plt.tight_layout()
    plt.figure(figsize=(15,12),dpi=80)
    
    
    return((fig,plt))


def plot_genres(df):
    
    new_df = pd.DataFrame()
    new_df['x'] = df.groupby('genero').size().index
    new_df['y'] = df.groupby('genero').size().values
    new_df.sort_values(by='y', ascending=False, inplace=True)
    
    fig, ax = plt.subplots(figsize=(12,12))
    

    hbars = ax.barh(new_df['x'], new_df['y'], linewidth=0.85)
    ax.axvline(x=new_df['y'].mean(), color='tab:orange', linestyle='dashed', label='Média', linewidth=1.5)
    ax.bar_label(hbars, label_type='center')
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    fig.tight_layout()
    ax.set_in_layout(True)

    return(fig)


@app.route('/books_per_year.png') # colocar <img src="/books_per_year.png"> no HTML
def books_per_year():
    df = df_from_sql(query_all_books)
    
    x = df.groupby('ano').size().index
    y = df.groupby('ano').size().values
    

    

    df['decada'] = 10 * (df['ano'] // 10)
    
    xd = df.groupby('decada').size().index
    yd = df.groupby('decada').size().values
    

    
    # aqui deveria retornar-se uma imagem com o grafico
    return (render_template('cronolivros.html'))

@app.route('/books_per_decade.png')
def books_per_decade():
    df = df_from_sql(query_all_books)
    fig = total_per_decade(df)[1]
    output = BytesIO()
    FigureCanvas(fig).print_png(output)
    return (Response(output.getvalue(), mimetype='image/png'))


@app.route('/top_genres.png')
def top_genres():
    df = df_from_sql(query_all_books)
    fig = plot_genres(df)
    output = BytesIO()
    FigureCanvas(fig).print_png(output)
    return (Response(output.getvalue(), mimetype='image/png'))


app.run(debug=True, port=5050)

