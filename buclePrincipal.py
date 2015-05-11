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
		listaObjetos(dato["_id"])

# actualizacion de valores de temperatura y luminosidad en el tiempo
def obtieneValorAmbiente(uidLugar, tipo):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	datos=coleccion.find_one({"_id":uidLugar})	
	if (tipo=="temp"):
		return datos["caracteristicas"]["temperatura"]
	if (tipo=="ilum"):
		return datos["caracteristicas"]["luminosidad"]	
	return -1

def ajusteValoresAmbiente(id):
	# comprobamos los valores del ambiente, y los pasamos a los lugares del interior, en intervalos de 1
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	#obtenemos los datos del ambiente
	datosAmbiente=coleccion.find_one({"id_padre":0, "tipo":"ambiente"})
	tempAmbiente=datosAmbiente["caracteristicas"]["temperatura"]
	lumiAmbiente=datosAmbiente["caracteristicas"]["luminosidad"]
	datos=coleccion.find({"id_padre":id})
	for dato in datos:
		#objeto lugar
		if (dato["tipo"]=="lugar"):
			# modificamos la temperatura
			if (dato["caracteristicas"]["temperatura"]<tempAmbiente):
				dato["caracteristicas"]["temperatura"] += 0.5
			if (dato["caracteristicas"]["temperatura"]>tempAmbiente):
				dato["caracteristicas"]["temperatura"] -= 0.5
			# modificamos la luminosidad
			if (dato["caracteristicas"]["luminosidad"]<lumiAmbiente):
				dato["caracteristicas"]["luminosidad"] += 1
			if (dato["caracteristicas"]["luminosidad"]>lumiAmbiente):
				dato["caracteristicas"]["luminosidad"] -= 1
			coleccion.save(dato)
			ajusteValoresAmbiente(dato["_id"])
		if (dato["tipo"]=="sensor"):
			valorActual=obtieneValorAmbiente(dato["id_padre"], dato["caracteristicas"]["tipo"])
			dato["caracteristicas"]["valor"]=valorActual
			coleccion.save(dato)
		

# ******************************************************************

# unidad AC de enfriamiento:
# baja la temperatura
def ejecutaAC(idLugar):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	dato=coleccion.find_one({"_id":idLugar})
	dato["caracteristicas"]["temperatura"] -= 1
	coleccion.save(dato)

# unidad de iluminacion
# sube la iluminacion		
def ejecutaLuz(idLugar):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	dato=coleccion.find_one({"_id":idLugar})
	dato["caracteristicas"]["luminosidad"] += 5
	coleccion.save(dato)

# ejecutor de actuadores 
def ejecutaActuadores(id):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	datosObjetos=coleccion.find({"id_padre":id})
	for dato in datosObjetos:
		if (dato["tipo"]=="actuador"):
			if (dato["caracteristicas"]["tipo"]=="temp" and dato["caracteristicas"]["activo"]==1): 	# aire acondicionado
				ejecutaAC(dato["id_padre"])
			if (dato["caracteristicas"]["tipo"]=="ilum" and dato["caracteristicas"]["activo"]==1): 	# iluminacion
				ejecutaLuz(dato["id_padre"])
		ejecutaActuadores(dato["_id"])

# ******************************************************************

				
def bucle():
	global items, numItem
	print "*************************************"
	print "Estado actual del sistema"
	numItem=0
	# muestra listado de objetos actuales
	listaObjetos(0)
	# realiza ajuste por temperatura ambiente exterior
	ajusteValoresAmbiente(0)

	# bucleActuadores
	ejecutaActuadores(0)
	
	

while True:
    startTime = time()
    bucle()
    endTime = time()-startTime
    sleep(5.0-endTime)