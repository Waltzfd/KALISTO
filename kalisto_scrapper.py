from selenium import webdriver  # importa o Selenium, que controla o navegador
import time  # usado para pausas (time.sleep)
from selenium.webdriver.common.by import By  # define os tipos de seletor (XPATH, CLASS_NAME etc.)
from selenium.webdriver.support.ui import WebDriverWait  # permite esperar até uma condição ser satisfeita
from selenium.webdriver.support import expected_conditions as EC  # FALTOU ESSA IMPORTAÇÃO
from selenium.common.exceptions import NoSuchElementException  # exceção lançada quando um elemento não é encontrado
import re          # biblioteca de expressões regulares, usada pra extrair números de dentro de um texto
import pandas as pd  # usada para montar a tabela e gerar os arquivos CSV/Excel
import os          # biblioteca para trabalhar com caminhos de arquivos/pastas do sistema

# Abrir Navegador
navegador = webdriver.Chrome()
navegador.get('https://books.toscrape.com')

# Maximizar a tela
navegador.maximize_window()

# Para iniciar a contagem de página
pagina_num = 1

# Lista vazia que vai guardar um dicionário {Título, Preço, Estoque} para cada livro coletado
livros_coletados = []

# Loop externo: repete o processo inteiro enquanto houver uma próxima página de listagem
while True:
    print(f"\n -----  Página {pagina_num}  -----")

    # Encontra a lista inicial apenas para saber a quantidade
    clicar = navegador.find_elements(By.XPATH, "//h3/a[@title]")
    quantidade_cliques = len(clicar)

    print(f"Encontrados {quantidade_cliques} para clicar")

    # O loop FOR precisa abraçar todo o processo de clique, espera e retorno
    for i in range(quantidade_cliques):
        # 1. Atualiza a lista de elementos para evitar o erro de elemento antigo (Stale)
        clique_atualizado = navegador.find_elements(By.XPATH, "//h3/a[@title]")
        item_atual = clique_atualizado[i]

        texto_titulo = item_atual.get_attribute("title")
        print(f"Clicando na página: {texto_titulo}")

        # 2. Clica no livro atual
        item_atual.click()

        # 3. Espera a página do livro carregar de fato, aguardando o elemento de PREÇO
        # (não usamos "//h1" sozinho, pois esse mesmo tag também existe na página de listagem
        # — isso fazia o código achar que já tinha navegado antes da hora, causando erro
        # "NoSuchElementException" ao tentar ler o preço. Esperar o próprio preço resolve isso)
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, "//p[@class='price_color']"))
        )

        # Pega o elemento <p class="price_color"> que contém o preço, ex: "£51.77"
        preco_texto = navegador.find_element(By.XPATH, "//p[@class='price_color']").text

        # Remove tudo que NÃO é dígito (0-9) nem ponto do texto do preço
        # "£51.77" -> sobra só "51.77" -> convertido pra número decimal (float)
        preco = float(re.sub(r"[^\d.]", "", preco_texto))

        # Pega o elemento que contém a disponibilidade em estoque, ex: "In stock (22 available)"
        estoque_texto = navegador.find_element(By.XPATH, "//p[contains(@class,'availability')]").text

        # Procura no texto o padrão "(número available)" e captura só o número
        # \( e \) = parênteses literais | (\d+) = captura um ou mais dígitos | \s+ = espaço(s)
        match_estoque = re.search(r"\((\d+)\s+available\)", estoque_texto)

        # Se encontrou o padrão, converte o número capturado pra inteiro; senão, assume 0 por segurança
        estoque = int(match_estoque.group(1)) if match_estoque else 0

        # Mostra no console o que foi capturado, útil pra acompanhar/depurar
        print(f"  Preço: £{preco} | Estoque: {estoque}")

        # Adiciona um dicionário na lista, com os 3 dados desse livro (título, preço e estoque)
        livros_coletados.append({
            "Título": texto_titulo,
            "Preço (£)": preco,
            "Estoque": estoque
        })

        # Pausa opcional de 2 segundos para você ver a página do livro aberta
        time.sleep(2)

        # 4. Volta para a página principal (Precisa dos parênteses do método: .back())
        navegador.back()

        # 5. Espera a página principal carregar os links de novo antes de ir para o próximo loop
        WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3/a[@title]"))
        )

    # Depois de clicar em TODOS os livros da página atual, tenta ir pra próxima página
    try:
        # Procura o link "next" que só existe se houver mais páginas de listagem
        botao_passar = navegador.find_element(By.XPATH, "//li[@class='next']/a")
        botao_passar.click()

        # Espera os livros da nova página carregarem antes de continuar o loop
        WebDriverWait(navegador, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//h3/a[@title]"))
        )
        pagina_num += 1

    except NoSuchElementException:
        # Se o botão "next" não existe, significa que chegamos na última página
        print("\n última pagina alcançada.")
        break

print("Processo finalizado!")
print(f"Total de livros coletados: {len(livros_coletados)}")

# Encerra o navegador
navegador.quit()

# ----- Geração dos arquivos CSV e Excel -----

# Transforma a lista de dicionários numa tabela (DataFrame do pandas)
# cada chave do dicionário ("Título", "Preço (£)", "Estoque") vira uma coluna automaticamente
df = pd.DataFrame(livros_coletados)

# Descobre a pasta pessoal do usuário logado no Windows
# os.path.expanduser("~") retorna algo como "C:\Users\claudio.mota"
pasta_usuario = os.path.expanduser("~")

# Junta a pasta pessoal com "Documents" e depois com "resultados"
# formando o caminho completo: C:\Users\claudio.mota\Documents\resultados
pasta_destino = os.path.join(pasta_usuario, "Documents", "resultados")

# Cria a pasta "resultados" dentro de Documents, se ela ainda não existir
# exist_ok=True evita erro caso a pasta já exista (o comando simplesmente não faz nada nesse caso)
os.makedirs(pasta_destino, exist_ok=True)

# Junta a pasta de destino com o nome de cada arquivo, montando o caminho completo
# os.path.join é preferível a concatenar strings manualmente, pois ele já usa
# a barra correta do sistema operacional (\ no Windows, / no Linux/Mac)
caminho_csv = os.path.join(pasta_destino, "livros.csv")
caminho_xlsx = os.path.join(pasta_destino, "livros.xlsx")

# Salva a tabela em CSV, dentro da pasta "resultados" em Documents
# utf-8-sig evita bug de acentuação ao abrir o arquivo no Excel
df.to_csv(caminho_csv, index=False, encoding="utf-8-sig")

# Salva a mesma tabela em formato Excel (.xlsx), também dentro da pasta "resultados"
df.to_excel(caminho_xlsx, index=False)

# Confirma no console, com o caminho exato, onde os arquivos foram parar
print(f"Arquivos salvos em: {pasta_destino}")