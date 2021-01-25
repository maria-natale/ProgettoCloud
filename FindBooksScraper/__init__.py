import logging
import time
from urllib.request import urlopen

from bs4 import BeautifulSoup
import requests
import json
import azure.functions as func

# parametri di configurazione bing search

subscriptionKey = "ffa25d9c29d34f8a89cc9542187a452e"
customConfigId = "7ef069d7-04d8-4bad-b8c4-da9912bdd273"
list_of_links = []

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')



    name_of_book= req.params.get('name') #prendi il nome del libro dalla richiesta
    who_has_to_scrape = req.params.get('who') #parametro per capire su quale sito si deve fare scraping
    if not name_of_book or not who_has_to_scrape:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name_of_book = req_body.get('name')
            who_has_to_scrape = req_body.get('who')

    if name_of_book and who_has_to_scrape:
       list_of_results = wich_scraper(name_of_book,who_has_to_scrape)
       logging.info('Sono nel main dopo assegnazione di list_of_result')
       logging.info('Ecco il contenuto della lista:')
       logging.info(list_of_results)
       if len(list_of_results)<=5:
           return func.HttpResponse(f"""Hai chiesto per il libro: {list_of_results[0]} di {list_of_results[1]} \n
            Il libro è {list_of_results[2]} al prezzo di{list_of_results[3]}, il suo genere è {list_of_results[4]}""")
       else:
           all_of_res =''
           for elem in list_of_results:
               all_of_res+=str(elem)
               all_of_res+='\n'
           return func.HttpResponse(all_of_res)
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )


def call_bing (searchTerms,list_):
    url = 'https://api.bing.microsoft.com/v7.0/custom/search?q=' + searchTerms + '&' + 'customconfig=' + customConfigId + '&mkt=it-IT&count=1'
    r = requests.get(url, headers={'Ocp-Apim-Subscription-Key': subscriptionKey})
    json_object_result = json.loads(r.text)
    #print(json_object_result)
    values= json_object_result['webPages']['value']
    for j in range(len(values)):
        list_.append(values[j]['url'])

