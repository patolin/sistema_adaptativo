from time import time, sleep
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

def creaUid(id):
	return ObjectId(str(id))

def obtieneObjetos(id):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	datos=coleccion.find({"id_padre":id})
	for dato in datos:
		print "Obj.:\t"+dato["nombre"]
		print "Tipo: \t"+dato["tipo"]
		if (dato["tipo"]=="sensor_temperatura"):
			print "\tTemp: "+str(dato["caracteristicas"]["temperatura"])
		if (dato["tipo"]=="sensor_iluminacion"):
			print "\tLumi: "+str(dato["caracteristicas"]["luminosidad"])
		if (dato["tipo"]=="lugar" or dato["tipo"]=="ambiente"):
			print "\tTemp: "+str(dato["caracteristicas"]["temperatura"])
			print "\tLumi: "+str(dato["caracteristicas"]["luminosidad"])
		print ""
		obtieneObjetos(dato["_id"])

	#return dato["tipo"]
	
# ajuste de valores para los parametros de exterior
def ajusteValoresAmbiente(id):
	# comprobamos los valores del ambiente, y los pasamos a los lugares del interior, en intervalos de 1
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	#obtenemos los datos del ambiente
	datosAmbiente=coleccion.find_one({"id_padre":0, "tipo":"ambiente"})
	tempAmbiente=datosAmbiente["caracteristicas"]["temperatura"]
	lumiAmbiente=datosAmbiente["caracteristicas"]["luminosidad"]
	
	#vamos ajustando a los parametros internos
	datos=coleccion.find({"id_padre":id})
	for lugar in datos:
		#objeto lugar
		if (lugar["tipo"]=="lugar"):
			#temperatura
			if (lugar["caracteristicas"]["temperatura"]<tempAmbiente):
				#elevamos la temperatura
				lugar["caracteristicas"]["temperatura"] += 1
			if (lugar["caracteristicas"]["temperatura"]>tempAmbiente):
				#bajamos la temperatura
				lugar["caracteristicas"]["temperatura"] -= 1
			
			#luminosidad
			if (lugar["caracteristicas"]["luminosidad"]<lumiAmbiente):
				#elevamos la luminosidad
				lugar["caracteristicas"]["luminosidad"] += 2
			if (lugar["caracteristicas"]["luminosidad"]>lumiAmbiente):
				#bajamos la luminosidad
				lugar["caracteristicas"]["luminosidad"] -= 2
			#coleccion.update_one({"_id": lugar["_id"]},{"$Set": lugar}, upsert=False)
			coleccion.save(lugar)
			ajusteValoresAmbiente(lugar["_id"])
		#sensor de temperatura
		if (lugar["tipo"]=="sensor_temperatura"):
			#temperatura
			if (lugar["caracteristicas"]["temperatura"]<tempAmbiente):
				#elevamos la temperatura
				lugar["caracteristicas"]["temperatura"] += 1
			if (lugar["caracteristicas"]["temperatura"]>tempAmbiente):
				#bajamos la temperatura
				lugar["caracteristicas"]["temperatura"] -= 1
			coleccion.save(lugar)
			ajusteValoresAmbiente(lugar["_id"])
		#sensor luminosidad
		if (lugar["tipo"]=="sensor_iluminacion"):
			#luminosidad
			if (lugar["caracteristicas"]["luminosidad"]<lumiAmbiente):
				#elevamos la luminosidad
				lugar["caracteristicas"]["luminosidad"] += 2
			if (lugar["caracteristicas"]["luminosidad"]>lumiAmbiente):
				#bajamos la luminosidad
				lugar["caracteristicas"]["luminosidad"] -= 2
			#coleccion.update_one({"_id": lugar["_id"]},{"$Set": lugar}, upsert=False)
			coleccion.save(lugar)
			ajusteValoresAmbiente(lugar["_id"])
			
def disparaAlarma(idAlerta, idSensor):
	print "**************************************"
	print "Alarma disparada	: "+str(idAlerta)
	print "Sensor			: "+str(idSensor)
	print "**************************************"
	


def obtieneValorActual(uidSensor):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	sensor=coleccion.find_one({"_id":uidSensor})
	if (sensor["tipo"]=="sensor_temperatura"):
		return sensor["caracteristicas"]["temperatura"]
	if (sensor["tipo"]=="sensor_iluminacion"):
		return sensor["caracteristicas"]["luminosidad"]
		
def bucleMonitor():
	#verifica alarmas programadas, y dispara alertas si ocurre un evento
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	#obtenemos los datos del ambiente
	datosAlarmas=coleccion.find({"tipo":"alarma"})
	for alarma in datosAlarmas:
		#comprobamos el estado del objeto y comparamos con la alarma
		uidSensor=alarma["id_objeto"]
		uidAlerta=alarma["_id"]
		
		valSensor=obtieneValorActual(uidSensor)
		valAlarma=alarma["valor"]
		valTipo=alarma["evento"]
		
		if (valTipo==1):	#mayor
			if (valSensor>valAlarma):
				disparaAlarma(uidAlerta, uidSensor)
		if (valTipo==2):	#menor
			if (valSensor<valAlarma):
				disparaAlarma(uidAlerta, uidSensor)
		if (valTipo==4):	#igual
			if (valSensor==valAlarma):
				disparaAlarma(uidAlerta, uidSensor)
				
def bucle():
	print "*************************************"
	print "Estado actual del sistema"
	
	obtieneObjetos(0)
	ajusteValoresAmbiente(0)
	
	bucleMonitor()
	

while True:
    startTime = time()
    bucle()
    endTime = time()-startTime
    sleep(5.0-endTime)