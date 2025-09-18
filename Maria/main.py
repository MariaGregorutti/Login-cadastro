from flask import Flask, render_template, request, flash, redirect, url_for
import fdb

app = Flask(__name__)
app.secret_key = 'qualquercoisa'

host = 'localhost'
database = r'C:\Users\Aluno\Desktop\Maria\BANCO.FDB'
user = 'SYSDBA'
pasword = 'sysdba'

con = fdb.connect(host=host, database=database,user=user, password=pasword)

@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute("SELECT l.ID_LIVRO, l.TITULO, l.AUTOR, l.ANO_PUBLICACAO FROM LIVRO l")
    livros = cursor.fetchall()
    cursor.close()

    return render_template('livros.html', livros=livros)


@app.route('/lista_usuario')
def lista_usuario():
    cursor = con.cursor()
    cursor.execute("SELECT l.ID_usuario, l.nome, l.email, l.senha FROM usuarios l")
    usuarios = cursor.fetchall()
    cursor.close()

    return render_template('usuarios.html', usuarios=usuarios)


@app.route("/novo")
def novo():
    return render_template('novo.html', titulo="Novo Livro")

@app.route('/criar', methods=['POST'])
def criar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicacao = request.form['ano_publicacao']

    cursor = con.cursor()
    try:
        cursor.execute('SELECT 1 FROM LIVRO l WHERE l.TITULO = ?', (titulo,))
        if cursor.fetchone(): #se existir algum livro com o titulo passado
            flash("Erro: Livro já cadastrado", 'error')
            return redirect(url_for('novo'))

        cursor.execute(''' INSERT INTO LIVRO (TITULO, AUTOR, ANO_PUBLICAcao)
                           VALUES (?, ?, ?)''', (titulo, autor, ano_publicacao))

        con.commit()
    finally:
        cursor.close()
    flash('Livro cradastrado com sucesso', 'success')
    return  redirect(url_for('index'))

@app.route('/atualizar')
def atualizar():
    return render_template('editar.html', titulo="Editar Livro")

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor=con.cursor() # abre cursor
    cursor.execute('SELECT id_livro, titulo, autor, ano_publicacao FROM LIVRO where id_livro = ?',(id,))
    livro = cursor.fetchone()

    if not livro:
        cursor.close()
        flash('Livro não encontrado')
        return redirect(url_for('index'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicado = request.form['ano_publicacao']

        cursor.execute('update livro set titulo = ?, autor = ?, ano_publicacao= ? where id_livro = ?',
                       (titulo, autor, ano_publicado, id))

        con.commit()
        flash('Livro atualizado com sucesso')
        return redirect(url_for('index'))

    cursor.close()
    return render_template('editar.html', livro=livro, titulo='Editar livro')

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cursor = con.cursor()  # Abre o cursor
    try:
        cursor.execute('delete from livro where id_livro = ?', (id,))
        con.commit()
        flash('Livro removido com sucesso!')

    except Exception as e:
        con.rollback()
        flash('Erro ao deletar o livro')
    finally:
        cursor.close()
        return redirect(url_for('index'))
@app.route('/cadastrar', methods=['POST', 'GET'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        con_local = fdb.connect(host=host, database=database, user=user, password=pasword)
        cursor = con_local.cursor()


        cursor.execute("SELECT * FROM USUARIOS WHERE EMAIL = ?", (email,))
        if cursor.fetchone():
            flash('Email já cadastrado')
            cursor.close()
            con_local.close()
            return redirect(url_for('cadastrar'))


        cursor.execute("INSERT INTO USUARIOS (NOME, EMAIL, SENHA) VALUES (?, ?, ?)", (nome, email, senha))
        con_local.commit()
        cursor.close()
        con_local.close()
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('login'))

    
    return render_template('cadastrar.html')

@app.route('/login',methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

con_local = fdb.connect(host=host, database=database, user=user, password=pasword)
cursor = con_local
cursor.execute("SELECT id_usuario, nome, email, senha FROM USUARIOS WHERE email = ?", (email))
user_db = cursor.fetchone()
cursor.close()
con_local.close()

 if user_db and user_db[3] == senha:
     session['user_id'] = user_db[0]
     session['user_name'] = user_db[1]
     flask('Login bem-sucedido')
     return redirect(url_for('index'))
 else:
     flash('Email ou senha inválidos!')


if __name__ == '__main__':
    app.run(debug=True)