def scrape_hoepli (url):   # in ordine restituisce titolo,autore,disponibilità e prezzo, genere
    page = urlopen(url)
    logging.info('URL HOEPLI: '+url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    logging.info('URL HOEPLI: '+url)
    list_of_result = []
    tit = soup.find('h1')
    list_of_result.append(tit.text)
    aut = soup.find('h2',attrs={'class':'prodotto'})
    list_of_result.append(aut.text)

    is_disp = soup.find('p',attrs={'class':'disp_frase'})
    if is_disp is None:
        list_of_result.append('Non disponibile')
    else:
        list_of_result.append('Disponibile')

    prezzo = soup.findAll("div",attrs={"class":"prezzo"})
    for span in prezzo:
        list_of_result.append(span.find('span').text)

    gener = soup.findAll("span",attrs={'class':'fs11'})
    genere =''
    for g in gener:
        genere+=g.text+', '
    list_of_result.append(genere)
    
    return list_of_result

def scrape_ibs(url):  #manca genere
    page = urlopen(url)
    logging.info('URL IBS: '+url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    ibs_result =[]
    priceString = soup.find("h2", class_="price__current")  # prezzo
    availability = soup.find("p", class_="availability__time availability available")
    title = soup.find("h1", class_="title__text")
    author = soup.find("h2", class_="subline__title author__title")
    if title is not None:
        title = title.text
        ibs_result.append(title)

    if author is not None:
        author=author.text
        author=author.lstrip()
        author=author.rstrip()
        ibs_result.append(author)

    if availability is not None:
        availability=availability.text
        ibs_result.append(availability)

    if priceString is not None:
        priceString=priceString.text
        priceString=" ".join(priceString.split())
        priceString=priceString.replace(",", ".")
        priceString=priceString[2:len(priceString)]
        price=float(priceString)
        ibs_result.append(price)
    ibs_result.append('Genere non rilevato')
    return ibs_result

def scrape_amazon(url): #completo
    clear_url = url[url.rindex('/') + 1:] #asin del libro
    logging.info('URL AMAZON: '+url)
    scrape_am_result =[]
    params = {
        'api_key': '903BFF738C8C466DB4F4708A699AD62A',
        'type': 'product',
        'asin': ''+clear_url,   #prendiamo l'asin del libro
        'amazon_domain': 'amazon.it'

    }
    result = requests.get('https://api.rainforestapi.com/request', params)
    jsonStringResult = json.dumps(result.json())
    jsonResult = json.loads(jsonStringResult)
    logging.info(jsonResult)
    scrape_am_result.append(jsonResult['product']['title'])
    autori = jsonResult['product']['authors']
    list_of_auth =""
    for autore in autori:
        list_of_auth+=autore['name']+' & '
    scrape_am_result.append(list_of_auth)
    try:
        scrape_am_result.append(jsonResult['product']['buybox_winner']['availability']['raw'])
        scrape_am_result.append(jsonResult['product']['buybox_winner']['price']['raw'])
    except KeyError:
        scrape_am_result.append('Non Disponibile')
        scrape_am_result.append('Articolo non disponibile, prezzo non specificato')
    categorie = jsonResult['product']['categories']
    for i in range(len(categorie)):
        if i == len(categorie) - 1:
            scrape_am_result.append(categorie[i]['name'])
    return scrape_am_result

def scrape_mondadori(url): #completo
    page = urlopen(url)
    logging.info('URL MONDADORI: '+url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    res_scrape = []
    title = soup.find("h1", class_="title")
    if title is not None:
        title = title.text
        title = title.lstrip()
        title = title.rstrip()
    res_scrape.append(title)
    author = soup.find("a", class_="link nti-author")
    if author is not None:
        author = author.text
        author = author.lstrip()
        author = author.rstrip()
    res_scrape.append(author)
    availability = soup.find("span", class_="big lightGreen")
    if availability is not None:
        availability = availability.text.rstrip()
        availability = availability.lstrip()
    res_scrape.append(availability)
    priceString = soup.find("span", class_="old-price")  # prezzo
    if priceString is None:
        priceString = soup.find("span", class_="priceBox")

    promoString = soup.find("span", class_="promo")
    newPrice = None
    if priceString is not None:
        priceString = " ".join(priceString.text.split())
        priceString = priceString[:len(priceString) - 2]
        priceString = priceString.replace(",", ".")
        price = float(priceString)
        if promoString is not None:
            promoString = promoString.text[1:len(promoString.text) - 1]
            promo = float(promoString)
            newPrice = price - (5 / 100 * price).__round__(2)
        else:
            newPrice = price
    res_scrape.append(newPrice)
    genre = soup.find("a", class_="link sgn")
    if genre is not None:
        genre = genre.text
    res_scrape.append(genre)
    return res_scrape

def scrape_not_available_feltrinelli(url): #in caso il libro non sia disponibile
    page = requests.get(url)
    logging.info('SCRAPE FELTR NOT AV URL: '+url)
    soup = BeautifulSoup(page.content, 'html.parser')
    result_ = []
    resultTitle = soup.findAll('div',attrs={"class":"head-intro"})
    for y in resultTitle:
        result_.append(y.find('h1').text)
        result_.append(y.find('a').text)
    result_.append('Non Disponibile')
    prezz = soup.find('span',attrs={'class':'price'})
    result_.append(prezz.text)
    moreInfo = soup.findAll('div',attrs={"class":"block-content separate-block"})
    for info in moreInfo:
        result_.append(info.find('a').text)
    return result_


def scrape_feltrinelli(url):
    page = requests.get(url)
    logging.info('URL FELTRINELLI: '+url)
    soup = BeautifulSoup(page.content, 'html.parser')
    result_felt = []
    # Prende il titolo ed autore
    resultTitle = soup.findAll('div', attrs={"class": "head-intro"})
    for y in resultTitle:
        result_felt.append(y.find('span').text) #nome libro
        result_felt.append(print(y.find('a').text)) #autore

    # Prende la disponibilità del prodotto
    resultAvailability = soup.findAll('div', attrs={"class": "availability"})
    for span in resultAvailability:
        result_felt.append(span.find('span').text) #disponibilità

    # Prende il prezzo
    resultsPrice = soup.findAll('div', attrs={"class": "price clearfix"})

    for x in resultsPrice:
        result_felt.append(x.find('span').text)

    # Altre info sul prodotto
    moreInfo = soup.findAll('div', attrs={"class": "block-content separate-block"})
    for info in moreInfo:
        result_felt.append(info.find('a').text)
    
    if len(result_felt)<5:
        result_felt = scrape_not_available_feltrinelli(url)
    return result_felt


def wich_scraper(name,who):
    web_sites = ['Hoepli', 'Ibs', 'Amazon', 'Mondadori', 'Feltrinelli']
    if who =='all':
        for i in range(len(web_sites)):
            searchTerms = name+' '+ web_sites[i]
            call_bing(searchTerms, list_of_links)
            time.sleep(4)  #necessario con il free tier di bing non si possono fare 4 chiamate in contemporaneo
        logging.info('chiamata prima di hoepli')
        result_of_hoepli_scrape = scrape_hoepli(list_of_links[len(list_of_links)-5]) #lista delle informazioni di hoepli
        logging.info('Hoepli LIST: '+str(result_of_hoepli_scrape))
        logging.info('chiamata prima di ibs')
        result_of_ibs_scrape = scrape_ibs(list_of_links[len(list_of_links)-4]) #lista informazioni ibs
        logging.info('IBS list: '+str(result_of_ibs_scrape))
        logging.info('chiamata prima di amazon')
        result_of_amazon_scrape = scrape_amazon(list_of_links[len(list_of_links)-3]) #lista informazioni amazon
        logging.info('List AMazon: '+str(result_of_amazon_scrape))
        logging.info('chiamata prima di mondadori')
        result_of_mond_scrape = scrape_mondadori(list_of_links[len(list_of_links)-2])
        logging.info('List Mondadori: '+ str(result_of_mond_scrape))
        logging.info('chiamata prima di feltrinelli')
        result_of_felt_scrape = scrape_feltrinelli(list_of_links[len(list_of_links)-1])
        logging.info('List Feltri: '+str(result_of_felt_scrape))
        concat_list = result_of_hoepli_scrape+result_of_ibs_scrape+result_of_amazon_scrape+result_of_mond_scrape+result_of_felt_scrape
        logging.info('Prima della concatenazione')
        logging.info(concat_list)
        return concat_list

    if who =='hoepli':
        searchTerms = name+' '+web_sites[0]
        call_bing(searchTerms,list_of_links)
        return scrape_hoepli(list_of_links[len(list_of_links)-1])

    if who =='ibs':
        searchTerms = name + ' ' + web_sites[1]
        call_bing(searchTerms, list_of_links)
        logging.info('link: '+list_of_links[0])
        return scrape_ibs(list_of_links[len(list_of_links)-1])
    if who =='amazon':
        searchTerms = name + ' ' + web_sites[2]
        call_bing(searchTerms, list_of_links)
        return scrape_amazon(list_of_links[len(list_of_links)-1])
    if who=='mondadori':
        searchTerms = name + ' ' + web_sites[3]
        call_bing(searchTerms, list_of_links)
        return scrape_mondadori(list_of_links[len(list_of_links)-1])
    if who=='feltrinelli':
        searchTerms = name + ' ' + web_sites[4]
        call_bing(searchTerms, list_of_links)
        return scrape_feltrinelli(list_of_links[len(list_of_links)-1])





