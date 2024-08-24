import markdown2
from bs4 import BeautifulSoup

def remove_markdown(testo_markdown):
  # Converti il Markdown in HTML
  html = markdown2.markdown(testo_markdown)
  
  # Usa BeautifulSoup per estrarre il testo dall'HTML
  soup = BeautifulSoup(html, "html.parser")
  clean_text = soup.get_text().strip()
  
  return clean_text