# pyScienti
Es una aplicación escrita en Python que permite obtener resúmenes de información académica de investigadores, Grupos de investigación y publicaciones de manera rápida y sencilla.\
A partir del código del grupo de investigación o con los enlaces de los perfiles de CvLAC o GrupLAC permite obtener un resumen de producción, categorías, integrantes e información de interés en un archivo de Excel, extrayendo la información directamente del texto de la página web del grupo o del investigador sin acceder a bases de datos, permitiendo extraer la información, ampliarla y vincularla con otra información.\
Permite obtener un resumen de producción, categorías, integrantes e información de interés registradas en la plataforma Scienti, y guardarla en un archivo de Excel, permitiendo extraer la información, ampliarla y vincularla con otra información fácilmente.\
La aplicación extrae la información directamente del texto de la página web del grupo o del investigador sin acceder a bases de datos, es decir, solo accede a la información de los grupos o investigadores que se encuentra pública.\
Cuenta con 3 partes principales:\
•	Grupos\
•	Investigadores\
•	Publicaciones
## Funcionalidades
### Grupos de investigación:
Es un módulo que obtiene información específicamente de grupos de investigación registrados en MinCiencias.\
A partir de:\
•	Código del grupo de investigación.\
•	Enlaces de los perfiles GrupLAC.\
El software extrae información directamente del GrupLAC del grupo:\
•	Nombre del grupo \
•	Categoría vigente del grupo\
•	Áreas de conocimiento\
•	Instituciones a las que se vincula el grupo\
•	Integrantes actuales\
•	Líneas de investigación del grupo\
•	Participación académica del grupo en programas académicos\
•	Producción académica, intelectual y cultural del grupo\
Permite comparar con una lista personalizada de integrantes para comparar y visualizar cuales de ellos se encuentran inscritos y activos en el grupo.\
De los artículos producidos por el grupo de investigación, se obtiene información de los autores, año, revista de publicación, DOI, además de correlacionar la información con otras fuentes, tales como la clasificación actual de la revista en Publindex y SJR.\
La aplicación permite exportar la información en un archivo xls separado por hojas según el tipo de información que contienen, es decir, En cada hoja se presenta una lista de productos del mismo tipo.
### Investigadores
Es un módulo que permite extraer información acerca de investigadores que tengan el perfil de CvLAC público.\
A partir del enlace de CvLAC del investigador, puede extraer la información individual de cada uno de los autores.\
•	Nombre del investigador\ 
•	Categoría vigente del investigador\
•	Áreas de conocimiento\
•	Formación\
•	Producción académica, intelectual y cultural del investigador.\
Permite a partir de una lista de investigadores, verificar si alguno de ellos está registrado en algún grupo de investigación y obtener su información y la del grupo, o similarmente, verificar si un grupo de investigación tiene inscrito un investigador en particular o una lista de investigadores.\
Es posible obtener la información de múltiples grupos de investigación y autores simultáneamente, poniendo los códigos de los grupos o sus enlaces de GrupLAC en un archivo de Excel y cargándolo a la aplicación.
### Publicaciones
Es un módulo que permite obtener la clasificación internacional y nacional de las revistas científicas (si están indexadas en publindex), y datos de los libros publicados
A partir de:
•	ISSN de una o varias revistas\
•	ISBN de uno o varios libros\
Se obtiene:\
•	La categoría en Publindex de la revista (si está indexada en el país) 
•	Cuartil al que pertenece internacionalmente (Scimago Journal Rank)\
•	Lista de autores de los libros

# Requerimientos
•	Python 3.7 o superior\
•	pandas
•	numpy
•	xlrd
•	bs4


# API reference

## Clases
### *class* **Author**(link)

Es una clase que representa un investigador.\
  **Parámetros:**\
  •link(*str*) - Enlace de CvLAC de la forma *https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=XXXXXXXXXXX* (debe ser de esta forma, los enlaces de la forma https://scienti. **colciencias.gov.co:8080** /cvlac/visualizador/generarCurriculoCv.do?cod_rh=XXXXXXXXXX no funcionan correctamente).\
  
#### *method* **Author.get_data_xls**(*self*)

Exporta la información del investigador en un archivo .xlsx con el nombre registrado en CvLAC

#### *method* **Author.save_group**(*self*)

Guarda el objeto del investigador a un archivo .pickle.

##
  
### *class* **Group**(link)

Es una clase que representa un grupo de investigación.
  **Parámetros:**\
  •link(*str*) - Enlace de GrupLAC de la forma *https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=XXXXXXXXXXXXXX*

#### *method* **Group.fill_group**(*self*)

Procesa la información del grupo y la convierte en atributos del mismo.

#### *method* **Group.get_common_inv**(*self, names, links*)

Utilizado para comparar si en una lista hay investigadores que pertenecen al grupo y se encuentran activos.

**Parámetros:**\
  •names(*Series*) - Serie de pandas que contiene los nombres de los investigadores, en el mismo orden de *links*\
  •links(*Series*) - Serie de pandas que contiene los enlaces de CvLAC de los investigadores, en el mismo orden de *names*\
  
#### *method* **Group.fill_authors**(*self*)

Crea objetos **Author** de los investigadores que pertenecen al grupo.

#### *method* **Group.to_xlsx**(*self*)

Exporta la informacion del grupo a un archivo .xlsx, si no se ha ejecutado *fill_group*, se hará automáticamente.

#### *method* **Group.save_group**(*self*)

Guarda el objeto del grupo a un archivo .pickle.


## Funciones
*function* **get_gruplac_link**(*code*)

Convierte el código del grupo en su respectivo enlace de GrupLAC. El codigo es de la forma *COLXXXXXXXX*


Copyright (C) <2020>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

  
