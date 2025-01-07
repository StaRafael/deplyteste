from flask import Flask, render_template, request, redirect, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "chave_secreta"

# Configuração do banco de dados
DB_NAME = "Cadastro.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cadastro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            data TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/gerar", methods=["POST"])
def gerar_codigos():
    ano = "W3A-25"
    projeto = request.form["projeto"].strip()
    amostra = request.form["amostra"].strip()
    quantidade = request.form["quantidade"].strip()

    if not projeto or not amostra or not quantidade.isdigit():
        flash("Preencha todos os campos corretamente!")
        return redirect("/")

    quantidade = int(quantidade)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Obter o maior número
    cursor.execute(f"""
        SELECT MAX(CAST(SUBSTR(codigo, -2) AS INTEGER))
        FROM cadastro
        WHERE codigo LIKE ?
    """, (f"{ano}-{projeto}-{amostra}-%",))
    ultimo_numero = cursor.fetchone()[0] or 0

    # Gerar novos códigos
    for i in range(1, quantidade + 1):
        novo_codigo = f"{ano}-{projeto}-{amostra}-{ultimo_numero + i:02d}"
        cursor.execute("INSERT INTO cadastro (codigo, data) VALUES (?, ?)", 
                       (novo_codigo, datetime.now().strftime("%Y-%m-%d")))

    conn.commit()
    conn.close()

    flash("Códigos gerados com sucesso!")
    return redirect("/")

@app.route("/pesquisar", methods=["POST"])
def pesquisar():
    termo = request.form["termo"].strip()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT codigo FROM cadastro WHERE codigo LIKE ?", (f"%{termo}%",))
    resultados = cursor.fetchall()

    conn.close()

    return render_template("index.html", resultados=[r[0] for r in resultados])

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
