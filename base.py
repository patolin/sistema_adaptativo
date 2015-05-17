from pymongo import MongoClient
import datetime


client = MongoClient()

db=client.db_sua


#borramos todos los objetos
print "Vaciando contenedores de datos"



coleccion = db.alertas
coleccion.remove({})

coleccion = db.objetos
coleccion.remove({})

print "Creando nuevos objetos"

temp_inicial=20
ilum_inicial=50

#creamos el elemento ambiente
objeto = { 	"tipo":"ambiente",
			"id_padre":0,
			"timestamp":datetime.datetime.utcnow(),
			"nombre":"exterior",
			"caracteristicas": {"temperatura":temp_inicial, "luminosidad": ilum_inicial  }
		}

uidCasa = coleccion.insert(objeto)
print "Objeto Casa ambiente con UID: "+str(uidCasa)

#creamos el objeto casa
objeto = { 	"tipo":"lugar",
			"id_padre":0,
			"timestamp":datetime.datetime.utcnow(),
			"nombre":"casa",
			"caracteristicas": { "estado":1,"temperatura":0, "luminosidad": 0 }
		}
uidCasa = coleccion.insert(objeto)
print "Objeto Casa creado con UID: "+str(uidCasa)

objeto = { 	"tipo":"lugar",
			"id_padre":uidCasa,
			"timestamp":datetime.datetime.utcnow(),
			"nombre":"cuarto 1",
			"caracteristicas": { "estado":1,"temperatura":0, "luminosidad":0 }
		}
uidCuarto1 = coleccion.insert(objeto)
print "Objeto Cuarto 1 creado con UID: "+str(uidCuarto1)

objeto = { 	"tipo":"lugar",
			"id_padre":uidCasa,
			"timestamp":datetime.datetime.utcnow(),
			"nombre":"cuarto 2",
			"caracteristicas": { "estado":1,"temperatura":0, "luminosidad": 0}
		}
uidCuarto2 = coleccion.insert(objeto)
print "Objeto Cuarto 2 creado con UID: "+str(uidCuarto2)

print "Configuramos datos de temperatura y luminosidad iniciales"

