# Gabriel Panca Ribeiro, Gabriel Mori, Larson Kremer

import requests
import json
import nltk
from bs4 import BeautifulSoup
from nltk.stem import RSLPStemmer


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

# Função para buscar matérias das 3 primeiras páginas do NSC Total e gerar o "materias.json"
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
    print("JSON exportado para o arquivo 'materias.json' : ")
    print(materiasJson)

    # Abrindo e escrevendo o arquivo JSON
    with open("materias.json", "w") as f:
        json.dump(materias, f)


# Função para carregar o arquvo json de materias
def carregaJson(path="materias.json"):
    with open(path, 'r') as file:
        return json.load(file)

# Função para carregar as stopwords do arquivo stopwords.txt
def carregaStopwords():
    # Ler o arquivo
    with open('stopwords.txt', 'r', encoding='utf-8') as file:
        content = file.read()

    # Separar as palavras por linha nova
    words = content.split('\n')

    # Remover os espaços em branco
    words = [word for word in words if word]
    temp = []
    for word in words:
        word = word.replace(" ","")
        temp.append(word)
    words = temp

    return words

# Função para aplicar o Stemming em uma lista de palavras
def aplicarStem(listaPalavras):
    stemmer = RSLPStemmer()

    temp = []
    for palavra in listaPalavras:
        temp.append(stemmer.stem(palavra))
    return temp

# Função para remover as stopwords
def removerStopwords(materias):
    for materia in materias:
        materia["descricao"] = nltk.word_tokenize(materia["descricao"])
        # Cria uma tabela de tradução que remove símbolos
        translator = str.maketrans('', '', "“”!@#$%^&*()_+=[]{};:'\"<>,.?/~\\|")
        novaDescricao = []
        for palavra in materia["descricao"]:
            palavra = palavra.translate(translator)
            novaDescricao.append(palavra.lower())

        novaDescricao = [word for word in novaDescricao if word]
        materia["descricao"] = [word for word in novaDescricao if word.lower() not in stopwords]

# Função para carregar o vocabulário com base nas categorias de classificação informadas
def carregarVocabulario(categorias):
    for categoria in categorias:
        # Ler o arquivo
        with open(categoria+'.txt', 'r', encoding='utf-8') as file:
            content = file.read()

        # Separar as palavras por linha nova
        words = content.split('\n')

        # Remove espaços em branco
        words = [word for word in words if word]
        temp = []
        for word in words:
            word = word.replace(" ", "")
            temp.append(word)
        words = temp
        # Aplica o stemming nas palavras
        words = aplicarStem(words)
        # Adiciona as palavras tratadas em uma lista de vocabulários para ser usada na categorização
        vocabularios.append(words)

# Função para categorias as materias
def categorizarMaterias(materias):
    for materia in materias:
        # Preparando as listas de categorias e de similaridades
        categorias = []
        materia["matches"] = []
        for vocabulario in vocabularios:
            categorias.append(0)

        # Contar a quantidade de palavras iguais
        for palavra in materia["descricao"]:
            index = 0
            for vocabulario in vocabularios:
                if(palavra in vocabulario):
                    categorias[index] = categorias[index] + 1
                    materia["matches"].append(palavra)
                index = index + 1

        # Categorizar as materias com base nas similaridades
        qntdCategoriaMaisRelacionada = max(categorias)
        indexCategoriaMaisRelacionada = 0 if qntdCategoriaMaisRelacionada == 0 else categorias.index(qntdCategoriaMaisRelacionada)
        materia["categoria"] = categorias[indexCategoriaMaisRelacionada]


# criarJsonAtualizado()
materias = carregaJson()
stopwords = carregaStopwords()

# nltk.download('rslp')
# nltk.download('punkt')

# TO-DO: Remover stopwords to texto
removerStopwords(materias)

# TO-DO: Aplicar STEM, aka fazer com que as palavras fiquem iguais (drogas, drogado, drogaria)
for materia in materias:
    materia["descricao"] = aplicarStem(materia["descricao"])

# TO-DO: Criar vocabulário, aka selecionar palavras e categorias para categorizar o banco de palavras
categorias = ["outros", "economia", "saude", "turismo", "esporte", "desastre"]
vocabularios = []
carregarVocabulario(categorias)


categorizarMaterias(materias)

print("Exportando matérias categorizadas para o arquivo 'resultado.json'")
with open("resultado.json", "w") as f:
    json.dump(materias, f)

print(vocabularios)
print(materias)



