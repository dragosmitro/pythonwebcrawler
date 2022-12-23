import pandas
import requests
from bs4 import BeautifulSoup
import re

fisierDate = open('date.txt', 'w')
fisierDateAll = open("dateUnprocessed.txt", 'w')

# extracting data from the csv file + general definitions
data = pandas.read_csv('sample-websites.csv')
forbidden = "403 Forbidden"
badEmail = ['@sentry-next.wixpress.com', '@sentry-viewer.wixpress.com', '@sentry.wixpress.com', '@example.com', '.png', '.webp', '.jpg', '.jpeg', 'sentry.io']

# further email processing to remove duplicates ('example@email.com' & 'example@email.com.' are considered duplicates)
def removeEmailDuplicates(array):
    if isinstance(array, str) or isinstance(array, int):
        array = str(array).strip(".-")
        return array
    else:
        for i in range(len(array)):
            array[i] = str(array[i]).strip(".-")
            for j in range(len(array)):
                if re.findall(str(array[i]), str(array[j])) or re.findall(str(array[j]), str(array[i])):
                    if len(str(array[i])) > len(str(array[j])):
                        array[i] = array[j]
                    else:
                        array[j] = array[i]
        return array

# write to file function
def scriereFisier(array, file):
    if isinstance(array, str) or isinstance(array, int):
        if str(array) != str(0):
            print(array, file = file)
    else:
        for i in range(len(array)):
            if str(array[i]) != str(0):
                print(array[i], file = file)

# write in terminal function
def afisare(array):
    if isinstance(array, str) or isinstance(array, int):
        if array != str(0):
            print(array)
    else:
        for i in range(len(array)):
            if array[i] != str(0):
                print(array[i])

# email processing
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

# phone number processing
def procesareNrTel(array):
    if isinstance(array, str) or isinstance(array, int):
        array = str(array)
        array = array.strip()
        array = array.strip("\/ -.")
        array = array.replace(" ", "")
        if len(array) < 10 or len(array) >= 16:
            array = "0"
    else:
        for i in range(len(array)):
            array[i] = str(array[i])
            array[i] = array[i].strip()
            array[i] = array[i].strip("\/ -.")
            array[i] = array[i].replace(" ", "")
            if len(array[i]) < 10 or len(array[i]) >= 16:
                array[i] = "0"

# function that returns a page that could be the contact page of the website
def parcurgerePagini(pagini):
    for i in range(len(pagini)):
        # extracts an object that has a valid link withn it
        pagini[i] = re.search(r"[(http(s)?):\/\/(www\.)-?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)", str(pagini[i]))
        # print(pagini[i])
        # only the link remains
        pagini[i] = pagini[i].group(0)

        # it searches for the word "contact" within the link
        if re.findall(r"contact", pagini[i].lower()):
            return pagini[i]
        else:
            pagini[i] = "deleted"
    # no "contact" page found
    return 0

# function that extracts email from a page
def extragereEmail(pagina):
    # same principle as in the next function
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

            # returns what it finds
            return emailContact
    except:
        # or 0 if it finds nothing or cant acces the page
        print("[NO CONNECTION] Nu se poate procesa pagina contact: " + pagina)
        return 0

# function that extracts phone number from a page
def extragereTelefon(pagina):
    try:
        # gets html page
        pag = requests.get(pagina)

        # processes html page
        supica = BeautifulSoup(pag.content, "html.parser")

        if supica.title.string == forbidden:
            print("[FORBIDDEN ACCES] Nu se poate procesa pagina contact " + pagina)
            return 0
        else:
            # basic phone number regex
            telefonContact = re.findall(r"[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*", str(supica.get_text()))
            print("Am procesat pagina contact (pentru extragere nr tel): " + pagina)

            # returns what if finds
            return telefonContact
    except:
        # or 0 if it finds nothing or cant acces the page
        print("[NO CONNECTION] Nu se poate procesa pagina contact: " + pagina)
        return 0

# main function, it processes all sites from the csv file
for i in range(len(data)):
    # generating URL
    URL = "http://www." + data.iloc[i, 0]

    try:
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")

        # if forbidden in title
        if soup.title.string == forbidden:
            print("[FORBIDDEN ACCES] Nu se poate procesa website: " + URL + " (" + str(i) + ")")

        # theoretically we are in
        else:

            print("Procesez website: " + URL + " (" + str(i) + ")")
            # searches for all links within the page
            pagini = soup.find_all('a', attrs={'href': re.compile("^http(s)?://")})

            # searches for the contact page within those links
            pagina = parcurgerePagini(pagini)

            # trying to extract email & phone number using regex from the provided page
            # regex email basic
            email = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", str(soup))
            # regex phone number basic
            telefon = re.findall(r"[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*", str(soup.get_text()))
            # notice how for the email we search in the html code while for the phone number we search in the text of the site
            # that is because phone numbers are much harder to extract from random numbers if read from html code
            # while emails are much easier to extract from html code because they dont get concatenated with text from the site

            # trying to take the email and the phone number from the contact page aswell if found
            if pagina != 0:
                emailContact = extragereEmail(pagina)
                telefonContact = extragereTelefon(pagina)
            else:
                emailContact = 0
                telefonContact = 0

            # initializing empty list
            totalTelefon = []

            # concatenates the two data lists found in every combination to ensure it is correctly concatenated
            # case value + X
            if isinstance(telefon, str) or isinstance(telefon, int):
                # case value + value
                if isinstance(telefonContact, str) or isinstance(telefonContact, int):
                    totalTelefon.append(telefon)
                    totalTelefon.append(telefonContact)
                # case value + list
                else:
                    telefonContact.append(telefon)
                    totalTelefon = telefonContact + totalTelefon
            # case list + X
            else:
                # case list + value
                if isinstance(telefonContact, str) or isinstance(telefonContact, int):
                    totalTelefon.append(telefonContact)
                    totalTelefon = totalTelefon + telefon
                # case list + list
                else:
                    totalTelefon = telefon + telefonContact

            # same principle as above
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

            # in the dataUnprocessed file it writes all found data (without further processing), helpful for debugging & improving
            print("##########", file=fisierDateAll)
            print("(" + str(i) + ") " + data.iloc[i, 0], file=fisierDateAll)
            print("##########", file=fisierDateAll)
            scriereFisier(totalTelefon, fisierDateAll)
            scriereFisier(totalEmail, fisierDateAll)

            # processing data
            procesareNrTel(totalTelefon)
            procesareEmail(totalEmail)

            # removing duplicates
            totalEmail = removeEmailDuplicates(totalEmail)
            totalEmail = list(dict.fromkeys(totalEmail))
            totalTelefon = list(dict.fromkeys(totalTelefon))

            # writing supposedly valid data in data file
            print("##########", file=fisierDate)
            print("(" + str(i) + ") " + data.iloc[i, 0], file = fisierDate)
            print("##########", file = fisierDate)
            scriereFisier(totalTelefon, fisierDate)
            scriereFisier(totalEmail, fisierDate)

            # deleting residual values (to not be used in the next iteration)
            del totalEmail
            del totalTelefon
    except:
        # error while loading the site (most likely no connection)
        print("[NO CONNECTION] Nu se poate procesa website: " + URL + " (" + str(i) + ")")

# processing finished
print("########################")
print("Procesare finalizata!")

# closing files
fisierDate.close()
fisierDateAll.close()

# all done