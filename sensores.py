from pymongo import MongoClient
import datetime
import os

def cls():
    os.system(['clear','cls'][os.name == 'nt'])


items={}
numItem=0

tipos={}
tipos[0]="lugar"
tipos[1]="sensor_temperatura"
tipos[2]="sensor_iluminacion"
tipos[3]="calefactor"
tipos[4]="bombilla"


def obtieneObjetos(id):
	global items, numItem
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	datos=coleccion.find({"id_padre":id})
	for dato in datos:
		print "["+str(numItem)+"]\tTipo: "+dato["tipo"]+"\tObj.:"+dato["nombre"]
		items[numItem]=dato["_id"]
		numItem += 1
		obtieneObjetos(dato["_id"])

def conectaObjeto(tipo, nombre, ubicacion):
	carac={}
	if (tipo==0):
		carac["estado"]=1
	if (tipo==1):
		carac["estado"]=1
		carac["temperatura"]=0
	if (tipo==2):
		carac["estado"]=1
		carac["luminosidad"]=0
	if (tipo==3):
		carac["estado"]=1
	if (tipo==4):
		carac["estado"]=1

	objeto = { 	"tipo":tipos[tipo],
			"id_padre":items[ubicacion],
			"timestamp":datetime.datetime.utcnow(),
			"nombre":nombre,
			"caracteristicas": carac
		}
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	coleccion.insert(objeto)

def desconectaObjeto(o_id):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	coleccion.remove({"_id":o_id})

while True:
	items={}
	numItem=1
	cls()
	print "Objetos disponibles actualmente"
	print ""
	obtieneObjetos(0)
	print ""
	print "Acciones disponibles"
	print "\t1) conectar objeto"
	print "\t2) desconectar objeto"
	accion = str(input("Seleccione una accion: "))
	if (accion=="1"):
		#creamos nuevo objeto
		ubi = int(input("Seleccione la ubicacion: "))
		print ""
		print "Tipo de objeto"
		print "\t0) Ubicacion"
		print "\t1) Sensor de temperatura"
		print "\t2) Sensor de iluminacion"
		print "\t3) Calefactor/AC"
		print "\t4) Bombilla"
		tip = int(input("Seleccione un tipo de objeto: "))
		nom = str(raw_input("Ingrese el nombre del objeto: "))
		conectaObjeto(tip, nom, ubi)
	elif (accion=="2"):
		ubi = int(input("Numero de objeto: "))
		desconectaObjeto(items[ubi])
	print items