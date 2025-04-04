from flask import Flask, render_template
from pages.graph import get_graph  # Import the graph function

app = Flask(__name__)

# Route to render the HTML page
@app.route("/")
def home():
    return render_template("index.html")

# Route to serve the graph
app.add_url_rule('/graph', 'get_graph', get_graph)

if __name__ == "__main__":
    app.run(debug=True)
