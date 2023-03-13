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


colors = ['hotpink', 'mediumslateblue', 'royalblue', 'darkcyan', 'springgreen', 'forestgreen',
        'olive', 'gold', 'darkgoldenrod', 'orange', 'orangered', 'firebrick', 'gray', 'blue', 'red',
        'magenta', 'crimson', 'yellow', 'lime', 'darkolivegreen', 'darkkhaki', 'darkseagreen', 'mediumvioletred']
cols = ['titulo', 'autor', 'ano', 'genero']
db_path = 'booksdb.db'
a_cols = ['nome', 'nasc', 'pais']

def df_from_sql(query):
    with sqlite3.connect(db_path) as connie:
        df = pd.read_sql_query(query, connie)
        print(df.head())
        print(type(df))
    return(df)

# GENERAL PURPOSE VARRIABLES:
query_all_books = "SELECT * FROM books"


books_df = df_from_sql(query_all_books)
books_df.sort_values(inplace=True, by="ano")



avg_book_year = books_df['ano'].mean()
print(avg_book_year)

authors_df = df_from_sql("SELECT * FROM authors")

authors_df.sort_values(inplace=True, by='nasc')

earliest_author = authors_df.iloc[0]
mostrecent_author = authors_df.iloc[-1]
print(earliest_author)
print(mostrecent_author)

avg_birthyear = authors_df['nasc'].mean()

bookcounts_per_author = books_df['autor'].value_counts(ascending=False)
top_author_per_genre = books_df.groupby(['genero'])['autor'].agg(pd.Series.mode)


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
both_df.to_csv('C:/Users/STI/Downloads/both_df.csv')

both_df['idade'] = both_df['ano'] - both_df['nasc']
avg_age_by_genre = both_df.groupby(['genero'])['idade'].mean()
print(avg_age_by_genre)

avg_age = both_df['idade'].mean()
bookcounts_per_country = both_df['pais'].value_counts(ascending=False)
bookcounts_per_country = bookcounts_per_country[0:10]

bookcounts_per_genre = books_df['genero'].value_counts(ascending=False)

country_most_books = bookcounts_per_country.iloc[0]


top_country_genre = both_df.groupby('pais')['genero'].apply(lambda x: x.value_counts().index[0]).reset_index()




avg_country_year = both_df.groupby(['pais'])['ano'].mean()
avg_country_age = both_df.groupby(['pais'])['idade'].mean().round(decimals = 0).astype('int')
avg_country_age.sort_values(inplace=True)
print('butico')
print(avg_country_age)
print('butico')

books_df.sort_values(inplace=True, by='ano')

oldest_book = books_df.iloc[0][['titulo', 'autor', 'ano']]
newest_book = books_df.iloc[-1][['titulo', 'autor', 'ano']]

both_df.sort_values(inplace=True, by='idade')

highest_age = both_df.iloc[-1][['titulo', 'autor', 'idade']]
lowest_age = both_df.iloc[0][['titulo', 'autor', 'idade']]


countrycount_per_genre = both_df.groupby(['genero']).nunique()['pais'].copy()
countrycount_per_genre.sort_values(inplace=True, ascending=False)


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
                
                highest_genre_age = round(avg_age_by_genre.sort_values(ascending=False)[0],2)
                highest_age_genre = avg_age_by_genre.sort_values(ascending=False).index[0]
                lowest_genre_age = round(avg_age_by_genre.sort_values(ascending=False)[-1],2)
                lowest_age_genre = avg_age_by_genre.sort_values(ascending=False).index[-1]
                
                paises_livros = bookcounts_per_country[0:5].index
                livros_paises = bookcounts_per_country[0:5].values
                countries_bookcounts_string = ""
                for i in range(0, 5):
                    countries_bookcounts_string += (f"{paises_livros[i]}: {livros_paises[i]} livros.")
                    countries_bookcounts_string += "\t"
                
                
                statsd = {}    
                statsd['Livro mais antigo'] = f"Titulo: {oldest_book['titulo']}, Ano: {oldest_book['ano']}"
                statsd['Livro mais recente'] = f"Titulo: {newest_book['titulo']}, Ano: {newest_book['ano']}"
                statsd['Ano médio de lançamento'] = int(avg_book_year)
                statsd['Autor mais antigo'] = f"Nome: {earliest_author['nome']}, Ano de nascimento: {earliest_author['nasc']}"
                statsd['Autor mais recente'] = f"Nome: {mostrecent_author['nome']}, Ano de nascimento: {mostrecent_author['nasc']}"
                statsd['Ano médio de nascimento'] = int(avg_birthyear)
                statsd['Países com mais livros'] = countries_bookcounts_string
                statsd['Média de livros por autor'] = round(avg_books_per_author, 2)
                statsd['Autor mais jovem na data de publicação'] = f"Nome: {lowest_age['autor']}, Idade: {lowest_age['idade']} anos, Livro: {lowest_age['titulo']}"
                statsd['Autor mais velho na data de publicação'] = f"Nome: {highest_age['autor']}, Idade: {highest_age['idade']} anos, Livro: {highest_age['titulo']}"
                statsd['Idade média do autor na data da publicação'] = round(avg_age,2)
                statsd['Gênero com maior média de idade de autor'] = f"{highest_age_genre}: {round(highest_genre_age)} anos"
                statsd['Gênero com menor média de idade de autor'] = f"{lowest_age_genre}: {round(lowest_genre_age)} anos"
                """
                statlist = []
                for skey, svalue in statsd.items():
                    statlist.append([skey,svalue])
                print(statlist)
                """
                return (render_template("stats.html", statsd=statsd))
            
        return (render_template('views.html'))


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
    axis.set_ylabel("Número de livros")
    axis.set_xlabel("Década")
    axis.grid(True)
    axis.plot(xd, yd)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/topautores')
