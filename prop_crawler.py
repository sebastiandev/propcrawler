import requests
from requests import ConnectionError
import yaml
import re
import os
from bs4 import BeautifulSoup
from pymongo import MongoClient


class PropCrawler(object):
    def __init__(self, collection_name="propiedades", download_imgs=False, img_folder=None, config=None):
        self._collection_name = collection_name
        self._collection = None
        try:
            client = MongoClient(host='localhost', port=27017, tz_aware=True)
            db = self.client['buscador_propiedades']
            self._collection = db[collection_name]
        except Exception, e:
            print "  >> Mongo Error: %s" % e
            print "  >> Continua sin base de datos..."
            
        self._need_to_download_imgs = download_imgs
        self._imgs_folder = img_folder
        self._config = config if type(config) is dict else yaml.load(open(config))
    
    def _build_search(self, operacion="", tipo="", zona="", barrio="", precio_min=0, precio_max=0):
        pass    
    
    def _iterate_results(self, html_parser):
        pass
    
    def _extract_data(self, html_parser):
        pass
    
    def _get_next_page(self, html_parser):
        pass
        
    @staticmethod
    def _limpiar_texto(texto):
        return re.sub(r'\s+', ' ', texto, flags=re.UNICODE | re.MULTILINE | re.IGNORECASE).strip()  # transforma multiples espacios a uno solo
        
    def _crawl_search_result(self, search_url=None, all_pages=True):
        res = None
        try:
            res = requests.get(search_url)
        except ConnectionError,e:
            print "  > Error! %s" % e
            return
        
        parser = BeautifulSoup(res.content)

        for item_url, resumen in self._iterate_results(parser):
            if resumen and self._collection:
                prop_id = PropCrawler._limpiar_texto(resumen).replace(' ', '_').replace('-', '_').lower()
                if self._collection.find_one({'_id': prop_id}) is not None:
                    continue #  ya tenemos la propiedad indexada, conitnuar
                    
            item_data = self._extract_data_from_item_page(item_url)
            
            if self._collection:
                item_data['_id'] = PropCrawler._limpiar_texto(resumen).replace(' ', '_').replace('-', '_').lower()
                self._collection.save(item_data)
            
            if self._need_to_download_imgs:
                self._download_imgs(folder=item_data['carpeta_fotos'], img_urls=item_data['fotos'])

            if self._is_interesting_prop(prop=item_data):
                print "********************************************************************"
                print "                  Encontramos una propiedad interesante!"
                print "********************************************************************"
                print " Url: %s" % item_data['url']
                print " Direccion: %s" % item_data['direccion']
                print " Zona: %s" % item_data['zona']
                print " Precio: %s" % item_data['precio']
                print " Descripcion: " 
                print " %s" % item_data['descripcion']
                print "********************************************************************"
        
        siguiente = self._get_next_page(parser)
        if siguiente:
            self._crawl_search_result(siguiente)
        
    def _extract_data_from_item_page(self, item_url):
        res = None
        try:
            res = requests.get(item_url)
        except ConnectionError,e:
            print "  > Error! %s" % e
            return
        
        parser = BeautifulSoup(res.content)     
        direccion, zona, precio, descripcion, caracteristicas, fotos = self._extract_data(parser)
        
        prop_imgs_folder = None
        if self._need_to_download_imgs:
            prop_folder = direccion+zona
            prop_folder = PropCrawler._limpiar_texto(prop_folder).strip().replace(' ', '_').replace(' -', '_')
            prop_imgs_folder = self._imgs_folder+"\\"+prop_folder+"\\"

        data = {
            'direccion': PropCrawler._limpiar_texto(direccion),
            'zona': PropCrawler._limpiar_texto(zona),
            'precio': PropCrawler._limpiar_texto(precio),
            'descripcion': PropCrawler._limpiar_texto(descripcion),
            'caracteristicas': caracteristicas,
            'carpeta_fotos': prop_imgs_folder.lower(),
            'fotos': fotos,
            'url': item_url
        }
        
        return data

    def _download_imgs(self, folder=None, img_urls=[]):
        try:
            if not os.path.exists(folder):
                os.makedirs(folder)
                    
            for i, url in enumerate(img_urls):
                img_binary = requests.get(url)
                img_file = open(folder+str(i)+".jpg", "wb")
                img_file.write(img_binary.content)
                img_file.flush()
                img_file.close()
        except ConnectionError,e:
            print "  > Error! %s" % e
        except Exception, e:
            print "  > Error Inesperado! %s" % e

    def _is_interesting_prop(self, prop=None):
        return True
        
    def crawl(self):
        url = self._build_search(**self._config['busqueda'])
        print url
        self._crawl_search_result(search_url=url)

    
    