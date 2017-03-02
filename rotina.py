#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import socket
import traceback
import sys
from StringIO import StringIO
from bs4 import BeautifulSoup
from cookielib import CookieJar
from gzip import GzipFile
from time import localtime
from time import time
from urllib import urlencode
from urllib2 import HTTPCookieProcessor
from urllib2 import HTTPError
from urllib2 import ProxyHandler
from urllib2 import Request
from urllib2 import build_opener
from pymongo import MongoClient
from time import gmtime, strftime

try:
    import cPickle as pickle
except ImportError:
    import pickle

"""
INICIALIZANDO VARIAVEIS GLOBAIS
"""
url_direct = {'pref-sp': 'http://capital.sp.gov.br/',
              'transp-cptm': "http://www.cptm.sp.gov.br/Pages/Home.aspx",
              'transp-metro': "http://www.metro.sp.gov.br/Sistemas/direto-do-metro-via4/diretodoMetroHome.aspx",
              'transito-agora': "http://cetsp1.cetsp.com.br/monitransmapa/agora/",
              'qualidade-oxigenio': "http://sistemasinter.cetesb.sp.gov.br/Ar/php/ar_resumo_hora.php",
              'dash-aero': "http://voos.infraero.gov.br/hstvoos/RelatorioPortal.aspx",
              'ex-clima': "http://www.cgesp.org/v3/previsao_prefeitura_xml.jsp",
              'dash-rodizio': "http://misc.prefeitura.sp.gov.br/pmspws/rotation/data.json",
              'dash-aero-situacao': "http://www.infraero.gov.br/situacaoaeroporto/",
              'ex-clima-media': "http://www.saisp.br/cgesp/temp_media_prefeitura_sp.jsp"}


"""
 A função principal executada é a main()
"""

"""
FUNCOES UTILIZADAS
"""
def getTempMedia():
    soup = BeautifulSoup(getContent(url_direct.get("ex-clima-media")))
    temp_media = float(soup.media.text)
    temperature = str(int(round(temp_media)))
    return temperature


def getUmidadeArMax():
    soup = BeautifulSoup(getContent(url_direct.get("ex-clima")))
    dia = soup.findAll('dia')
    umid_max = dia[0].parent.find('umid-max')
    return umid_max.string

def getUmidadeArMin():
    """
    return unit ar min
    """
    soup = BeautifulSoup(getContent(url_direct.get("ex-clima")))
    dia = soup.findAll('dia')
    umid_min = dia[0].parent.find('umid-min')
    return umid_min.string


def getHoraPorSol():
    """
    return sunset time
    """
    soup = BeautifulSoup(getContent(url_direct.get("ex-clima")))
    dia = soup.findAll('dia')
    sunset = dia[0].parent.find('sunset')
    return sunset.string


def getTempMaxima():
    """
    return time morning
    """
    soup = BeautifulSoup(getContent(url_direct.get("ex-clima")))
    dia = soup.findAll('dia')
    temp_max = dia[0].parent.find('temp-max')
    return temp_max.string


def getTempMinima():
    """
    return temperature minimo
    """
    soup = BeautifulSoup(getContent(url_direct.get("ex-clima")))
    dia = soup.findAll('dia')
    temp_min = dia[0].parent.find('temp-min')
    return temp_min.string

"""
def setWeatherSp(title=False):
    try:
        soup = BeautifulSoup(getContent(url_direct.get("ex-clima-media")))
        temp_media = setTempMedia()

        soup = BeautifulSoup(getContent(url_direct.get("ex-clima")))
        dia = soup.findAll('dia')
        prev_manha = dia[0].parent.find('ct', {'periodo': 'Manhã'})
        prev_tarde = dia[0].parent.find('ct', {'periodo': 'Tarde'})
        prev_noite = dia[0].parent.find('ct', {'periodo': 'Noite'})
        prev_madrugada = dia[0].parent.find('ct', {'periodo': 'Madrugada'})
        umidade_ar_max = getUmidadeArMax()
        umidade_ar_min = getUmidadeArMin()
        hora_nascer_sol = getHoraNascerSol()
        hora_por_sol = getHoraPorSol()
        temp_maxima = getTempMaxima()
        temp_minima = getTempMinima()
    except Exception as exc:
        print(exc)
"""

