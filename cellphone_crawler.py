import re
import  threading


import requests
from bs4 import BeautifulSoup


URL = "https://django-anuncios.solyd.com.br"
URL_AUTO = (URL+'/automoveis')
LINKS = []
TELEFONES = []


def requisicao(url):
    try:
        resposta = requests.get("{}".format(url))
        if resposta.status_code != 200:
            print("Status Code:",resposta.status_code)
        elif resposta.status_code == 200:
            return resposta.text
        else:
            print("Erro ao requisitar")
    except Exception as error:
        print("Não foi possível requisitar página")
        print(error)


def parsing_html(resposta_html):
    try:
        soup = BeautifulSoup(resposta_html, 'html.parser')
        return soup
    except Exception as error:
        print("erro ao fazer o parsing")
        print(error)
    pass


def encontrar_links(soup):
    try:
        cards_pai = soup.find("div", class_="ui three doubling link cards")
        cards = cards_pai.find_all("a")
    except:
        print("erro ao encontrar links")
        return None
    links = []
    for card in cards:
        try:
            link = card['href']
            links.append(link)
        except:
            pass
    return links


def encontrar_telefones(soup):
    try:
        descricao = soup.find_all("div", class_="sixteen wide column")[2].p.get_text().strip()
    except:
        print("erro ao encontrar descrição")
        return None

    regex = re.findall(r"\(?0?([1-9]{2}) ?[ \-\.\)]{0,2}(9[ \.]?\d{4})[ \-\.]?(\d{4})", descricao)
    if regex:
        return regex


def descobrir_telefones():
    while True:
        try:    
            link_anuncio = LINKS.pop(0)
        except:
            break

        resposta_anuncio = requisicao(URL+link_anuncio)
        
        if resposta_anuncio:
            soup_anuncio = parsing_html(resposta_anuncio)
            if soup_anuncio:
                telefones = encontrar_telefones(soup_anuncio)
                if telefones:
                    for telefone in telefones:
                        TELEFONES.append(telefone)
                        salvar_telefones(telefone)


def salvar_telefones(telefone):
    telefone_str = "{}{}{}\n".format(telefone[0],telefone[1],telefone[2])
    try:
        with open("telefones.csv","a") as arquivo:
            arquivo.write(telefone_str)
    except:
        print("erro ao salvar o arquivo")


if __name__=="__main__":
    resposta_busca = requisicao(URL_AUTO)
    if resposta_busca:
        soup_busca = parsing_html(resposta_busca)
        if soup_busca:
            LINKS = encontrar_links(soup_busca)

            THREADS = []
            for i in range (5):
                t = threading.Thread(target=descobrir_telefones)
                THREADS.append(t)

            for t in THREADS:
                t.start()

            for t in THREADS:
                t.join()        