from flask import Flask, render_template, request
from citation_logic import citation_components, apa_compile, chicago_compile, mla_compile, citation_from_doi
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/confirm', methods=['POST'])
def confirm():
    url = request.form.get('url')
    style = request.form.get('style')
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

    # Check if the input is a DOI
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

    return render_template("result.html", citation=citation)

if __name__ == '__main__':
    app.run(debug=True)