"""
QUADRO DE CLIMA
"""
def getWeatherCapa():
    weather = {}
    try:
        soup = BeautifulSoup(getContent(url_direct.get("ex-clima-media")))
        temp_media = getTempMedia()
        hour = localtime(time()).tm_hour
        soup = BeautifulSoup(getContent(url_direct.get("ex-clima")))
        dia = soup.findAll('dia')
        potencial = dia[0].parent.find('ct', {'periodo': getPeriod(hour)})
        weather['temp_media'] = temp_media
        weather['potencial'] = potencial['pt']
    except Exception as exc:
        print('ERRO NO CARREGAMENTO DE INFORMACOES ACERCA DO CLIMA')
        print(exc)
    return weather

def getPeriod(hour):
    if int(hour) >= 6 and int(hour) < 13:
        return 'Manhã'
    elif int(hour) >= 13 and int(hour) < 19:
        return 'Tarde'
    elif int(hour) >= 19 and int(hour) <= 23:
        return 'Noite'
    elif int(hour) >= 0 and int(hour) < 6:
        return 'Madrugada'

"""
INFORMACOES DE QUALIDADE DO AR
"""
def airQualityCapa():
    airQuality = {}
    try:
        soup = BeautifulSoup(getContent(url_direct.get('qualidade-oxigenio')))
        qualidade_ar = getDescQualidade()
        airQuality['qualidade_ar'] = qualidade_ar
    except Exception as e:
        print('ERRO NO CARREGAMENTO DE INFORMACOES DA QUALIDADE DO AR')
        print(e)
    return airQuality

def getDescQualidade(local='Congonhas'):
    """
    return type description qualidaty atmosfera
    """
    soup = BeautifulSoup(getContent(url_direct.get('qualidade-oxigenio')))
    quality = int(soup.find('td', text=local).parent.find('td', width=50).text)
    if quality >= 0 and quality <= 40:
        descript = 'Boa'
    elif quality >= 41 and quality <= 80:
        descript = 'Moderado'
    elif quality >= 81 and quality <= 120:
        descript = 'Ruim'
    elif quality >= 121 and quality <= 200:
        descript = 'Muito Ruim'
    elif quality >= 200:
        descript = 'Pessimo'
    return descript


"""
INFORMACOES DE AEROPORTOS
"""
def trafficCapa():
    traffic = {}
    try:
        soup = BeautifulSoup(getContent(url_direct.get('transito-agora')))
        total_km_lentidao = soup.find('div', {"id": 'lentidao'}).string
        result = getTrafficCount(total_km_lentidao)
        status_transito_sp = result[1]
        css = result[0]
        traffic['total_km_lentidao'] = total_km_lentidao
        traffic['status_transito_sp'] = status_transito_sp
        traffic['css'] = css
        
    except Exception as e:
        print('ERRO NO CARREGAMENTO DO PAINEL DE AEROPORTOS ')
        print(e)
    return traffic

def getTrafficCount(total_km_lentidao):
    traffic_count = []
    if int(total_km_lentidao) <= 45:
        status_transito_sp = 'livre'
        css = 'verde'
    elif int(total_km_lentidao) >= 45 and int(total_km_lentidao) <= 90:
        status_transito_sp = 'regular'
        css = 'amarelo'
    elif int(total_km_lentidao) > 90:
        css = 'vermelho'
        status_transito_sp = 'ruim'
    traffic_count.append(css)
    traffic_count.append(status_transito_sp)
    return traffic_count

"""
INFORMACOES DE RODIZIO
"""
def getRodizioCapa():
    rodizio = {}
    try:
        url_rodizio = url_direct.get('dash-rodizio')
        placas_final_url_return = urllib.urlopen(url_rodizio)
        data_result = json.loads(placas_final_url_return.read())
        placa = data_result['Rotation']['desc']
        rodizio['placa'] = placa
    except Exception as e:
        print('ERRO NO CARREGAMENTO DE INFORMACOES ACERCA DO RODIZIO')
        print(e)
    return rodizio



"""
  FUNÇÃO QUE IRÁ IMPLEMENTAR AS ATUALIZAÇÕES
"""

