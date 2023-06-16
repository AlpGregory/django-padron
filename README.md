# Desafío Padron electoral

Debe realizar un branch con su nombre en donde trabajará su solución.

## Fase 1:

Debe descargar el padron electoral de la siguiente dirección.
https://www.tse.go.cr/descarga_padron.htm

Dentro del archivo descargado se encuentran 2 archivos de interés, y un archivo de ayuda.
Debe construir los modelos necesarios en django para almacernar los datos en una base de datos.
Debe instalar y configurar Postgresql y PgAdmin4.
Debe crear un commando de django que permita ingresar Distelec.txt y Padron Completo.txt como parámetros y permita procesar los datos
    https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/

El procesamiento de los datos debe ser lo más rápido y eficiente posible en términos de memoria.

**Nota**:  Un tiempo válido es aproximadamente un minuto cargando todo y generando las estadísticas y más de 3 minutos ya se considera muy lento, por lo que deben ser eficientes.

Debe crear una vista que permita buscar el lugar de votación de una persona por nombre y número de cédula. El sistema se estará usando al pie de urna por lo que debe dar resultados sin demoras.

Dentro de la información que debe proporcionar en la vista está:
- Nombre
- Número de cédula
- Lugar de votación 
- Mesa de votación
- Vencimiento de la cédula.

Cantidad de personas que votan en el distrito, cantón y Provincia.
Cantidad de hombres y mujeres que votan en el distrito, cantón y Provincia.
Cantidad de personas que votan con la misma fecha de vencimiento de su cédula.

Para determinar el sexo de una persona debe implementar este algoritmo.
Si el cuarto dídigo de la cédula es par entonces la persona es Hombre, si es impar es mujer.

## Fase 2:

Debe crear un formulario autenticado que permita ingresar personas en centros de votación y eliminar personas fallecidas.
La actualización de esta información debe darse a travez de signals.

https://simpleisbetterthancomplex.com/tutorial/2016/07/28/how-to-create-django-signals.html


Enlaces de interés 

- https://docs.djangoproject.com/en/4.1/topics/db/queries/
- https://docs.djangoproject.com/en/4.1/topics/class-based-views/generic-display/
- https://docs.djangoproject.com/en/4.1/ref/models/querysets/
- https://docs.djangoproject.com/en/4.1/topics/db/optimization/
- https://docs.djangoproject.com/en/4.1/topics/db/sql/#executing-custom-sql-directly

## Fase 3:

Debe hacer una integración con MongoDB utilizando PyMongo, de forma que pueda usarse tanto la base de datos en Postgres como la de Mongo.
La intensión es que un usuario pueda estipular que base de datos desea utilizar en su instalación, (durante todas las funcionalidades del aplicativo se estará usando la misma db seleccionada en settings).

Debe utilizar almenos un patrón de diseño de 

- https://refactoring.guru/es/design-patterns/python

Debe modificar las vistas de forma que puedan funcionar con la base de datos seleccionada.

Nota: No puede utilzar ninguna biblioteca que permita usar el ORM de django con Mongo, osea Mongo engine y djongo entre otras están prohibídas.
