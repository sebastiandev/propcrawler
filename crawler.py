#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from zonaprop_crawler import ZonapropCrawler

def get_zonas():
    return ["capital federal", "buenos aires", "cordoba", "santa fe", "mendoza"]
    
def get_barrios():
    return ["Almagro", "Balvanera", "Barracas", "Barrio Norte", "Belgrano", "Boca", "Boedo", "Caballito", "Centro/Microcentro", "Chacarita", "Coghlan", "Colegiales", "Congreso", "Constitucion", "Flores", "Floresta", "Liniers", "Mataderos", "Monte Castro", "Nunez", "Palermo", "Parque Avellaneda", "Parque Centenario", "Parque Chacabuco", "Parque Chas", "Parque Patricios", "Paternal", "Pompeya", "Recoleta", "Saavedra", "San Cristobal", "San Nicolas", "San Telmo", "Tribunales", "Velez Sarsfield", "Versalles", "Villa Crespo", "Villa del Parque", "Villa Devoto", "Villa General Mitre", "Villa Lugano", "Villa Luro", "Villa Ortuzar", "Villa Pueyrredon", "Villa Real", "Villa Santa Rita", "Villa Soldati", "Villa Urquiza"]

def get_operaciones():
    return ["venta", "alquiler"]

def get_tipos():
    return ["ph", "departamentos", "casas", "oficinas"]

def get_precios(alquiler=False):
    multiplicador = 1000 if not alquiler else 1000
    if alquiler:
        precios = [str((n+1)*multiplicador) for n in range(20)]
    else:
        precios = [str((n)*multiplicador) for n in range(30, 200, 10)]
        precios += [str((n)*multiplicador) for n in range(200, 2000, 100)]
    
    return precios
    
def get_portales():
    return  [ZonapropCrawler, "todos"]

def mostrar_opciones(opciones, separador="."):
        print ""
        if len(opciones) >= 3:
            filas = (len(opciones) / 3) 

            for i in range(filas):
                # Magia: funcion lambda para calcular el elemento mas largo de la columna y usarlo como largo de la misma
                l = lambda col: max([len(opciones[col*filas:col*filas+filas][x]) for x in range(filas)])+1
                print ''.join([" %s%s%s" % (str(c*filas+i+1).rjust(2), separador, opciones[c*filas:c*filas+filas][i].ljust(l(c))) for c in range(3)])
        else:
            for i, o in enumerate(opciones):
                print " %s.%s" % (i+1, o)
                
        print ""
        opcion = raw_input(" Ingrese la opciones que desee: ")
        opcion = opcion if not opcion.isdigit() else opciones[int(opcion)-1]

        while opcion not in opciones:
            opcion = raw_input(" Nombre o numero invalido, ingrese nuevamente: ")
            opcion = opcion if not opcion.isdigit() else opciones[int(opcion)-1]

        return opcion

if __name__ == "__main__":
    import argparse
    import sys
    argparser = argparse.ArgumentParser(__file__, description="Buscador de propiedades")
    argparser.add_argument("--config", "-c", metavar="", help="yaml de configuracion")

    args = argparser.parse_args()
    config = args.config
    
    if not config:
        os.system('cls' if os.name == 'nt' else 'clear')
        print "**********************************************************************"
        print "**************    Buscador de propiedades    ********************"
        print "**********************************************************************"
        print ""
        print " Defina los ajustes de la busqueda"
        print ""
        
        print " Seleccione el tipo de operacion que desea buscar: "
        operacion = mostrar_opciones(get_operaciones())

        print ""
        print " Seleccione el tipo de propiedad que desea buscar: "
        tipo = mostrar_opciones(get_tipos())

        print ""
        print " Seleccione la zona donde desea buscar: "
        zona = mostrar_opciones(get_zonas())
        
        barrio = None
        print ""
        r = raw_input(" Desea especificar un barrio? (s/n): ").lower()
        if r == 's':
            barrio = mostrar_opciones(get_barrios())
            
        precio_max = None
        print ""
        r = raw_input(" Desea especificar un limite de precio? (s/n): ").lower()
        if r == 's':
            precio_max = mostrar_opciones(get_precios(alquiler=True if operacion=='alquiler' else False), separador=')')
        
        config = {
            'busqueda': {
                'operacion': operacion.lower(),
                'tipo': tipo.lower(),
                'zona': zona.lower(),
                'barrio': barrio.lower(),
                'precio_max': precio_max
            }
        }
        
        download = False
        folder = None
        r = raw_input(" Desea descargar las imagenes de cada publicacion? (s/n): ").lower()
        if r == 's':
            download = True
            while True:
                folder = raw_input(" Indique la carpeta donde se guardaran todas las imagenes de la busqueda: ").lower()
                e = raw_input(" Ingreso '%s', es correcto? (s/n): " % folder).lower()
             
                while not e.lower() == "s":
                    folder = raw_input(" Ingrese la carpeta de nuevo: ").lower()
                    e = raw_input(" Ingreso '%s', es correcto? (s/n): " % folder).lower()

                folder = os.path.abspath(folder)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                
                break
            
        print ""
        print " Seleccione el portal donde realizar la busquedad:"
        print ""

        portal = mostrar_opciones(get_portales())
        
        print ""
        print " Comenzando busqueda en %s" % portal if type(portal) is str else portal.__name__
        print "   > parametros:"
        for k, v in config['busqueda'].iteritems():
            print "     - %s: %s" % (k, v)
        print ""
        
        if portal == 'all':
            portales = get_portales().remove('all')
            for p in portales:
                crawler = p(download_imgs=download, img_folder=folder, config=config)
                crawler.crawl()
        else:
            portal(download_imgs=download, img_folder=folder, config=config).crawl()
    else:
        print "Usando configuracion:"
        for k, v in config['busqueda'].iteritems():
            print "  - %s: %s" % (k, v)
        pass
        
    
    