def main():
    print('')
    print('########### INICIANDO PROCESSO DE ATUALIZAÇÃO DO PAINEL DASHBOARD  #################')
    data_hora_atual = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print('########### DATA E HORA ATUAIS:  ' + data_hora_atual + ' ##############')
    mongo_client = MongoClient('mongodb://mongo0.prodam:27017')
    db = mongo_client.prodam
    dashboard = db.dashboard
    registro = dashboard.find_one()


    try:
        doc = {}

        # Clima
        try:
            weather = getWeatherCapa()
            doc['temp_media'] = weather['temp_media']
            doc['potencial'] = weather['potencial']
        except:
            print('PROBLEMAS NA RECUPERACAO DE INFORMACOES ACERCA DO CLIMA')
            doc['temp_media'] = registro['temp_media'] if registro else ''
            doc['potencial'] = registro['potencial'] if registro else ''

        # Qualidade do ar
        try:
            air = airQualityCapa()
            doc['qualidade_ar'] = air['qualidade_ar']
        except:
            print('PROBLEMAS NA RECUPERACAO DE INFORMACOES ACERCA DA QUALIDADE DO AR')
            doc['qualidade_ar'] = registro['qualidade_ar'] if registro else ''

        # Trafego
        try:
            traffic = trafficCapa()
            doc['total_km_lentidao'] = traffic['total_km_lentidao']
            doc['status_transito_sp'] = traffic['status_transito_sp']
            doc['traffic_css'] = traffic['css']
        except:
            print('PROBLEMAS NA RECUPERACAO DE INFORMACOES ACERCA DO TRAFEGO')
            doc['total_km_lentidao'] = registro['total_km_lentidao'] if registro else ''
            doc['status_transito_sp'] = registro['status_transito_sp'] if registro else ''
            doc['traffic_css'] = registro['traffic_css'] if registro else ''

        # Rodizio
        try:
            rodizio = getRodizioCapa()
            doc['placa'] = rodizio['placa']
        except:
            print('PROBLEMAS NA RECUPERACAO DE INFORMACOES ACERCA DO RODIZIO')
            doc['placa'] = registro['placa'] if registro else ''

        # EXCLUINDO REGISTRO PRÉ-EXISTENTE 
        if registro:
            print('')
            print('EXCLUINDO REGISTRO PRÉ-EXISTENTE')
            print(registro)
            dashboard.delete_one({})
        
        # TODO: Implementado  atualizacao do dashboard
        print('')
        print('DICIONÁRIO ATUALIZADO: ')
        print(doc)
        res = dashboard.insert_one(doc)
        print('')
        print('GERADO REGISTRO NA COLEÇÃO DE DASHBOARD')
        print(res.inserted_id)
    except:
        print('ERRO NA ATUALIZAÇÃO DOS REGISTROS')

    print('')
    print('########### FIM PROCESSO DE ATUALIZAÇÃO DO PAINEL DASHBOARD  #################')
    data_hora_fim = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print('########### DATA E HORA ATUAIS:  ' + data_hora_fim + ' ##############')



"""
FUNÇÕES GENÉRICAS
"""
class StringCookieJar(CookieJar):
    def __init__(self, string=None, policy=None):
        CookieJar.__init__(self, policy)
        if string:
            self._cookies = pickle.loads(string)

def getContent(url, data=None, referer=None):
    """
    return content cookie html in response decode utf-8 to BeautifulSoup
    """
    encoded_data = urlencode(data) if data else None
    # if referer is None: url
    default_headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.2.9) Gecko/20100824 Firefox/3.6.9 ( .NET CLR 3.5.30729; .NET4.0E)',
    'Accept-Language': 'pt-br;q=0.5',
    'Accept-Charset': 'utf-8;q=0.7,*;q=0.7',
    'Accept-Encoding': 'gzip',
    'Connection': 'close',
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer': referer}
    req = Request(url, encoded_data, default_headers, origin_req_host=referer)

    cj = StringCookieJar()
    retries = 0
    response = None
    cookie_handler = HTTPCookieProcessor(cj)
    opener = build_opener(cookie_handler)
    max_retries = 3

    while True:
        try:
            handle = opener.open(req, timeout=30)
            if handle.info().get('Content-Encoding') == 'gzip':
                data = handle.read()
                buf = StringIO(data)
                f = GzipFile(fileobj=buf)
                response = f.read()
                break
            else:
                response = handle.read()
                break
            print(response)
        except HTTPError, e:
            retries = retries + 1
            print "%d Tentativas na url: %s, erro: %s" % (retries, url, e.getcode())
            if retries > max_retries:
                break
        except socket.timeout:
            retries = retries + 1
            print "%d Time out: %s, erro: %s" % (retries, url, e.getcode())
            if retries > max_retries:
                break
        except Exception as e:
            print(e)
            break

    if response:
        return response
    else:
        return False

"""
FUNCAO PRINCIPAL  QUE SERÁ EXECUTADA
"""

main()
