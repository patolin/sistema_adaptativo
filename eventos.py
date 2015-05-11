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
		strTipo=""
		strAlarma=""
		if (dato["tipo"]=="sensor"):
			strTipo="* "
		if (dato["tipo"]=="alarma"):
			strTipo="** "
			strAlarma=""
			if (dato["caracteristicas"]["tipo"]==1):
				strAlarma="Val. menor a "+str(dato["caracteristicas"]["valor"])
			if (dato["caracteristicas"]["tipo"]==2):
				strAlarma="Val. mayor a "+str(dato["caracteristicas"]["valor"])
			if (dato["caracteristicas"]["tipo"]==3):
				strAlarma="Val. igual a "+str(dato["caracteristicas"]["valor"])
		print "["+str(numItem)+"]\t"+strTipo+"Tipo: "+dato["tipo"]+"\tObj.:"+dato["nombre"]+"\t"+strAlarma
		items[numItem]=dato["_id"]
		numItem += 1
		#obtieneAlarmas(dato["_id"])
		obtieneObjetos(dato["_id"])	

def obtieneAlarmas(id):
	global items, numItem
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	datos=coleccion.find({"tipo":"alarma", "id_objeto":id})
	for dato in datos:
		
		alTipo=""
		if (dato["caracteristicas"]["tipo"]==1):
			alTipo="Menor a"
		if (dato["caracteristicas"]["tipo"]==2):
			alTipo="Mayor a"
		if (dato["caracteristicas"]["tipo"]==3):
			alTipo="Igual a"	
		items[numItem]=dato["_id"]
		print "\t["+str(numItem)+"] Alarma: "+alTipo+" "+str(dato["caracteristicas"]["valor"])
		numItem += 1
		

def creaAlerta(ubicacion, tipo, valor, nombre):
	carac={}
	carac["tipo"]=tipo #1 mayor, 2 menor, 3 igual
	carac["valor"]=valor
	objeto = {
		"tipo":"alarma",
		"id_padre":items[ubicacion],
		"nombre":nombre,
		"timestamp":datetime.datetime.utcnow(),
		"caracteristicas":carac
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
	print "Gestion de eventos de monitoreo"
	print "OEventos disponibles actualmente"
	print ""
	obtieneObjetos(0)
	print ""
	print "Acciones disponibles"
	print "\t1) crear trigger de evento"
	print "\t2) borrar trigger"
	accion = str(input("Seleccione una accion: "))
	if (accion=="1"):
		# insertamos nueva alarma
		ubi=int(input("Seleccione el sensor: "))
		nom=str(raw_input("Nombre de la alerta: "))
		tip=int(input("Opcion: 1) menor, 2) mayor, 3) igual : "))
		val=int(input("Valor de disparo: "))
		creaAlerta(ubi, tip, val, nom)
	if (accion=="2"):
		#borramos una alarma
		id=int(input("Seleccione una alerta: "))
		eliminaAlerta(id)