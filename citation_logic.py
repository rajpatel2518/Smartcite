import urllib.request
import datetime
import re
import json
from bs4 import BeautifulSoup
from dateutil import parser


def citation_components(web_address):
    first_name = ""
    last_name = ""
    page_title = "Untitled Page"
    website_title = "Unknown"
    date_published = ""
    date_accessed = datetime.date.today().strftime("%B %d, %Y")

    try:
        req = urllib.request.Request(web_address, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
    except:
        return (first_name, last_name, page_title, website_title, date_published, date_accessed)

    try:
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") in ["NewsArticle", "Article"]:
                    if "author" in data:
                        author_data = data["author"]
                        if isinstance(author_data, dict):
                            author_name = author_data.get("name", "").strip()
                        elif isinstance(author_data, list):
                            author_name = author_data[0].get("name", "").strip()
                        else:
                            author_name = ""
                        if author_name:
                            name_parts = author_name.split()
                            if len(name_parts) >= 2:
                                first_name = name_parts[0]
                                last_name = name_parts[-1]
                    if "datePublished" in data:
                        parsed = parser.parse(data["datePublished"])
                        date_published = parsed.strftime("%B %d, %Y")
                    if "headline" in data:
                        page_title = data["headline"].strip()
                    break
            except:
                continue

    except:
        pass

    try:
        if not page_title or page_title == "Untitled Page":
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.has_attr("content"):
                page_title = og_title["content"].strip()
    except:
        pass

    if not page_title or page_title == "Untitled Page":
        try:
            title_tag = soup.find("title")
            if title_tag:
                page_title = title_tag.get_text().strip()
        except:
            pass

    if not page_title or page_title == "Untitled Page":
        try:
            h1_tag = soup.find("h1")
            if h1_tag:
                page_title = h1_tag.get_text().strip()
        except:
            pass

    try:
        match = re.search(r"(?:https?://)?(?:www\.)?([^/]+)", web_address)
        if match:
            website_title = match.group(1)
    except:
        pass

    try:
        if not first_name or not last_name:
            for tag in soup.find_all(["p", "div", "span"]):
                text = tag.get_text(strip=True)
                if text.lower().startswith("by "):
                    match = re.match(r"[Bb]y ([A-Z][a-z]+) ([A-Z][a-z]+)", text)
                    if match:
                        first_name = match.group(1)
                        last_name = match.group(2)
                        break
    except:
        pass

    try:
        if not first_name or not last_name:
            author_tag = soup.find(attrs={"class": re.compile(r"(author|byline).*", re.I)})
            if author_tag:
                author_name = author_tag.get_text(strip=True)
                name_parts = author_name.split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = name_parts[-1]
    except:
        pass

    try:
        if not date_published:
            time_tag = soup.find("time")
            if time_tag and time_tag.has_attr("datetime"):
                parsed = parser.parse(time_tag["datetime"])
                date_published = parsed.strftime("%B %d, %Y")
            elif time_tag and time_tag.string:
                parsed = parser.parse(time_tag.string)
                date_published = parsed.strftime("%B %d, %Y")
    except:
        pass

    try:
        if not date_published:
            all_text = soup.get_text()
            match = re.search(r'\b(20\d{2}|19\d{2})\b', all_text)
            if match:
                date_published = match.group(1)
    except:
        pass

    return (first_name, last_name, page_title.strip(), website_title.strip(), date_published, date_accessed)


def apa_compile(web_address):
    first_name, last_name, page_title, website_title, date_published, _ = citation_components(web_address)

    if first_name and last_name:
        citation = f"{last_name}, {first_name[0]}."
    else:
        citation = page_title

    if date_published:
        citation += f" ({date_published}). "
    else:
        citation += " (n.d.). "

    if first_name and last_name:
        citation += f"{page_title}. "

    citation += f"{website_title}. Retrieved from {web_address}"
    return citation


def chicago_compile(web_address):
    first_name, last_name, page_title, website_title, date_published, date_accessed = citation_components(web_address)

    author = f"{first_name} {last_name}." if first_name and last_name else ""
    site = f"<i>{website_title}</i>"
    citation = f"{author} \"{page_title}.\" {site}."

    if date_published:
        citation += f" Published {date_published}."
    citation += f" Accessed {date_accessed}. {web_address}"
    return citation


def mla_compile(web_address):
    first_name, last_name, page_title, website_title, date_published, date_accessed = citation_components(web_address)
    site = f"<i>{website_title}</i>"

    author = f"{last_name}, {first_name}." if first_name and last_name else ""
    citation = f"{author} \"{page_title}.\" {site}"
    if date_published:
        citation += f", {date_published}"
    citation += f", {web_address}. Accessed {date_accessed}."
    return citation


def citation_from_doi(doi: str, style: str):
    import requests
    if doi.startswith("https://doi.org/"):
        doi = doi.replace("https://doi.org/", "")

    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url)
        data = response.json()["message"]

        author_list = data.get("author", [])
        if author_list:
            first = author_list[0].get("given", "")
            last = author_list[0].get("family", "")
        else:
            first = last = ""

        title = data.get("title", ["Untitled"])[0]
        container = data.get("container-title", [""])[0]
        year = data.get("published-print", {}).get("date-parts", [[None]])[0][0] or "n.d."
        accessed = datetime.date.today().strftime("%d %b. %Y")
        link = f"https://doi.org/{doi}"

        if style == "apa":
            if first and last:
                return f"{last}, {first[0]}. ({year}). {title}. {container}. {link}"
            else:
                return f"{title} ({year}). {container}. {link}"

        elif style == "chicago":
            author = f"{first} {last}." if first and last else ""
            return f"{author} \"{title}.\" <i>{container}</i>. Published {year}. Accessed {accessed}. {link}"

        elif style == "mla":
            author = f"{last}, {first}." if first and last else ""
            return f"{author} \"{title}.\" <i>{container}</i>, {year}, {link}. Accessed {accessed}."

    except Exception as e:
        return f"Error generating citation from DOI: {e}"