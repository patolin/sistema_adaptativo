from time import time, sleep
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import os

items={}
numItem=0

def cls():
    os.system(['clear','cls'][os.name == 'nt'])

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

# ejecutor de simulacion 
def ejecutaSimulador(id):
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
		ejecutaSimulador(dato["_id"])

# ******************************************************************

# bucle Monitoreo
# verifica el estado de los sensores, y dispara alertas 
def verificaSensores(id):
	#verifica la existencia de sensores en la ubicacion, si no hay, apaga todos los AC y calefactores
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	objetosBase=coleccion.find({"tipo":"lugar", "id_padre":id})
	for lugar in objetosBase:

		cuartos=coleccion.find({"tipo":"lugar", "id_padre":lugar["_id"]})
		for cuarto in cuartos:
			#contamos cuantos sensores hay en dicho cuarto
			numSensores=coleccion.count({"tipo":"sensor", "id_padre":cuarto["_id"]})
			#print "sensores encontrados: "+str(numSensores)
			if (numSensores==0):
				# creamos una alerta
				print "Creando alerta para lugar id: "+str(cuarto["_id"])
				alarma={	"timestamp":datetime.datetime.utcnow(),
					"id_padre":cuarto["_id"],
					"id_alerta":-1,
					"atendida":0
				}
				coleccionAlertas=db.alertas
				coleccionAlertas.insert(alarma)

def disparaAlarma(idAlerta, idSensor):
	print "**************************************"
	print "Alarma disparada	: "+str(idAlerta)
	print "Sensor			: "+str(idSensor)
	print "**************************************"
	client = MongoClient()
	db=client.db_sua
	coleccion = db.alertas
	alarma={	"timestamp":datetime.datetime.utcnow(),
				"id_padre":idSensor,
				"id_alerta":idAlerta,
				"atendida":0
			}
	coleccion.insert(alarma)

def obtieneValorActual(uidSensor):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	sensor=coleccion.find_one({"_id":uidSensor})
	return sensor["caracteristicas"]["valor"]

def bucleMonitoreo(id):
	#verifica alarmas programadas, y dispara alertas si ocurre un evento
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	#monitoreamos la existencia de sensores
	verificaSensores(0)

	#obtenemos los datos del ambiente
	datosAlarmas=coleccion.find({"tipo":"alarma"})
	for alarma in datosAlarmas:
		uidAlarma=alarma["_id"]
		uidObjeto=alarma["id_padre"]
		tipoAlarma=alarma["caracteristicas"]["tipo"]
		valSensor=obtieneValorActual(uidObjeto)
		valAlarma=alarma["caracteristicas"]["valor"]
		if tipoAlarma==1:	# menor
			if (valSensor<valAlarma):
				disparaAlarma(uidAlarma, uidObjeto)
		if tipoAlarma==2:	# mayor
			if (valSensor>valAlarma):
				disparaAlarma(uidAlarma, uidObjeto)
		if tipoAlarma==3:	# igual
			if (valSensor==valAlarma):
				disparaAlarma(uidAlarma, uidObjeto)


# bucle de analisis
# verifica las alertas y actua segun lo programado, dependiendo de los objetos existentes
# por defecto siempre se puede controlar la iluminacion (persianas)
def obtieneLugarSensor(uid):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	sensor=coleccion.find_one({"_id":uid})
	return sensor["id_padre"]

def obtieneTipoAlerta(uid):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	objeto=coleccion.find_one({"_id":uid})
	if objeto != None:
		return objeto["caracteristicas"]["tipo"]

def bucleAnalisis(id):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.alertas
	alertas=coleccion.find({"atendida":0})
	for alerta in alertas:
		uidAlerta=alerta["_id"]
		uidSensor=alerta["id_padre"]
		uidFuente=alerta["id_alerta"]

		if (uidFuente==-1):
			# alerta de no sensores en la habitacion
			print "No hay sensores en el lugar. Apagando todas las unidades AC disponibles"
			coleccionObjetos=db.objetos
			unidadesAC=coleccionObjetos.find({"tipo":"actuador", "id_padre":uidSensor})
			for unidadAC in unidadesAC:
				coleccionAcciones = db.acciones
				accionNueva={
								"timestamp":datetime.datetime.utcnow(),
								"accion": "apagar", # encender/apagar
								"actuador": unidadAC["_id"],
								"atendida": 0
							}
				coleccionAcciones.insert(accionNueva)
			

		else:
			# lectura normal de sensores
			uidPadre=obtieneLugarSensor(uidSensor)
			tipAlerta=obtieneTipoAlerta(uidFuente)
			if (tipAlerta==1): #menor
				accionEvento="apagar"
			if (tipAlerta==2): #mayor
				accionEvento="encender"

			# obtenemos el lugar al que pertenece el sensor
			# verificamos si tiene una unidad AC
			coleccionObj = db.objetos
			NumUnidadesAC=coleccionObj.count({"id_padre": uidPadre, "tipo":"actuador"})
			#print "Unidades AC para el id: "+str(uidPadre)+" = "+str(NumUnidadesAC)
			if (NumUnidadesAC>0):
				unidadesAC=coleccionObj.find({"id_padre": uidPadre, "tipo":"actuador"})
				for unidadAC in unidadesAC:
					# encendemos cada unidad para que empiece a bajar la temperatura
					client = MongoClient()
					db=client.db_sua
					coleccionAcciones = db.acciones
					accionNueva={
									"timestamp":datetime.datetime.utcnow(),
									"accion": accionEvento, # encender/apagar
									"actuador": unidadAC["_id"],
									"atendida": 0
								}
					print "Nueva accion generada"
					coleccionAcciones.insert(accionNueva)
			else:
				# al no tener AC, bajamos la iluminacion simulando el cierre de persianas
				accionNueva= {}

		#marcamos la alerta como atendida
		alerta["atendida"]=1
		coleccion = db.alertas
		coleccion.save(alerta)


# bucle de ejecucion
def cambiaEstadoActuador(id, estado):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.objetos
	objeto=coleccion.find_one({"_id":id})
	if objeto != None:
		print ("Ejecutando accion "+estado+" para el actuador uid: "+str(id))
		if (estado=="encender"):
			objeto["caracteristicas"]["activo"]=1
		if (estado=="apagar"):
			objeto["caracteristicas"]["activo"]=0	
		coleccion.save(objeto)

def bucleEjecucion(id):
	client = MongoClient()
	db=client.db_sua
	coleccion = db.acciones
	accionesPendientes=coleccion.find({"atendida":0})
	for accion in accionesPendientes:
		cambiaEstadoActuador(accion["actuador"], accion["accion"])
		accion["atendida"]=1
		coleccion.save(accion)



# bucle principal del programa

def bucle():
	cls()
	global items, numItem
	print "*************************************"
	print "Estado actual del sistema"
	numItem=0
	# muestra listado de objetos actuales
	listaObjetos(0)
	# realiza ajuste por temperatura ambiente exterior
	ajusteValoresAmbiente(0)

	# bucle de monitoreo
	bucleMonitoreo(0)

	# bucle de analisis
	bucleAnalisis(0)

	# bucle de ejecucion
	bucleEjecucion(0)

	# bucle simulacion
	ejecutaSimulador(0)
	
	

while True:
    startTime = time()
    bucle()
    endTime = time()-startTime
    sleep(2.5-endTime)