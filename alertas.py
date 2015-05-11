#generacion de alertas para el monitoreo

from pymongo import MongoClient
import datetime
import os

items={}
numItem=0


def cls():
    os.system(['clear','cls'][os.name == 'nt'])
	

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
		obtieneAlarmas(dato["_id"])
		obtieneObjetos(dato["_id"])	

def obtieneAlarmas(id):
	global items, numItem
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	datos=coleccion.find({"tipo":"alarma", "id_objeto":id})
	for dato in datos:
		alTipo=""
		if (dato["evento"]==1):
			alTipo="Menor a"
		if (dato["evento"]==2):
			alTipo="Mayor a"
		if (dato["evento"]==3):
			alTipo="Igual a"	
		items[numItem]=dato["_id"]
		print "\t["+str(numItem)+"] Alarma: "+alTipo+" "+str(dato["valor"])
		numItem += 1
		

def creaAlerta(ubicacion, tipo, valor):
	objeto = {
		"tipo":"alarma",
		"id_objeto":items[ubicacion],
		"evento":tipo,
		"valor":valor
	}
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	coleccion.insert(objeto)

def eliminaAlerta(id):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	coleccion.remove({"tipo":"alarma", "_id":items[id]})
	
	
while True:
	items={}
	numItem=1
	cls()
	print "********************************"
	print "Gestion de alertas de monitoreo"
	print "Objetos disponibles actualmente"
	print ""
	obtieneObjetos(0)
	print ""
	print "Acciones disponibles"
	print "\t1) crear alerta"
	print "\t2) borrar alerta"
	accion = str(input("Seleccione una accion: "))
	if (accion=="1"):
		# insertamos nueva alarma
		ubi=int(input("Seleccione el sensor: "))
		tip=int(input("Alarma a: 1) menor, 2) mayor, 3) igual : "))
		val=int(input("Valor de disparo: "))
		creaAlerta(ubi, tip, val)
	if (accion=="2"):
		#borramos una alarma
		id=int(input("Seleccione una alerta: "))
		eliminaAlerta(id)