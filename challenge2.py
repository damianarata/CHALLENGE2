from __future__ import print_function
import pickle
import os.path
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
import mysql.connector
import webbrowser

#connecting with mysql
mydb = mysql.connector.connect(
   host="localhost",
   user="root",
   passwd="Meli2019#"
)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def ListMessagesMatchingQuery(service, user_id, query=''):
  try:
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])
    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])
    return messages
  except errors.HttpError as error:
    print ('An error occurred: %s' % error)

def GetMessage(service, user_id, msg_id):
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    return message
  except errors.HttpError as error:
    print ('An error occurred: %s' % error)
      
def CreateDB(ndb):
  try:
    mycursor = mydb.cursor() 
    mycursor.execute("DROP DATABASE IF EXISTS devopsmails;") #Elimino la db "devosmails" en caso de que exista
    mycursor.execute("CREATE DATABASE " + ndb )
    mycursor.execute("USE " + ndb)
    mycursor.execute("CREATE TABLE datos (subject VARCHAR(80), date VARCHAR (80), remitente VARCHAR (80));")
    print ("La base de datos fue creada")
    return mycursor
  except:
    print ("Error al crear la base de datos")

def SearchData (mycursor,service,userId,word):
  try:
    a =("")
    b =("")
    c =("")
    idMails = ListMessagesMatchingQuery(service, userId, word) #se realiza la query
    for id in idMails: #search data about from, date and subject 
        mensaje = GetMessage(service, userId, id["id"]) #obtejngo todos los ID de correos con la palabra que busco
        for header in mensaje["payload"]["headers"]:
            if header["name"] == "Subject":
               a = header["value"]
            if header["name"] == "Date":
               b = header["value"]
            if header["name"] == "From":
              c = header["value"]
            if a != "" and b != "" and c != "" :
              try:
                sql = ("INSERT INTO datos (subject, date, remitente) VALUES (%s,%s,%s)")
                var = ( a [0:79] , b , c [0:79] ) #truncar datos para evitar problemas con la longitud de la base de datos
                mycursor.execute(sql,var)
                mydb.commit()
                print("1 registro insertado")
                a =("")
                b =("")
                c =("")
              except: #ante algun error en la escritura va a continuar el proceso
                  print ("Error al insertar valores")
                  a =("")
                  b =("")
                  c =("")

  except:
     print ("cuenta de correo no valida, por favor verifique")
     
def words ():
  try:
    words = input ("Ingrese palabra a buscar y presione Enter (Por default la palabra a buscar sera DevOPS):\n")
    if words == "":
      words = "Devops"
    return words
  except:
    return "Devops"

def db (): #se define una db persistente o no.
  try:
    db = input ("Si desea guardar la base de datos de manera permanente ingrese un nombre para la misma sino Enter (Por defualt la base de datos es Devopsmails): ")
    if db == "":
      db = "devopsmails"
    return db 
  except:
    return db 

def UpdateCred (userId,lastmail): #modifico la cuenta de correo por default, ingreso al codigo y hago un swap de variables. 
  s = open("challenge2.py").read() #en la proxima ejecucion el default va a ser el ultimo ejecutado(y funcionado).
  s = s.replace(lastmail,userId)
  f = open("challenge2.py", 'w')
  f.write(s)
  f.close()
                  
def main():
    """Shows basic usage of the Gmail API. Lists the user's Gmail labels."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    lastmail = "rodriguezarata.d@gmail.com" #cuenta de correo por default
    userId = input ("Ingrese una cuenta de correo gmail o presiona enter para continuar con la cuenta por default ("+lastmail+"): ")
    #print (lastmail)
    if userId == "":
      userId = lastmail
    word = words()
    ndb = db ()
    print ("La palabra a buscar es: " + word)
    print ("El nombre de la base de datos es: " + ndb)
    mycursor = CreateDB(ndb + ";") #Se le agrega el ";" para que se ejecute el comando en sql
    SearchData (mycursor,service,userId,word)
    if userId != lastmail: #actualizar la cuenta por default
      DefaultCred = input ('¿Confirma hacer esta cuenta "'+ userId+'" como default? y/n')
      if DefaultCred == "y" or DefaultCred == "Y" or DefaultCred == "yes" or DefaultCred == "YES" or DefaultCred == "Yes":
        UpdateCred (userId,lastmail)
        
    
if __name__ == '__main__':
  try: #Verifico que esten las credenciales
    s = open("credentials.json").read()
  except:
    input ("Falta descargar las credenciales y almacenarlas en la misma carpeta\nPresiona enter para acceder a la web y reiniciar el programa ")
    webbrowser.open_new("https://developers.google.com/gmail/api/quickstart/python")
  main()
  os.remove ("token.pickle") #por motivo de seguridad borro el token
  print ("Ejecucion terminada")



