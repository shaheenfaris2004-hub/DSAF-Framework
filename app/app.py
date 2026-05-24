from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def home():
    return "DSAF Test Application"


@app.route("/search")
def search():
    query = request.args.get("q", "")
    query = query[:100]
    return render_template("search.html", query=query)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
