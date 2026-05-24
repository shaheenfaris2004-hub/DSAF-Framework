from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def home():
    return "DSAF Test Application"

@app.route("/search")
def search():
    q = request.args.get("q", "")
    template = f"""
    <html>
        <body>
            <h1>Search Result</h1>
            <p>{q}</p>
        </body>
    </html>
    """
    return render_template_string(template)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
