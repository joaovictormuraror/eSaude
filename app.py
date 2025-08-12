from flask import Flask

app = Flask(_name_)

@app.route('/')
def home():
    return '<p>funcionando</p>'

@app.route('/sobre')
def sobre():
    return '<h1>Sobre</h1><p> exemplo.</p>'

# Executar
if _name_ == '_main_':
    app.run(debug=True)