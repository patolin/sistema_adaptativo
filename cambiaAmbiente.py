# cambio en los parametros del ambiente

from time import time, sleep
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

client = MongoClient()
db=client.db_sua
coleccion = db.objetos
datosAmbiente=coleccion.find_one({"id_padre":0, "tipo":"ambiente"})
datosAmbiente["caracteristicas"]["temperatura"]=28
datosAmbiente["caracteristicas"]["luminosidad"]=50
coleccion.save(datosAmbiente)