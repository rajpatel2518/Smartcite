from flask import Flask, render_template, request, session, make_response
from citation_logic import (
    citation_components,
    apa_compile,
    chicago_compile,
    mla_compile,
    citation_from_doi
)
import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session usage

@app.route('/')
def index():
    history = session.get("history", [])
    return render_template("index.html", history=history)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/confirm', methods=['POST'])
def confirm():
    url = request.form.get('url')
    style = request.form.get('style')
    first = request.form.get('first_name')
    last = request.form.get('last_name')
    title = request.form.get('page_title')
    website = request.form.get('website_title')
    published = request.form.get('date_published')

    # If fields weren't included (like from Edit), fetch them
    if not all([first, last, title, website, published]):
        first, last, title, website, published, _ = citation_components(url)

    return render_template("confirm.html",
        first_name=first,
        last_name=last,
        page_title=title,
        website_title=website,
        date_published=published,
        web_address=url,
        style=style
    )

@app.route('/generate', methods=['POST'])
def generate():
    url = request.form.get('web_address')
    style = request.form.get('style')

    is_doi = url.lower().startswith("10.") or "doi.org" in url.lower()

    if is_doi:
        citation = citation_from_doi(url, style)
    elif style == 'apa':
        citation = apa_compile(url)
    elif style == 'chicago':
        citation = chicago_compile(url)
    elif style == 'mla':
        citation = mla_compile(url)
    else:
        citation = "Invalid citation style selected."

    entry = {
        "citation": citation,
        "url": url,
        "style": style
    }

    if "history" not in session:
        session["history"] = []
    session["history"].append(entry)
    session.modified = True

    return render_template("result.html", citation=citation)

@app.route('/clear', methods=['POST'])
def clear():
    session.pop("history", None)
    return render_template("index.html", history=[])

@app.route('/export', methods=['POST'])
def export():
    history = session.get("history", [])
    content = "\n".join(item["citation"] for item in history)
    response = make_response(content)
    response.headers["Content-Disposition"] = "attachment; filename=citation_history.txt"
    response.headers["Content-Type"] = "text/plain"
    return response

if __name__ == '__main__':
    app.run(debug=True)