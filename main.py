#Importar tudo o que é necessário
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import pandas as pd
import time
import unidecode
import requests
from bs4 import BeautifulSoup
import urllib3
import re
import numpy as np

#Lista de Empresas a Extrair
#No futuro fazer Webscrap de Site com Lista
nome_do_csv = input("Escreva o nome do ficheiro .csv com nome de empresas na primeira coluna - ")

#É preciso alterar o local da pasta, este é adaptado ao meu pc
bd_conecta = pd.read_csv(f"~/Documents/Conecta_PME_40/WebScrap_CSV/{nome_do_csv}.csv")

bd_conecta

empresas = []

for x in bd_conecta["empresa"]:

  #Arranjar texto de pesquisa
  x = x.lower()

  #Criar Lista
  empresas.append(x)

print(empresas)

#Setup Chromium-Browser on Linux


browser = webdriver.Firefox()

tempo = 1.5

codigo_data = []
codigo_titulos = []
lista_empresas_c = []
lista_empresas_r = []
title_rigor = []
data_rigor = []

empresa_extraida = 0

start = time.time()

for empresa in empresas:

    print(empresa)

    # Pesquisar empresa no Código Postal

    browser.get("https://codigopostal.ciberforma.pt/")

    search = browser.find_element_by_id("autocomplete-ajax")
    search.send_keys(empresa)
    search.send_keys(Keys.RETURN)

    time.sleep(tempo)

    # Página de Pesquisa

    content = browser.page_source

    soup = BeautifulSoup(content)

    # Procurar Erro
    empresa_search = soup.find("div", attrs={"class": "gs-snippet"})

    # Procurar Pesquisa com Sucesso
    pesquisa = soup.find("a", attrs={"class": "gs-title"}, href=True)

    # Se existir empresa em BD
    if pesquisa is not None:

        try:

            pesquisa_link = pesquisa["href"]

            # Entrar na página da empresa dentro do Código Postal

            site = requests.get(pesquisa_link)

            site = site.content.decode('ISO-8859-1')

            soup = BeautifulSoup(site)

            print(f"Entramos na página de {empresa} dentro do 'Código Postal'")

            time.sleep(tempo)

            # A escavação do código HTML

            body = soup.find("body")

            procura_ = body.find("div", {"id": "wrapper"})

            procura_ = procura_.find("div", {"class": "main-container"})

            procura_ = procura_.find_all("div", {"class": "container"})

            procura_ = procura_[1].find("div", {"class": "row"})

            procura_ = procura_.find("div", {"class": "col-sm-9 page-content col-thin-right"})

            procura_ = procura_.find("div", {"class": "inner inner-box ads-details-wrapper"})

            procura_ = procura_.find("div", {"class": "Ads-Details"})

            procura_ = procura_.find("div", {"class": "row"})

            procura_ = procura_.find("div", {"class": "ads-details-info col-md-8"})

            pesquisa_1 = procura_.find_all("h4")

            # A dita cuja extração

            for a in pesquisa_1:

                b = a.find("span")

                if b == None:

                    codigo_titulos.append("Morada")
                    codigo_data.append(a.text)
                    lista_empresas_c.append(empresa)


                elif b is not None:
                    codigo_titulos.append(a.text)
                    b = b.text
                    codigo_data.append(b)
                    lista_empresas_c.append(empresa)

                codigo_titulos = [c.split(":")[0] for c in codigo_titulos]

            print(f"Foi extraída informação de {empresa} em 'Código Postal'")

        except:
            print(f"Info de {empresa} em 'Código Postal' foi ignorada")
            pass


    # Se não estiver na BD
    else:
            print(f"Não há informação de {empresa} no site 'Código Postal'")
            pass

    # Criação de link e Abertura de Página Rigozbiz

    # Criar Link
    linke = empresa.split()
    linke = '+'.join(linke)
    linke = unidecode.unidecode(linke)

    # Entrar na página de pesquisa
    linke = f"?query={linke}&situacao=0"
    link = f"https://www.rigorbiz.pt/procurar-empresas/{linke}"
    browser.get(link)
    time.sleep(tempo)

    # Estudar a Página de Pesquisa
    content = browser.page_source
    soup = BeautifulSoup(content)

    try:

        empresa_search = soup.find("h3", {"class": "name"})

        a = empresa_search.find("a", href=True)

        if a is not None:

            titles_rigor = []
            datas_rigor = []
            listas_empresas_r = []

            url_empresa = a["href"]

            url_empresa = f"https://www.rigorbiz.pt{url_empresa}"

            # Entrar da página da empresa dentro da Rigorbiz

            browser.get(url_empresa)

            print(f"Entramos na página de {empresa} dentro de 'Rigorbiz'")

            time.sleep(tempo)

            content = browser.page_source
            soup = BeautifulSoup(content)

            # Titulos
            scrap2 = soup.find_all("div", {"class": 'entity-attributes-title'})
            for a in scrap2:
                a = a.text
                titles_rigor.append(a)
                listas_empresas_r.append(empresa)

            # Dados
            scrap = soup.find_all("div", {"class": 'entity-attributes-data'})
            for a in scrap:
                a = a.text
                datas_rigor.append(a)

            # Arranjar Tabelas

            del datas_rigor[2]
            del datas_rigor[3:7]
            datas_rigor[4] = str(datas_rigor[4]).replace("\n", " ")
            data_rigor.extend(datas_rigor)

            del titles_rigor[2]
            del titles_rigor[3:7]
            title_rigor.extend(titles_rigor)

            del listas_empresas_r[2]
            del listas_empresas_r[3:7]
            lista_empresas_r.extend(listas_empresas_r)

            print(f"Foi extraída informação de {empresa} em 'Rigorbiz'")

        else:
            pass

    except:
        print(f"Info de {empresa} em 'Rigorbiz' foi ignorada")
        pass


    pausa = time.time()

    empresa_extraida = empresa_extraida + 1

    print(
        f"Número de Extrações = {empresa_extraida}. Última empresa = {empresa}. Tempo até agora = {round((pausa - start) / 60, 2)} minutos.")

