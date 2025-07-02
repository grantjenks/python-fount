from flask import Flask, request, render_template_string

app = Flask(__name__)

FORM = """
<!doctype html>
<html>
  <head></head>
  <body>
    <title>Hello</title>
    <h1>Hello {{name}}!</h1>
    <form method="post">
      <label>Your name: <input name="name"></label>
      <button>Submit</button>
    </form>
    <p><a href="/">Home</a></p>
  </body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    name = request.form.get('name') or 'World'
    return render_template_string(FORM, name=name)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
