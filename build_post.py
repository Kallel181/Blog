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

POSTS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

EXTENSOES_VIDEO = {'.mp4', '.webm', '.ogg'}

def selecionar_arquivo(titulo, tipos_arquivos, diretorio_inicial=None):
    """Abre uma caixa de diálogo do sistema para escolher arquivos."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    caminho = filedialog.askopenfilename(
        title=titulo, 
        filetypes=tipos_arquivos, 
        initialdir=diretorio_inicial
    )
    return Path(caminho) if caminho else None

def selecionar_pasta(titulo, diretorio_inicial=None):
    """Abre uma caixa de diálogo para escolher um diretório."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    caminho = filedialog.askdirectory(
        title=titulo,
        initialdir=diretorio_inicial
    )
    return Path(caminho) if caminho else None

def slugify(text):
    """Transforma 'Título do Post!' em 'titulo_do_post'."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s-]+', '_', text).strip('_')

def processar_midia_obsidian(body_text, slug_titulo, md_dir, imagens_dir=None, videos_dir=None):
    """Procura mídias ![[arquivo]] ou ![](arquivo), copia para static/images e gera HTML apropriado."""
    count = 1
    padrao_midia = r'!\[\[([^\]]+)\]\]|!\[(.*?)\]\(([^)]+)\)'

    def substituir(match):
        nonlocal count
        if match.group(1):
            nome_original = match.group(1).strip()
        else:
            nome_original = match.group(3).strip()

        extensao = Path(nome_original).suffix.lower() or ".png"
        novo_nome_midia = f"{slug_titulo}_{count}{extensao}"
        dst_path = IMAGES_DIR / novo_nome_midia

        # Define as rotas de busca
        is_video = extensao in EXTENSOES_VIDEO
        src_path_md = md_dir / nome_original
        src_path_img = (imagens_dir / nome_original) if imagens_dir else None
        src_path_video = (videos_dir / nome_original) if videos_dir else None

        # 1. Se for vídeo, procura primeiro na pasta de vídeos
        if is_video and src_path_video and src_path_video.exists():
            shutil.copyfile(src_path_video, dst_path)
            print(f"-> Vídeo copiado da pasta de vídeos: {novo_nome_midia}")
        # 2. Se for imagem, procura primeiro na pasta de imagens
        elif not is_video and src_path_img and src_path_img.exists():
            shutil.copyfile(src_path_img, dst_path)
            print(f"-> Imagem copiada da pasta de imagens: {novo_nome_midia}")
        # 3. Tenta na mesma pasta do Markdown
        elif src_path_md.exists():
            shutil.copyfile(src_path_md, dst_path)
            print(f"-> Mídia copiada do diretório do Markdown: {novo_nome_midia}")
        # 4. Seleção manual via Tkinter
        else:
            dir_busca = videos_dir if is_video else (imagens_dir or md_dir)
            print(f"[!] Mídia não encontrada automaticamente: '{nome_original}'")
            print(f"[Janela] Por favor, localize o arquivo correspondente...")

            caminho_manual = selecionar_arquivo(
                f"Localize a mídia: {nome_original}",
                [("Mídias (Imagens/Vídeos)", "*.png *.jpg *.jpeg *.webp *.gif *.mp4 *.webm *.ogg")],
                diretorio_inicial=dir_busca
            )

            if caminho_manual and caminho_manual.exists():
                shutil.copyfile(caminho_manual, dst_path)
                print(f"-> Mídia manual copiada: {novo_nome_midia}")
            else:
                print(f"[X] Erro: Mídia '{nome_original}' ignorada.")
                count += 1
                return ''

        count += 1
        url_midia = f"https://kallel181.github.io/Blog/static/images/{novo_nome_midia}"

        if is_video:
            return f'<video controls width="100%"><source src="{url_midia}" type="video/{extensao.replace(".", "")}">Seu navegador não suporta a tag de vídeo.</video>'
        else:
            return f'<img src="{url_midia}" alt="{nome_original}"/>'

    return re.sub(padrao_midia, substituir, body_text)

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
    """Gera a estrutura HTML do post."""
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

  <script>
    window.MathJax = {{
      tex: {{
        inlineMath: [['$', '$']],
        displayMath: [['$$', '$$']],
        processEscapes: true
      }}
    }};
  </script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
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

    # 2. Selecionar Pasta de IMAGENS do Obsidian
    print("\n[Janela] Selecione a pasta de IMAGENS (Attachments) do Obsidian...")
    imagens_dir = selecionar_pasta("Selecione a pasta de IMAGENS", diretorio_inicial=md_path.parent)

    # 3. Selecionar Pasta de VÍDEOS do Obsidian
    print("\n[Janela] Selecione a pasta de VÍDEOS do Obsidian...")
    videos_dir = selecionar_pasta("Selecione a pasta de VÍDEOS", diretorio_inicial=md_path.parent)

    with open(md_path, 'r', encoding='utf-8') as f:
        body_markdown = f.read()

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

    nome_arquivo_html = f"{slug_titulo}-{data_formatada_arquivo}.html"

    resume = input("Breve resumo para o post:\n> ").strip()

    print(f"\n[Janela] Selecione a imagem para o ÍCONE...")
    icon_path = selecionar_arquivo("Selecione o ÍCONE do post", [("Imagens", "*.png *.jpg *.jpeg *.webp")], diretorio_inicial=imagens_dir)

    print(f"\n[Janela] Selecione a imagem para o BANNER...")
    banner_path = selecionar_arquivo("Selecione o BANNER do post", [("Imagens", "*.png *.jpg *.jpeg *.webp")], diretorio_inicial=imagens_dir)

    if icon_path:
        shutil.copyfile(icon_path, IMAGES_DIR / f"{nome_arquivo_html}_icon.png")
    if banner_path:
        shutil.copyfile(banner_path, IMAGES_DIR / f"{slug_titulo}_banner.png")

    # Processar mídias passando ambos os diretórios
    body_markdown = processar_midia_obsidian(body_markdown, slug_titulo, md_path.parent, imagens_dir, videos_dir)

    html_body_conteudo = markdown.markdown(body_markdown, extensions=['fenced_code', 'codehilite'])
    html_completo = gerar_html_final(titulo, data_formatada_json, tags, html_body_conteudo, slug_titulo)

    with open(POSTS_DIR / nome_arquivo_html, 'w', encoding='utf-8') as f:
        f.write(html_completo)

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