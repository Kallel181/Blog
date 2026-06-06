import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import markdown

# Configurações de Pastas Base do seu projeto
BASE_DIR = Path(__file__).parent.resolve()
POSTS_DIR = BASE_DIR / "static" / "posts"
IMAGES_DIR = BASE_DIR / "static" / "images"
JSON_PATH = BASE_DIR / "static" / "posts.json"

# Garantir que as pastas existam
POSTS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def selecionar_arquivo(titulo, tipos_arquivos):
    """Abre uma caixa de diálogo do sistema para escolher arquivos."""
    root = tk.Tk()
    root.withdraw() # Esconde a janela principal do tkinter
    root.attributes('-topmost', True) # Traz a janela para frente
    caminho = filedialog.askopenfilename(title=titulo, filetypes=tipos_arquivos)
    return Path(caminho) if caminho else None

def slugify(text):
    """Transforma 'Título do Post!' em 'titulo_do_post'."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '_', text).strip('_')

def processar_imagens_obsidian(body_text, slug_titulo, md_dir):
    """Encontra imagens no formato ![[imagem.png]], copia e renomeia para a pasta static."""
    count = 1
    padrao_obsidian = r'!\[\[([^\]]+)\]\]'
    
    def substituir(match):
        nonlocal count
        nome_original = match.group(1).strip()
        extensao = Path(nome_original).suffix or ".png"
        novo_nome_img = f"{slug_titulo}_{count}{extensao}"
        
        src_path = md_dir / nome_original
        dst_path = IMAGES_DIR / novo_nome_img
        
        if src_path.exists():
            shutil.copyfile(src_path, dst_path)
            print(f"-> Imagem interna copiada: {novo_nome_img}")
        else:
            print(f"[!] Aviso: Imagem interna não encontrada em: {src_path}")
            
        count += 1
        return f'<img src="https://kallel181.github.io/Blog/static/images/{novo_nome_img}" alt="{nome_original}"/>'

    return re.sub(padrao_obsidian, substituir, body_text)

def atualizar_json_posts(novo_post):
    """Adiciona o novo post no topo da lista do arquivo JSON existente."""
    if JSON_PATH.exists():
        with open(JSON_PATH, 'r+', encoding='utf-8') as f:
            dados = json.load(f)
            dados["posts"].insert(0, novo_post)
            f.seek(0)
            json.dump(dados, f, indent=4, ensure_ascii=False)
            f.truncate()
    else:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump({"posts": [novo_post]}, f, indent=4, ensure_ascii=False)

def gerar_html_final(titulo, data_str, tags, html_conteudo, slug_titulo):
    """Gera a string HTML usando a estrutura limpa e as tags dinâmicas."""
    tags_html = ''.join(f'<span class="tag">{t}</span>' for t in tags)
    banner_url = f"https://kallel181.github.io/Blog/static/images/{slug_titulo}_banner.png"
    
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{titulo}</title>
  <link rel="stylesheet" href="https://kallel181.github.io/Blog/static/css/styles.css"/>
  <link rel="stylesheet" href="https://kallel181.github.io/Blog/static/js/hljs/styles/github-dark.css">
</head>
<body>
  <div class="container">
    <header class="post-header">
      <a href="https://kallel181.github.io/Blog/" style="color: #ff8c42; text-align: left; display: block; text-decoration: none;">← Início</a>
      <h1>{titulo}</h1>
      <div class="post-meta">
        <span class="date">{data_str}</span> —
        <span class="tags">{tags_html}</span>
      </div>
      <img class="post-banner" src="{banner_url}" alt="Banner do post"/>
    </header>
    <article class="post-body">
      {html_conteudo}
    </article>
  </div>
  
  <script src="https://kallel181.github.io/Blog/static/js/hljs/highlight.js"></script>
  <script>hljs.highlightAll();</script>
</body>
</html>"""

def main():
    print("=== Gerador de Posts para o Blog ===")
    
    # 1. Selecionar Arquivo Markdown
    print("\n[Janela] Selecione o arquivo Markdown (.md)...")
    md_path = selecionar_arquivo("Selecione o arquivo Markdown", [("Markdown Files", "*.md")])
    if not md_path:
        print("Operação cancelada.")
        return

    # Ler o conteúdo completo do Markdown (sem se importar com metadados)
    with open(md_path, 'r', encoding='utf-8') as f:
        body_markdown = f.read()

    # 2. Perguntas no terminal para os metadados
    print("\n--- Informações do Post ---")
    titulo = input("Título do post: ").strip()
    while not titulo:
        titulo = input("O título não pode ser vazio. Título do post: ").strip()
        
    slug_titulo = slugify(titulo)

    tags_input = input("Tags (separadas por vírgula, ex: reversing, arm, windows): ")
    tags = [t.strip() for t in tags_input.split(",") if t.strip()]

    data_input = input("Data de publicação (DD/MM/AAAA) [Deixe em branco para usar HOJE]: ").strip()
    if data_input:
        try:
            data_objeto = datetime.strptime(data_input, "%d/%m/%Y")
        except ValueError:
            print("[!] Formato incorreto. Usando a data de hoje.")
            data_objeto = datetime.now()
    else:
        data_objeto = datetime.now()

    data_formatada_arquivo = data_objeto.strftime("%d_%m_%Y")
    data_formatada_json = data_objeto.strftime("%d/%m/%Y")
    
    # Nome padrão do arquivo HTML baseado no input
    nome_arquivo_html = f"{slug_titulo}-{data_formatada_arquivo}.html"

    resume = input("Breve resumo para o post:\n> ").strip()

    # 3. Selecionar Imagens Extras (Ícone e Banner)
    print(f"\n[Janela] Selecione a imagem para o ÍCONE...")
    icon_path = selecionar_arquivo("Selecione o ÍCONE do post", [("Imagens", "*.png *.jpg *.jpeg *.webp")])
    
    print(f"\n[Janela] Selecione a imagem para o BANNER...")
    banner_path = selecionar_arquivo("Selecione o BANNER do post", [("Imagens", "*.png *.jpg *.jpeg *.webp")])

    # Copiar e nomear ícone e banner se fornecidos
    if icon_path:
        shutil.copyfile(icon_path, IMAGES_DIR / f"{nome_arquivo_html}_icon.png")
    if banner_path:
        shutil.copyfile(banner_path, IMAGES_DIR / f"{slug_titulo}_banner.png")

    # 4. Processar imagens internas do Obsidian ![[...]]
    body_markdown = processar_imagens_obsidian(body_markdown, slug_titulo, md_path.parent)

    # 5. Converter Markdown para HTML
    html_body_conteudo = markdown.markdown(body_markdown, extensions=['fenced_code', 'codehilite'])
    html_completo = gerar_html_final(titulo, data_formatada_json, tags, html_body_conteudo, slug_titulo)

    # Salvar arquivo HTML final
    with open(POSTS_DIR / nome_arquivo_html, 'w', encoding='utf-8') as f:
        f.write(html_completo)
        
    # 6. Atualizar posts.json
    dados_post_json = {
        "icon_location": f"https://kallel181.github.io/Blog/static/images/{nome_arquivo_html}_icon.png",
        "file_location": f"https://kallel181.github.io/Blog/static/posts/{nome_arquivo_html}",
        "resume": resume,
        "name": titulo,
        "date": data_formatada_json,
        "tags": tags
    }
    
    atualizar_json_posts(dados_post_json)
    print(f"\n[Sucesso] Post '{titulo}' publicado com sucesso em {nome_arquivo_html}!")

if __name__ == "__main__":
    main()