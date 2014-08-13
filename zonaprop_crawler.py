#!/usr/bin/python
# -*- coding: utf-8 -*-

from prop_crawler import PropCrawler

barrios = {
    "almagro": "lnZ3667",
    "balvanera": "lnZ3683",
    "barracas": "lnZ3686",
    "barrio Norte": "lnZ3659",
    "belgrano": "lnZ3652",
    "boca": "lnZ3682",
    "boedo": "lnZ3703",
    "caballito": "lnZ3693",
    "centro/microcentro": "lnZ3671",
    "chacarita": "lnZ3665",
    "coghlan": "lnZ3651",
    "colegiales": "lnZ3678",
    "congreso": "lnZ3653",
    "constitucion": "lnZ3691",
    "flores": "lnZ3687",
    "floresta": "lnZ3654",
    "liniers": "lnZ3676",
    "mataderos": "lnZ3704",
    "monte castro": "lnZ3695",
    "nunez": "lnZ3697",
    "palermo": "lnZ3694",
    "parque avellaneda": "lnZ3688",
    "parque centenario": "lnZ3662",
    "parque chacabuco": "lnZ3644",
    "parque chas": "lnZ3649",
    "parque patricios": "lnZ3681",
    "paternal": "lnZ3670",
    "pompeya": "lnZ3702",
    "recoleta": "lnZ3675",
    "saavedra": "lnZ3698",
    "san cristobal": "lnZ3679",
    "san nicolas": "lnZ3646",
    "san telmo": "lnZ3689",
    "tribunales": "lnZ3696",
    "velez sarsfield": "lnZ3690",
    "versalles": "lnZ3663",
    "villa crespo": "lnZ3701",
    "villa del parque": "lnZ3645",
    "villa devoto": "lnZ3658",
    "villa general mitre": "lnZ3666",
    "villa lugano": "lnZ3669",
    "villa luro": "lnZ3672",
    "villa ortuzar": "lnZ3660",
    "villa pueyrredon": "lnZ3647",
    "Villa real": "lnZ3650",
    "villa santa rita": "lnZ3664",
    "villa soldati": "lnZ3668",
    "villa urquiza": "lnZ3657"
}

class ZonapropCrawler(PropCrawler):
    def __init__(self, collection_name="propiedades", download_imgs=False, img_folder=None, config=None):
        super(ZonapropCrawler, self).__init__(collection_name=collection_name, download_imgs=download_imgs, img_folder=img_folder, config=config)

    def _build_search(self, operacion="", tipo="", zona="", barrio="", precio_min=0, precio_max=0):
        url = "http://propiedades.zonaprop.com.ar/%s %s %s %s" % (operacion, tipo, zona, barrio)
        url = url.strip().replace(' ', '-')
        
        # arma segunda parte con codigos
        codigo_tipo = ''
        codigo_operacion = ''
        codigo_zona = ''
        codigo_precio = ''
        
        codigo_operacion = "opZtipo-operacion-%s" % operacion if operacion else None
        if tipo == 'ph':
            codigo_tipo = "ncZ3"
        elif tipo == 'departamentos':
            codigo_tipo = "ncZ1"
        elif tipo == 'oficinas':
            codigo_tipo = "ncZ19"
        elif tipo == 'casas':
            codigo_tipo = "ncZ2"
        
        if zona == "capital federal":
            codigo_zona = "lnZ3642"
        
        if barrio:
            codigo_zona = barrios[barrio.lower()]
        
        if precio_max > 0:
            codigo_precio = "prZusd-%s-%s" % (precio_min, precio_max)
        
        url2 = "/%s %s %s %s soZlsasc" % (codigo_tipo, codigo_operacion, codigo_zona, codigo_precio)  # soZlsasc ordena por mas reciente
        url2 = url2.strip().replace('  ',' ').replace(' ', '_')
        url += "/"+url2
        
        return url

    
    def _iterate_results(self, html_parser):
        listado = html_parser.findChild('div', attrs={'id':"listado"})
        resumenes = listado.findchildren('a', attrs={'abbreviate': "56"})
        items = listado.findChildren('div', attrs={'class': "aviso"})
        
        for i, item in enumerate(items):
            yield item.attrs['viewitemurl'], resumenes[i].text if resumenes else None

    def _extract_data(self, html_parser):
        aviso = html_parser.findChild('div', attrs={'id': "aviso"})
        titulo = aviso.findChild('div', attrs={'class': "titulo"})
        
        direccion = titulo.findChild('h2', attrs={'class': "h2"}).text
        zona = titulo.findChild('h2', attrs={'class': "ubicacion"}).text
        precio = aviso.findChild('div', attrs={'class': "ar"}).p.text
        
        descripcion = html_parser.find('pre', attrs={'id': "description"}).text
        
        caracteristicas_item = html_parser.find('div', attrs={'class': "caract_grales"})
        caracteristicas = {}
        for dt in caracteristicas_item.findChildren('dt'):
            nombre = PropCrawler._limpiar_texto(dt.text.replace(':', ''))
            valor = dt.find_next_sibling().text
            caracteristicas[nombre] = PropCrawler._limpiar_texto(valor)
        
        fotos = []
        images = aviso.find('div', attrs={'id': "bigImages"})
        for img in images.findChildren('a'):
            fotos.append(img['href'])

        return direccion, zona, precio, descripcion, caracteristicas, fotos

    def _get_next_page(self, html_parser):
        siguiente = html_parser.find('div', attrs={'id': "paginacion"}).find('a', text="Siguiente")
        return siguiente['href'] if siguiente else None
