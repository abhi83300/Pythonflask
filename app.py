from flask import Flask
app = Flask(__name__)

@app.route('/<nam>')
def home(nam):
    return "Hello " + nam
@app.route('/about')
def about():
    return "this is about page"

@app.route('/product')
def product():
    return "this is product page"

@app.route('/product/laptop')
def laptop():
    return "this is product lap page"




if __name__ == '__main__':
    app.run(debug=True)
    