end = time.time()

print(
    f"Fim do Programa. Número de Extrações Realizadas = {empresa_extraida} com uma duração de {round(((end - start) / 60) / 60, 2)} horas")


print(f"tamanho lista_empresas_c = {len(lista_empresas_c)}")
print(f"tamanho codigo_titulos = {len(codigo_titulos)}")
print(f"tamanho codigo_data = {len(codigo_data)}")

print(f"tamanho lista_empresas_r = {len(lista_empresas_r)}")
print(f"tamanho title_rigor = {len(title_rigor)}")
print(f"tamanho data_rigor = {len(data_rigor)}")

#Criar DataFrames
df = pd.DataFrame(data = list(zip(lista_empresas_c, codigo_titulos, codigo_data)))
df.columns = ["empresa", "tipo_de_dado", "dado"]

df1 = pd.DataFrame(data = list(zip(lista_empresas_r, title_rigor, data_rigor)))
df1.columns = ["empresa", "tipo_de_dado", "dado"]

#Eliminar Info a mais DataFrames
df = df[df.tipo_de_dado != "Morada"]

#Juntar DataFrames dos dos sites
df2 = df.append(df1)

#Eliminar mais Info a mais
df2.drop_duplicates(subset=['tipo_de_dado'])

#Copiar porque posso
df3 = df2

#Arranjar tudo como deve ser
df3 = df3.pivot(index="empresa", columns = "tipo_de_dado")
df3 = df3.replace(np.nan, '', regex=True)

#Index de colunas corrigido
df3.columns = df3.columns.get_level_values(1)

#Arranjar CAE's
new = df3["CAE"].str.split("-", n = 1, expand = True)
df3["CAE Número"] = new[0]
df3["CAE Informação"] = new[1]
df3.drop(columns =["CAE"], inplace = True)

#Copiar outra vez porque posso
df4 = df3
novo = df4["Endereço"].str.split('([0-9]{4} - [0-9]{3})', expand = True)
df4["Rua"] = novo [0]
df4["Localidade"] = novo[2]
df4["Código Postal"] = df3["Endereço"].str.extract(r'([0-9]{4} - [0-9]{3})')
df4.reset_index(level="empresa", inplace=True)


df4.to_csv(f"~/Documents/Conecta_PME_40/WebScrap_CSV/Extracoes/{nome_do_csv}_EXTRAIDO.csv", sep = ",", index = False, header = True)