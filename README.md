# Blog Pessoal - Programação, Matemática e Cibersegurança

Este é o repositório do meu blog pessoal, onde compartilho conteúdos relacionados a **programação**, **matemática**, **cibersegurança**, **CTFs (Hack The Box)**, e muito mais. O site é totalmente estático, feito com **HTML, CSS e JavaScript puro**, e hospedado gratuitamente no GitHub Pages.

---

## 📁 Estrutura do Projeto

```
.
├── static/
│ ├── images/ # Imagens ilustrativas dos posts
│ ├── posts/ # Arquivos HTML dos posts
│ ├── js/ # Scripts principais
│ ├── css/ # Estilos do site
│ └── posts.json # Lista com metadados dos posts
├── index.html # Página inicial com lista de posts
└── README.md # Este arquivo
```

---

## 📝 Formato do `posts.json`

Os metadados dos posts ficam no arquivo `static/posts.json`. Exemplo:

```json
{
  "posts": [
    {
      "icon_location": "/static/images/HTB_IClean_Guide_icon.png",
      "file_location": "/static/posts/HTB_IClean_Guide-10_05_2024.html",
      "name": "HTB IClean Guide",
      "date": "10/05/2024",
      "tags": ["HTB", "XSS", "SSTI"]
    }
  ]
}
```
