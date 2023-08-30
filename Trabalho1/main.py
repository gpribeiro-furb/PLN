# Gabriel Panca Ribeiro, Gabriel Mori, Larson Kremer

import requests
import json
from bs4 import BeautifulSoup


# Função para formatar a data da matéria
def formatarData(string):
    start_index = string.find("-")
    end_index = string.find("-", start_index + 1)
    return string[:end_index]


# Função para remover espaço no final da string
def removerEspacoFinal(string):
    if string[-1] == " ":
        return string[:-1]
    else:
        return string


def criarJsonAtualizado():
    # Inicia lista de atributos
    titles = []
    texts = []
    dates = []

    # Loop de 3 páginas que serão percorridas
    for pagina in range(1, 4):
        # Montagem da URL
        url = "https://www.nsctotal.com.br/ultimas-noticias/page/" + str(pagina)

        # Usando a response no BeautifulSoup para começar a pesquisar as informações
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Percorrendo por todas as matérias, em que estão em painéis "h3" com a class de "title"
        for h3 in soup.find_all("h3", class_="title"):
            if h3.find("a"):
                # Pegando a URL da matéria
                urlMateria = h3.find("a").attrs['href']

                # Acessando a matéria para pegar mais informações, e usando o BeautifulSoup novamente
                responseMateria = requests.get(urlMateria)
                soupMateria = BeautifulSoup(responseMateria.content, "html.parser")

                # Buscando as informações da matéria
                textoMateria = soupMateria.find("div", id="post-content").find("p")
                dataMateria = soupMateria.find("p", class_="date mb-3").text
                dataMateria = removerEspacoFinal(formatarData(dataMateria)).replace("\n", "")

                # Preenchendo as listas
                texts.append(textoMateria.text)
                title = h3.find("a").text.replace("\n", "")
                titles.append(removerEspacoFinal(title))
                dates.append(dataMateria)

    # Juntando as informações em uma lista de objetos
    materias = []
    for i in range(len(titles)):
        materia = {
            "titulo": titles[i],
            "data": dates[i],
            "descricao": texts[i]
        }
        materias.append(materia)

    # Criando o JSON para exportar
    materiasJson = json.dumps(materias)
    print(materiasJson)

    # Abrindo e escrevendo o arquivo JSON
    with open("materias.json", "w") as f:
        json.dump(materias, f)


def carregaJson(path="materias.json"):
    with open(path, 'r') as file:
        return json.load(file)

def carregaStopwords():
    # Open the file for reading
    with open('stopwords.txt', 'r') as file:
        # Read the content of the file
        content = file.read()

    # Split the content into words using newline characters as separators
    words = content.split('\n')

    # Remove any empty strings resulting from trailing newline
    words = [word for word in words if word]

    return words

# TO-DO: ler json
materias = carregaJson()
stopwords = carregaStopwords()
print(materias)

# TO-DO: Remover stopwords to texto

for materia in materias:
    for word in stopwords:
        materia["descricao"].replace(word, "")

print(materias)
# TO-DO: Aplicar STEM, aka fazer com que as palavras fiquem iguais (drogas, drogado, drogaria)

# TO-DO: Criar vocabulário, aka selecionar palavras e categorias para categorizar o banco de palavras