def plot_topautores():
    
    x = bookcounts_per_author[0:5].index
    y = bookcounts_per_author[0:5].values
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_ylabel("Número de livros")
    axis.set_xlabel("Autor")
    axis.grid(False)
    axis.bar(x, y, color=[colors[i] for i in range(len(x))])
    plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')
    fig.autofmt_xdate()
    plt.tight_layout()
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/topautorgeneros')
def plot_topautorgeneros():
    

    generos = top_author_per_genre.index
    autores = top_author_per_genre.values
    contagem = []
    for author in autores:
        contagem.append(bookcounts_per_author[author])

    
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Número de livros")
    axis.set_xlabel("Autor")
    axis.grid(False)
    axis.bar(autores, contagem, label=generos, color=[colors[i] for i in range(len(generos))])
    plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')

    axis.bar_label(axis.containers[0], label_type='center', labels=generos, rotation=90)
    fig.autofmt_xdate()
    plt.tight_layout()
    
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@app.route('/plot/topgeneros')
def plot_topgeneros():
    
    x = bookcounts_per_genre.index
    y = bookcounts_per_genre.values
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_ylabel("Número de livros")
    axis.grid(False)
    axis.bar(x, y, color=[colors[i] for i in range(len(x))])
    plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')
    fig.autofmt_xdate()
    plt.tight_layout()
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    
    return response


@app.route('/plot/paisesporgenero')
def plot_paisesporgenero():
    
    x = countrycount_per_genre.index
    y = countrycount_per_genre.values
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_ylabel("Número de países distintos")
    axis.grid(False)
    axis.bar(x, y, color=[colors[i] for i in range(len(x))])
    plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')
    fig.autofmt_xdate()
    plt.tight_layout()
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    
    return response

@app.route('/plot/livrosporpais')
def plot_livrosporpais():
    
    df = df_from_sql(query_all_books)
    
    x = bookcounts_per_country.index
    y = bookcounts_per_country.values
    
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_ylabel("Número de livros")
    axis.grid(False)
    axis.bar(x, y, color=[colors[i] for i in range(len(x))])
    axis.set_ylim(0,y.max()+5)
    plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')
    
    fig.autofmt_xdate()
    plt.tight_layout()    
    
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/generoporpais')
def plot_generoporpais():
    
    
    
    country_genre_counts = both_df.groupby(['pais', 'genero']).size()
    country_genre_counts.sort_values(ascending=False, inplace=True)
    data = pd.DataFrame(columns=['pais', 'genero', 'nlivros'])
    lista = []

    for i in range(0,country_genre_counts.index.shape[0],1):
        lista.append({'pais':country_genre_counts.index[i][0],
                    'genero':country_genre_counts.index[i][1],
                    'nlivros':country_genre_counts.values[i]})
    
    data = pd.DataFrame(lista)
    data.drop_duplicates(subset='pais',inplace=True)
    
    top_country_genres = data.iloc[0:5]
    
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_ylabel("Número de Livros")
    axis.grid(False)
    print('aqui')
    axis.bar(x=top_country_genres['genero'], height=top_country_genres['nlivros'], color=[colors[i] for i in range(len(top_country_genres['genero']))], label=top_country_genres['pais'])
    axis.bar_label(axis.containers[0], label_type='edge', labels=top_country_genres['pais'], padding=-14)
    #axis.bar(x, y, color=[colors[i] for i in range(len(x))])
    #axis.bar_label(axis.containers[0], label_type='center', labels=y, rotation=90)
    plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')
    fig.autofmt_xdate()
    plt.tight_layout()
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/anomediopais')
def plot_anomediopais():
    
    x = avg_country_year.index
    y = avg_country_year.values
    
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_ylabel("Ano médio de publicação")
    axis.grid(False)
    axis.bar(x, y, color=[colors[i] for i in range(len(x))])
    axis.set_ylim(y.min()-20,y.max()+1)
    plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')
    fig.autofmt_xdate()
    plt.tight_layout()
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/mediaidadepais')
def plot_mediaidadepais():
    
    x = avg_country_age.index
    y = avg_country_age.values
    
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_ylabel("Média de idade na data de publicação")
    axis.grid(False)
    axis.bar(x=x, height=y, color=[colors[i] for i in range(len(x))])
    axis.set_ylim(y.min()-20,y.max()+1)
    plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')
    fig.autofmt_xdate()
    plt.tight_layout()
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@app.route('/plot/histidades')
def plot_histidades():
    
    
    
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_xlabel("Idade na data de publicação")
    axis.hist(both_df['idade'])
    axis.axvline(x=both_df['idade'].mean(), color='orange', label='Média')
    fig.autofmt_xdate()
    plt.tight_layout()
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    
    return response


@app.route('/plot/decadasnasc')
def plot_decadasnasc():
    
    
    
    both_df['decada'] = 10 * (both_df['nasc'] // 10)
    
    xd = both_df.groupby('decada').size().index
    yd = both_df.groupby('decada').size().values
    
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_ylabel("Número de autores")
    axis.set_xlabel("Década")
    axis.grid(True)
    axis.plot(xd, yd)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@app.route("/about")
def about():
    return(render_template("about.html"))



print(top_author_per_genre)

app.run(debug=True, port=5050)

