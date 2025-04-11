## Codebase Evaluation – AutoCite_CLI.py

I explored the command-line Python tool AutoCite_CLI.py from the AutoCite project (https://github.com/BrandonTang89/AutoCite), which automatically creates citations (APA and Chicago).

### ✅ What Worked
- I ran the script succesfully and it works.
- The project has both CLI support and python gui which uses Tkinter (not flask). 
- The script will extract author, title, publish dates, and access dates using BeutifulSoup and regex.
- It does very well ouputs the data in Chicago and APA format. 

### ⚠️ What Didn’t Work or Could Improve
- There's no support for MLA format
- There's no error message support if the link provided fails and no manual input
- No history

### 💡 What I Will Reuse for SmartCite
- I will probably reuse the `citation_components()` and the formatting logic in my Flask app.
- I will also be adding MLA support, and provide history tracking.
