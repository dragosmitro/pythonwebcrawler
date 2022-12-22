import numpy as np
import pandas
import requests
from bs4 import BeautifulSoup
import re
from dateutil.parser import parse

fisierDate = open('date.txt', 'w')
fisierDateAll = open("dateAll.txt", 'w')

# extragere date + definitii generale
data = pandas.read_csv('sample-websites.csv')
forbidden = "403 Forbidden"
badEmail = ['@sentry-next.wixpress.com', '@sentry-viewer.wixpress.com', '@sentry.wixpress.com', '@example.com', '.png', '.webp', '.jpg', '.jpeg']

def scriereFisier(array, file):
    if isinstance(array, str) or isinstance(array, int):
        if str(array) != str(0):
            print(array, file = file)
    else:
        for i in range(len(array)):
            if str(array[i]) != str(0):
                print(array[i], file = file)

def afisare(array):
    if isinstance(array, str) or isinstance(array, int):
        if array != str(0):
            print(array)
    else:
        for i in range(len(array)):
            if array[i] != str(0):
                print(array[i])

# procesare email
def procesareEmail(array):
    if isinstance(array, str) or isinstance(array, int):
        array = str(array).lower()
        if re.findall(r"(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){1}", str(array)):
            array = "0"
        for j in range(len(badEmail)):
            if re.findall(badEmail[j], str(array)):
                array = "0"
    else:
        for i in range(len(array)):
            array[i] = str(array[i]).lower()
            if re.findall(r"(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){1}", str(array[i])):
                array[i] = 0
            for j in range(len(badEmail)):
                if re.findall(badEmail[j], str(array[i])):
                    array[i] = 0

# procesare nr tel
def procesareNrTel(array):
    if isinstance(array, str) or isinstance(array, int):
        array = str(array)
        array = array.strip()
        array = array.strip("\/ ")
        array = array.replace(" ", "")
        if len(array) <= 10 or len(array) >= 15:
            array = "0"
    else:
        for i in range(len(array)):
            array[i] = str(array[i])
            array[i] = array[i].strip()
            array[i] = array[i].strip("\/ ")
            array[i] = array[i].replace(" ", "")
            if len(array[i]) <= 10 or len(array[i]) >= 15:
                array[i] = "0"

# functie extragere pagina ce contine "contact" in ea
def parcurgerePagini(pagini):
    for i in range(len(pagini)):
        # se extrage un obiect ce are ca parametru pagina
        pagini[i] = re.search(r"[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)", str(pagini[i]))

        # ramane doar acel parametru
        pagini[i] = pagini[i].group(0)

        # se cauta cuvantul "contact" in link
        if re.findall(r"contact", pagini[i].lower()):
            return pagini[i]
        else:
            pagini[i] = "deleted"
    # cazul in care nu exista contact in nici o pagina
    return 0

# functie extragere email dintr-o pagina de "contact"
def extragereEmail(pagina):
    # acelasi principiu ca mai jos
    try:
        pag = requests.get(pagina)
        supa = BeautifulSoup(pag.content, "html.parser")

        if supa.title.string == forbidden:
            print("[FORBIDDEN ACCES] Nu se poate procesa pagina contact " + pagina)
            return 0
        else:
            # regex email basic
            emailContact = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(supa))
            print("Am procesat pagina contact (pentru extragere email): " + pagina)

            # se returneaza ce se gaseste
            return emailContact
    except:
        # sau 0 daca nu se gaseste nimic
        print("[NO CONNECTION] Nu se poate procesa pagina contact: " + pagina)
        return 0

def extragereTelefon(pagina):
    # acelasi principiu ca mai jos
    try:
        pag = requests.get(pagina)
        supica = BeautifulSoup(pag.content, "html.parser")

        if supica.title.string == forbidden:
            print("[FORBIDDEN ACCES] Nu se poate procesa pagina contact " + pagina)
            return 0
        else:
            # regex telefon basic
            telefonContact = re.findall(r"[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*", str(soup.get_text()))
            print("Am procesat pagina contact (pentru extragere nr tel): " + pagina)

            # se returneaza ce se gaseste
            return telefonContact
    except:
        # sau 0 daca nu se gaseste nimic
        print("[NO CONNECTION] Nu se poate procesa pagina contact: " + pagina)
        return 0

