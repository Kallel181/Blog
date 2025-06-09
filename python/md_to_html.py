import markdown
import yaml
from bs4 import BeautifulSoup
import re
import os
import shutil
import unicodedata

# Caminho absoluto de onde copiar as imagens
IMAGEM_DESTINO = "../static/images"

def slugify(value):
  """Gera um slug para usar como nome de arquivo (ex: Título do Post -> titulo_do_post)"""
  value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
  return re.sub(r'[^a-zA-Z0-9]+', '_', value).strip('_').lower()

def extrair_metadados(markdown_text):
  match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', markdown_text, re.DOTALL)
  if match:
      metadata_raw, content = match.groups()
      metadata = yaml.safe_load(metadata_raw)
      return metadata, content
  else:
      return {}, markdown_text

def clean_code_blocks(soup):
  for div in soup.find_all("div", class_="codehilite"):
    code_tag = div.find("code")
    classes = code_tag.get("class", []) if code_tag else []
    lang = next((cls.split('language-')[1] for cls in classes if cls.startswith('language-')), 'plaintext')
    raw_text = code_tag.get_text() if code_tag else ''
    new_code = soup.new_tag("code", attrs={"class": f"meu-code lang-{lang}"})
    new_code.string = raw_text
    new_pre = soup.new_tag("pre", attrs={"class": "meu-pre"})
    new_pre.append(new_code)
    div.clear()
    div.append(new_pre)
  return soup

def processar_imagens(md_text, titulo_slug,origem_imagem):
  imagem_map = {}
  imagem_count = 1
  def substituir(match):
    nonlocal imagem_count
    
    nome_original = match.group(1)
    extensao = os.path.splitext(nome_original)[1]
    novo_nome = f"{titulo_slug}_{imagem_count}{extensao}"
    imagem_count += 1
   
    # Copiar imagem
    src_path = os.path.join(origem_imagem, nome_original)
    dst_path = os.path.join(IMAGEM_DESTINO, novo_nome)
    
    if os.path.exists(src_path):
      shutil.copyfile(src_path, dst_path)
      print(f"Copiado: {src_path} → {dst_path}")
    else:
      print(f"Imagem não encontrada: {src_path}")
    imagem_map[nome_original] = novo_nome
    return f'<img src="/static/images/{novo_nome}" alt="{nome_original}"/>'
  
  novo_md = re.sub(r'!\[\[([^\]]+)\]\]', substituir, md_text)
  return novo_md

def markdown_para_html(markdown_body):
  html = markdown.markdown(markdown_body, extensions=['fenced_code'])
  soup = BeautifulSoup(html, 'html.parser')
  soup = clean_code_blocks(soup)
  return str(soup)

def gerar_html_template(md_file_path,origem_imagem):
  with open(md_file_path, 'r', encoding='utf-8') as f:
    md = f.read()
  meta, body = extrair_metadados(md)
  titulo = meta.get('title', 'Sem título')
  data = meta.get('date', '')
  tags = meta.get('tags', [])
    
  titulo_slug = slugify(titulo)
    
  # processar imagens inline e substituir blocos ![[imagem]]
  body = processar_imagens(body, titulo_slug,origem_imagem)
    
  html_conteudo = markdown_para_html(body)
  tags_html = ''.join(f'<span class="tag">{t}</span>' for t in tags)
  banner_nome = f"{titulo_slug}_banner.png"
    
  template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{titulo}</title>
  <link rel="stylesheet" href="/static/css/styles.css"/>
</head>
<body>
  <div class="container">
    <header class="post-header">
      <h1>{titulo}</h1>
      <div class="post-meta">
        <span class="date">{data}</span> —
        <span class="tags">{tags_html}</span>
      </div>
      <img class="post-banner" src="/static/images/{banner_nome}" alt="Imagem do post"/>
    </header>
    <article class="post-body">
      {html_conteudo}
    </article>
  </div>
</body>
</html>"""
  return template

