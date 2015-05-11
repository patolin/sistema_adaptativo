from time import time, sleep
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

items={}
numItem=0


def creaUid(id):
	return ObjectId(str(id))

def listaObjetos(id):
	global items, numItem
	
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	datos=coleccion.find({"id_padre":id})
	for dato in datos:
		strTab=""
		strAlarma=""
		strValor=""
		if (dato["tipo"]=="lugar" or dato["tipo"]=="ambiente"):
			strValor="["+str(dato["caracteristicas"]["temperatura"])+","+str(dato["caracteristicas"]["luminosidad"])+"]"
		if (dato["tipo"]=="sensor" or dato["tipo"]=="actuador"):
			strTab="* "
			strValor="["+str(dato["caracteristicas"]["valor"])+"]"
		if (dato["tipo"]=="alarma"):
			strTab="** "
			strAlarma=""
			if (dato["caracteristicas"]["tipo"]==1):
				strValor=" < "+str(dato["caracteristicas"]["valor"])
			if (dato["caracteristicas"]["tipo"]==2):
				strValor=" > "+str(dato["caracteristicas"]["valor"])
			if (dato["caracteristicas"]["tipo"]==3):
				strValor=" = "+str(dato["caracteristicas"]["valor"])

		print "["+str(numItem)+"]\t"+strValor+"\t"+strTab+"Tipo: "+dato["tipo"]+"\tObj.:"+dato["nombre"]
		items[numItem]=dato["_id"]
		numItem += 1
		obtieneObjetos(dato["_id"])


				
def bucle():
	global items, numItem
	print "*************************************"
	print "Estado actual del sistema"
	numItem=0
	listaObjetos(0)
	
	

while True:
    startTime = time()
    bucle()
    endTime = time()-startTime
    sleep(5.0-endTime)