import shutil
import pylab
import requests
from bs4 import BeautifulSoup
import cv2
# Nodig voor tekst op foto
import numpy as np
from PIL import Image, ImageTk, ImageFont, ImageDraw, ImageFile, ImageDraw2
ImageFile.LOAD_TRUNCATED_IMAGES = True

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
# Imports voor autmatisch opnieuw op te starten
from datetime import datetime, timedelta
# Nodig voor de fotos te verwijderen
import os
import math

# Seconden naar middernacht berekenen om dan de functie (script) te herstarten
def how_many_seconds_until_midnight():
    tomorrow = datetime.now() + timedelta(1)
    midnight = datetime(year=tomorrow.year, month=tomorrow.month,
                        day=tomorrow.day, hour=0, minute=0, second=0)
    return (midnight - datetime.now()).seconds


def ophalen_ibood_promoties():

    url = 'https://www.ibood.com/be/nl'
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    nav = soup.find_all('div', class_='cf')

    headers = soup.find_all('h3')

    headerdict = {}
    x = 0
    for header in headers:
        header = str(header)
        header = header.replace("<h3>", '')
        header = header.replace("</h3>", '')
        headerdict[x] = header
        x+=1

    # laatsteitemdict = list(headerdict.keys())[-1]

    headerdict.popitem()

    fotoots = {}
    x = 0
    for container in nav:
        img = container.find('img')
        if img is not None:
            if img not in fotoots.values():
                fotoots[x] = img
                x += 1


    # Dicts aanmaken
    links = {}
    titels = {}



    # 29ste link is de start van de producten
    i = 29
    x = 0
    while(i < 33):
        links[x] = (soup.find_all('a')[i])
        titels[x] = (soup.find_all('h3')[x])
        i += 1
        x += 1


    titels2 = {}
    x = 0

    for titel in titels.values():
        titel = str(titel)
        titel = titel.replace("<h3>", '')
        titel = titel.replace("</h3>", '')
        titels[x] = titel
        x+=1


    fotonamen = {}
    fotonaamwijzigen = ''
    x = 0
    y = 0

    # vars voor displayen imgs
    rij = 0
    plaats = 0

    # Get current working directory
    path = os.getcwd()

    # lijst maken met alle files in de directory
    filesinfolder = os.listdir(path)

    #Voor elke file die in de folder zit die eindigt op '.gif' verwijderen
    for file in filesinfolder:
        if file.endswith('.gif'):
            os.remove(file)

    # Menu afzetten
    plt.rcParams['toolbar'] = 'None'

    aantal_fotos = (len(fotoots) - 2)
    # print('aantal fotos: ', fotoots)
    print(math.floor((aantal_fotos / 2)))

    # Aantal rijen berekenen
    aantal_rijen = math.floor((aantal_fotos / 2))
    print('Aantal rijen: ', aantal_rijen)
    # axis array voor de fotos in te zetten (4 naar beneden, 2 in de lengte)
    f, axarr = plt.subplots(aantal_rijen, 2)

    toegevoegde_productnamen = []
    # Iteraten over alle values van de dicts -> daarvan de src van de html tag nemen
    for foto in fotoots.values():
        src = foto.get("src")


        if src:
            srcstring = str(src)
            srcarray = src.split('/')

            srcarray = list(filter(None, srcarray))  # fastest

            if str(srcarray[1]).isdigit():

                if not src.startswith("https"):
                    fotonaam = src
                    link = 'https:' + src

                r = requests.get(link, stream=True)
                if r.status_code == 200:

                    # Decoderen voor de bits te verkijgen (Om te downloaden)
                    r.raw.decode_content = True
                    f = open(fotonaam.split("/")[-1], "wb")
                    # os.mkdir(os.path.join(os.getcwd(), src))
                    shutil.copyfileobj(r.raw, f)
                    f.close()

                    # String splitsen voor de extensie te verkijgen
                    fotosrcarray = fotonaam.split('/')
                    laatstearrayitem = len(fotosrcarray) - 1

                    # Foto openen
                    im = Image.open(fotosrcarray[laatstearrayitem])


                    # .jpg wijzigen naar .gif om de fotos te openen en op te slaan als .gif
                    fotonaamwijzigen = str(fotosrcarray[laatstearrayitem]).split('.')

                    fotonaamwijzigen[len(fotonaamwijzigen) - 1] = 'gif'
                    fotonaamwijzigen = '.'.join(fotonaamwijzigen)

                    # tekst op fotos zetten als x kleiner is dan de lengte van de headerdictionary
                    if x < len(headerdict):

                        productnaam = headerdict[x]
                        image = cv2.imread(fotonaamwijzigen)



                    im.save(fotonaamwijzigen)


                    text_foto = Image.open(fotonaamwijzigen)
                    # draw = ImageDraw2(text_foto)
                    # font = ImageFont.truetype("Roboto-Regular.ttf", 50)
                    # draw.text((10, 10), "Sample Text", (255, 255, 255), font=font)
                    # text_foto.save(fotonaamwijzigen)

                    fotonamen[x] = fotosrcarray[laatstearrayitem]

                    # matplotlib foto openen
                    img = mpimg.imread(fotonaamwijzigen)

                    if '<span>' not in productnaam and len(productnaam) > 5 and productnaam not in toegevoegde_productnamen:

                        toegevoegde_productnamen.append(productnaam)

                        #Tonen van images en titels toevegen met productnaam
                        axarr[rij, plaats].plot(x, y)
                        axarr[rij, plaats].set_title(productnaam)
                        axarr[rij, plaats].imshow(img)
                        axarr[rij, plaats].axis('off')
                        # axarr[rij, plaats].

                        print(fotonaamwijzigen, ' geplaatst op ', rij, ', ', plaats+1)

                        if plaats >= 1:
                            rij = rij + 1
                            plaats = 0
                        else:
                            plaats = plaats + 1

                    # Verwijderen vorige .jpgs om plaats te besparen
                    os.remove(fotosrcarray[laatstearrayitem])
                    axarr[rij, plaats].axis('off')

                    x += 1


    # ibood.com link verwijderen uit de dict
    links.pop(0)



    # fig = plt.figure(figsize=(12, 10))
    fig = pylab.gcf()
    fig.canvas.set_window_title('iBood')

    fig.set_size_inches((10,10))


    plt.axis('off')

    plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
    plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)

    # Window icoon wijzigen
    plt.Figure()
    thismanager = plt.get_current_fig_manager()
    # thismanager.window.wm_iconbitmap("icon/favicon.ico")

    plt.show(block=False)

    seconden_naar_middernacht = int(how_many_seconds_until_midnight())

    plt.savefig('../discord3.6/imgs/ibood.png')

    plt.pause(seconden_naar_middernacht)

    plt.close()

def herstart():
    ophalen_ibood_promoties()

while True:
    herstart()