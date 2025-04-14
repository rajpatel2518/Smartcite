from flask import Flask, render_template, request
from citation_logic import citation_components, apa_compile, chicago_compile
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
    first = request.form.get('first_name')
    last = request.form.get('last_name')
    title = request.form.get('page_title')
    website = request.form.get('website_title')
    published = request.form.get('date_published')
    accessed = datetime.date.today().strftime("%B %d, %Y")
    url = request.form.get('web_address')
    style = request.form.get('style')

    if style == 'apa':
        if first and last:
            citation = f"{last}, {first[0]}. ({published if published else 'n.d.'}). {title}. {website}. Retrieved from {url}"
        else:
            citation = f"{title} ({published if published else 'n.d.'}). {website}. Retrieved from {url}"
    else:  # chicago
        if first and last:
            citation = f"{last}, {first}. \"{title}.\" {website}"
        else:
            citation = f"\"{title}.\" {website}"

        if published:
            citation += f", {published}"
        citation += f". {url}. Accessed {accessed}."

    return render_template("result.html", citation=citation)

if __name__ == '__main__':
    app.run(debug=True)
