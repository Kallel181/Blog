from md_to_html import *
import sys
from datetime import datetime
import json


def write_json(new_data, filename='../static/posts.json'):
  with open(filename,'r+') as file:
    file_data = json.load(file)
    file_data["posts"].insert(0,new_data)

    file.seek(0)
    json.dump(file_data, file, indent = 4)


if __name__ == "__main__":
  print("Postando novo post")

  md_file_path = input("Insira o Diretório para o arquivo .md: ")
  md_file_path = md_file_path.replace("\\","/")
  
  md_file_images_path = input("Insira o Diretório para as imagens do arquivo md: ")
  md_file_images_path = md_file_images_path.replace("\\","/")
  
  html = gerar_html_template(md_file_path,md_file_images_path)
    
  with open(md_file_path, 'r', encoding='utf-8') as f:
    md = f.read()
  meta = extrair_metadados(md)

  file_path = "../static/posts/"
  file_name = meta[0].get('title').replace(" ","_")+"-"+meta[0].get('date').strftime("%d_%m_%Y")+".html"

  with open(file_path+file_name, 'w', encoding='utf-8') as f:
    f.write(html)

  print(f"{file_name} gerado com sucesso")

  resume = input("Resumo do post: ")

  post={
    'icon_location': "https://kallel181.github.io/Blog/static/images/"+file_name+"_icon.png",
    'file_location': "https://kallel181.github.io/Blog/static/posts/"+file_name,
    'resume': resume,
    'name': meta[0].get('title'),
    'date': meta[0].get('date').strftime("%d/%m/%Y"),
    'tags': meta[0].get('tags')
  }

  write_json(post)

  print("Adicione o arquivo: ")
  print("/static/images/"+file_name+"_icon.png")
  print("/static/images/"+file_name+"_banner.png")