# parcurgere fiecare site in parte
for i in range(len(data)):
    # generare URL
    URL = "http://www." + data.iloc[i, 0]
    try:
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")

        # daca avem forbidden acces in titlu
        if soup.title.string == forbidden:
            print("[FORBIDDEN ACCES] Nu se poate procesa website: " + URL + " (" + str(i) + ")")

        # teoretic am intrat cu succes pe site
        else:
            print("Procesez website: " + URL + " (" + str(i) + ")")

            # cautare toate paginile dinauntru site-ului cu ajutorul <a href=http...>
            pagini = soup.find_all('a', attrs={'href': re.compile("^http(s)?://")})

            # se extrage pagina care contine cuvantul cheie "contact"
            pagina = parcurgerePagini(pagini)

            # se incearca obtinerea emailului si a telefonului din pagina actuala
            # regex email basic
            email = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(soup))
            # regex nr tel basic
            telefon = re.findall(r"[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*", str(soup.get_text()))

            # se incearaca obtinerea emailului si a telefonului din pagina de "contact"
            if pagina != 0:
                emailContact = extragereEmail(pagina)
                telefonContact = extragereTelefon(pagina)
            else:
                emailContact = 0
                telefonContact = 0

            # se initializeaza lista totala goala
            totalTelefon = []
            # se iau toate cazurile posibile pentru a putea concatena datele intr-un singur obiect
            # cazul value + X
            if isinstance(telefon, str) or isinstance(telefon, int):
                # cazul value + value
                if isinstance(telefonContact, str) or isinstance(telefonContact, int):
                    totalTelefon.append(telefon)
                    totalTelefon.append(telefonContact)
                # cazul value + list
                else:
                    telefonContact.append(telefon)
                    totalTelefon = telefonContact + totalTelefon
            # cazul list + x
            else:
                # cazul list + value
                if isinstance(telefonContact, str) or isinstance(telefonContact, int):
                    totalTelefon.append(telefonContact)
                    totalTelefon = totalTelefon + telefon
                # cazul list + list
                else:
                    totalTelefon = telefon + telefonContact

            # aceleasi principii ca la totalTelefon
            totalEmail = []
            if isinstance(email, str) or isinstance(email, int):
                if isinstance(emailContact, str) or isinstance(emailContact, int):
                    totalEmail.append(email)
                    totalEmail.append(emailContact)
                else:
                    totalEmail.append(email)
                    totalEmail = emailContact + totalEmail
            else:
                if isinstance(emailContact, str) or isinstance(emailContact, int):
                    totalEmail.append(emailContact)
                    totalEmail = totalEmail + email
                else:
                    totalEmail = email + emailContact

            # se scriu datele raw in fisierul cu toate datele raw
            print("##########", file=fisierDateAll)
            print("(" + str(i) + ") " + data.iloc[i, 0], file=fisierDateAll)
            print("##########", file=fisierDateAll)
            scriereFisier(totalTelefon, fisierDateAll)
            scriereFisier(totalEmail, fisierDateAll)

            # se proceseaza datele
            procesareNrTel(totalTelefon)
            procesareEmail(totalEmail)

            # se elimina valorile duplicat
            totalEmail = list(dict.fromkeys(totalEmail))
            totalTelefon = list(dict.fromkeys(totalTelefon))

            # se scriu datele in fisier
            print("##########", file=fisierDate)
            print("(" + str(i) + ") " + data.iloc[i, 0], file = fisierDate)
            print("##########", file = fisierDate)
            scriereFisier(totalTelefon, fisierDate)
            scriereFisier(totalEmail, fisierDate)

            # se sterg valorile reziduale
            del totalEmail
            del totalTelefon
    except:
        # eroare incarcare site (de cele mai multe ori no connection)
        print("[NO CONNECTION] Nu se poate procesa website: " + URL + " (" + str(i) + ")")

print("########################")
print("Procesare finalizata!")

fisierDate.close()
fisierDateAll.close()