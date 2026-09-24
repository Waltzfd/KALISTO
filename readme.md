# 📚 Kalisto Scrapper

Web scraper feito com **Selenium** e **Python** que coleta dados de livros do site [Books to Scrape](https://books.toscrape.com) — um site público criado especificamente para prática de scraping.

## 🔍 O que o script faz

1. Abre o navegador Chrome e acessa o site.
2. Percorre todas as páginas de listagem de livros.
3. Para cada livro, clica no item, espera a página carregar e coleta:
   - **Título**
   - **Preço** (em libras, £)
   - **Estoque disponível**
4. Volta para a listagem e repete o processo até esgotar os livros da página.
5. Avança automaticamente para a próxima página até não haver mais.
6. Ao final, salva todos os dados coletados em dois formatos:
   - `livros.csv`
   - `livros.xlsx`

Os arquivos são salvos em `Documentos/resultados` na pasta do usuário logado no sistema.

## ⏱️ Medição de tempo (timer)

O script marca o instante em que começa a processar cada página (`inicio_pagina`) e, após percorrer **todos** os livros dela, calcula e exibe no console o tempo total gasto:

```
Tempo gasto na pagina (1): 12.45 segundos
```

## 🛠️ Tecnologias utilizadas

- **Selenium** — automação do navegador
- **Pandas** — organização dos dados em tabela e exportação para CSV/Excel
- **re (Regex)** — extração de números de preço e estoque a partir do texto bruto da página
- **os** — manipulação de caminhos de arquivos multiplataforma
- **time** — medição do tempo de execução por página

## 📦 Pré-requisitos

- Python 3.8+
- Google Chrome instalado
- Bibliotecas Python:

```bash
pip install selenium pandas openpyxl
```

> O ChromeDriver é gerenciado automaticamente pelo Selenium Manager nas versões mais recentes do Selenium (4.6+). Se estiver usando uma versão mais antiga, será necessário baixar o [ChromeDriver](https://chromedriver.chromium.org/) manualmente e garantir que ele esteja no PATH do sistema.

## ▶️ Como executar

```bash
python kalisto_scrapper.py
```

O navegador abrirá automaticamente, percorrerá todas as páginas do site e, ao final, os arquivos `livros.csv` e `livros.xlsx` estarão disponíveis em:

```
C:\Users\<seu_usuario>\Documents\resultados\
```

## 📊 Estrutura dos dados coletados

| Título | Preço (£) | Estoque |
|--------|-----------|---------|
| Nome do livro | 51.77 | 22 |

## 💡 Pontos de destaque no código

- Uso de `WebDriverWait` + `expected_conditions` para evitar falhas por carregamento assíncrono da página (em vez de `time.sleep` fixo, que é menos confiável).
- Recaptura dos elementos a cada iteração do loop (`find_elements` dentro do `for`) para evitar o erro `StaleElementReferenceException`, comum quando o DOM muda após navegação.
- Uso de expressões regulares para limpar e converter texto bruto (preço e estoque) em tipos numéricos utilizáveis.
- Tratamento de exceção (`NoSuchElementException`) para detectar automaticamente o fim da paginação.
- Medição de tempo por página com o módulo `time`, útil para acompanhar performance da coleta.

## 📝 Licença

Projeto para fins de estudo e prática de web scraping.