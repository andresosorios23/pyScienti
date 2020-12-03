from bs4 import BeautifulSoup
from sjr import Journal
import pandas as pd
from hashlib import md5
import requests
import urllib3
import pickle
import glob
import os
import xlsxwriter


_SESSION = requests.Session()
revistas = pd.read_excel(r'publindex.xlsx', header = 0)
countries = ['Estados Unidos','Reino Unido','Alemania','Francia','Inglaterra','Colombia','Suiza','Pakistan','Israel','Venezuela','Países Bajos','España','Italia','Eslovenia','China'  ]
def _get_page(pagerequest):
    requests.packages.urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)
    resp = _SESSION.get(pagerequest)
    if resp.status_code == 200:
        return resp.text
    if resp.status_code == 503:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))  
    else:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))

def _get_soup(page):
    html = page
    html = html.replace(u'\xa0', u' ')
    return BeautifulSoup(html, 'html.parser')

def mix_list(list1,list2):
    aux = []
    for i in range(len(list1)):
        aux.append(list1[i])
        try:
            aux.append(list2[i])
        except:
            pass
    return aux

def publindex(ISSN):

    cat = revistas[revistas['ISSN'].str.contains(ISSN.replace('-',''),na=False)]['CATEGORIA'].values
    if len(cat):
        return cat[0]
    else:
        return 'N/C'


class Publication(object):
    def __init__(self,__data,type,group):
        self.type = type
        if self.type == 'book':
            if group:
                if 'ISSB' in __data:
                    self.Journal_ISBN = __data[__data.find('ISBN')+6:__data.find('ISSN')+15]
            else:
                info = __data.replace('\xa0','').split('"')
                self.country = ''
                for i in countries:
                    if i in info[2]:
                        info[2] = info[2].replace(i,'')
                        self.country = i

                self.authors = info[0][:-2]
                self.title = info[1]
                self.year = ''
                for i in range(1950,2020):
                    if str(i) in info[2]:
                        self.year = str(i)
                self.Book_ISBN = ''
                if 'ISSB' in __data:
                    self.Book_ISBN = __data[__data.find('ISBN')+6:__data.find('ISBN')+23]
                self.ed = info[2].split('ISBN')[0].replace(' . En: ','').replace(',','').replace('ed:','')

        elif self.type == 'paper':
            if group:
                if 'ISSN' in __data:
                    self.Journal_ISSN = __data[__data.find('ISSN')+6:__data.find('ISSN')+15]
                    self.Publindex_CAT = publindex(self.Journal_ISSN)
                
        
                info = __data.split('\n')
                self.authors = info[-2].replace('Autores: ','')
                if 'DOI' in info[1]:
                    self.doi = info[1][info[1].find('DOI')+4:]
                else:
                    self.doi = ''
                self.title = info[0].replace('Corto (Resumen): ','').replace('Publicado en revista especializada: ','')
                self.country = ''
                for i in countries:
                    if i in info[1]:
                        info[1] = info[1].replace(i,'')
                        self.country = i
                self.journal = info[1].split('ISSN')[0].replace(',','')
                self.year = str()
                for i in range(1950,2020):
                    if str(i) in info[1]:
                        self.year = str(i)
            else:
                if 'ISSN' in __data:
                    self.Journal_ISSN = __data[__data.find('ISSN')+6:__data.find('ISSN')+15]
                    self.Publindex_CAT = publindex(self.Journal_ISSN)
                elif 'ISSB' in __data:
                    self.Journal_ISBN = __data[__data.find('ISBN')+6:__data.find('ISSN')+15]
                info = __data.replace('\xa0','').split('"')
                self.country = ''
                for i in countries:
                    if i in info[2]:
                        info[2] = info[2].replace(i,'')
                        self.country = i

                self.authors = info[0][:-2]
                self.title = info[1]
                self.year = ''
                for i in range(1950,2020):
                    if str(i) in info[2]:
                        self.year = str(i)
                if 'DOI' in info[2]:
                    self.doi = info[2][info[2].find('DOI')+4:].split(' ')[0]
                else:
                    self.doi = ''
                self.journal = info[2].split('ISSN')[0].replace(' . En: ','').replace(',','')

    def pub_dict(self):
        if self.type == 'paper':
            info = {'Titulo': self.title, 'Autores':self.authors,'Año': self.year, 'Revista' : self.journal,'ISSN': self.Journal_ISSN  , 'Categoría' : self.Publindex_CAT, 'DOI' : self.doi,'País':self.country }
        else:
            info = {'Titulo': self.title, 'Autores':self.authors,'Año': self.year,'Editorial':self.ed,'ISBN': self.Book_ISBN, 'País':self.country }

        return info



class Author(object):
    def __init__(self, __data):

        self.link = get_cvlac_link(__data)
        self.html = _get_page(self.link)
        self.filled = False
        df_list = pd.read_html(self.html)
        soup = _get_soup(self.html)
        cv = {x[0]: x[1] for x in df_list[1].values.tolist()}
        if 'Nombre' in cv:
            self.name = cv['Nombre'].replace('\xa0', u' ')
        if 'Categoría' in cv:
            self.category = cv['Categoría']
        if 'Sexo' in cv:
            self.gender = cv['Sexo']
        if 'Par evaluador reconocido por Minciencias.' in cv:
            self.acknowledgment = True
        else:
            self.acknowledgment = False
        art = []
        for i in df_list:
            if i.isin(['Artículos']).values.any():
                art = i.values.tolist()
        articles_raw = list(set([x for i in art for x in i]))
        deletions = ['Artículos','Producción bibliográfica - Artículo - Publicado en revista especializada','Producción bibliográfica - Artículo - Revisión (Survey)','Producción bibliográfica - Artículo - Corto (Resumen)']
        for i in deletions:
            if i in articles_raw:
                articles_raw.remove(i)

        self.articles = list()
        for i in articles_raw:
            self.articles.append(Publication(i,'paper',False).pub_dict())

        boo = []
        for i in df_list:
            if i.isin(['Libros']).values.any():
                boo = i.values.tolist()
        book_raw = list(set([x for i in boo for x in i]))
        deletions = ['Libros','Producción bibliográfica - Libro - Libro resultado de investigación','Producción bibliográfica - Libro - Otro libro publicado','Producción bibliográfica - Libro - Libro pedagógico y/o de divulgación']

        for i in deletions:
            if i in book_raw:
                book_raw.remove(i)        
        self.books = list()
        for i in book_raw:
            self.books.append(Publication(i,'book',False).pub_dict())


    def to_xlsx(self):
        df_list = pd.read_html(self.html)
        os.makedirs('../Autores CvLAC',exist_ok=True)    


        with pd.ExcelWriter('../Autores CvLAC/'+self.name+'.xlsx', engine='xlsxwriter') as writer:
            print(self.name)
            a = pd.DataFrame()
            a['Nombre'] = [self.name]
            try:
                a['Categoria'] = [self.category]
            except:
                pass
            try:
                a['Género'] = [self.gender]
            except:
                pass
            a.to_excel(writer,sheet_name = 'Información Básica', index = False)

            a = pd.DataFrame()
            aux = []
            if len(df_list)>3:
                if df_list[2].values[0][0] == 'Formación Académica':
                    for i in df_list[2].values[1:]:
                        aux.append(i[1])
                    a['Formación Académica'] = aux
                    a.to_excel(writer,sheet_name = 'Formación Académica', index = False)

                a = pd.DataFrame(self.articles)
                if not a.empty:
                    a = a[['Titulo','Autores','Año','Revista','País','ISSN','DOI','Categoría']]  
                    a.to_excel(writer,sheet_name = 'Artículos', index = False)
                a = pd.DataFrame(self.books)
                if not a.empty:
                    a = a[['Titulo','Autores','Año','Editorial','País','ISBN']]  
                    a.to_excel(writer,sheet_name = 'Libros', index = False)

                for i in df_list[8:]:
                    if i.values[0][0] == 'Artículos' or 'Nombre del evento' or 'Libros' in i.values[0][0]:
                        pass
                    else:
                        if len(i.columns)>1:
                            i = i.iloc[:,:1]
                        auxname = i.values[0][0]
                        i.columns = [auxname]
                        i = i.iloc[1:,]
                        if len(auxname.replace('/',''))>30:
                            i.to_excel(writer,sheet_name = auxname.replace('/','').replace(':','')[:30], index = False)
                        else:
                            i.to_excel(writer,sheet_name = auxname.replace('/','')[:30], index = False)
        return self.name

    def fill(self):

        if self.filled:
            pass
        else:
            for i in self.articles:
                try:
                    i.journal = Journal(i.Journal_ISSN)
                    print(i.title)
                    print(i.journal.title)
                except:
                    pass
            self.filled = True

    def save_author(self):
        file = open('../CvLAC/' + self.link[-10:] +'.obj', 'wb')
        pickle.dump(self,file)
        

class Group(object):
    def __init__(self, __data):
        self.link = __data
        if len(self.link)<16:
            self.link = get_gruplac_link(self.link)
        self.page = _get_page(self.link)
        html = _get_soup(self.page)        
        self.name = html.find('span', class_='celdaEncabezado').text
        self.filled = False
        self.filled_authors = False
        self.auth_comp = False
        print(self.name)
        basic_data = html.find_all('table')[0].find_all('tr')[1:]

        tables = [x['href'] for x in html.find_all('table')[4].find_all('a')]
        active_raw = [x.text for x in html.find_all('table')[4].find_all('tr')[2:]]
        active = []



        self.instituciones = [x.text.replace('\n                    ','').replace('\n','')[4:] for x in mix_list(html.find_all('table')[1].find_all('td', class_ = 'celdas1'),html.find_all('table')[1].find_all('td', class_ = 'celdas0'))]
        self.instituciones.sort()
        cat = [x.find('td',class_ = 'celdasTitulo').text for x in basic_data]
        text = [x.find('td',class_ = 'celdas2').text.replace('\n                    ','').replace('\n','') for x in basic_data]
        self.data = dict()
        for index,i in enumerate(cat):
            self.data[i] = text[index]
        self.data['Clasificación'] = self.data['Clasificación'][:3].replace('c','').replace('o','')
        self.lineas_de_inv = [x.text.replace('\n                    ','').replace('\n','').split('- ')[1] for x in mix_list(html.find_all('table')[3].find_all('td', class_='celdas1'),html.find_all('table')[3].find_all('td', class_='celdas0'))]
        self.investigadores_de_interes = []
        self.plan = html.find_all('table')[2].find('td', class_='celdas1').text
        tables = [[x.text, x['href']] for x in html.find_all('table')[4].find_all('a')]
        active_raw = [x.text for x in html.find_all('table')[4].find_all('tr')[2:]]
        active = []
        for i in active_raw:
            if 'Actual' in i:
                active.append(True)
            else:
                active.append(False)
        self.investigadores = []
        for index,i in enumerate(tables):
            if active[index]:
                self.investigadores.append(i)

        

    def fill_group(self):
        html = _get_soup(self.page)
        titulos = [x.text for x in html.find_all(class_='celdaEncabezado')]
        while '' in titulos:
            titulos.remove('')
        self.produccion = []
        formacion = {}
        for index, i in enumerate(titulos[7:12]):
            formacion[i] = [x.text.split('.- ')[1].replace('  ','').split('\n')[:4] for x in mix_list(html.find_all('table')[6+index].find_all('td', class_ = 'celdas1'),html.find_all('table')[6+index].find_all('td', class_ = 'celdas0'))]
        self.produccion.append(formacion)


        prod_bibliografica = {}
        for index, i in enumerate(titulos[14:23]):
            if i == 'Artículos publicados':
                prod_bibliografica[i] = [x.text.split('.- ')[1].replace('  ','') for x in mix_list(html.find_all('table')[13+index].find_all('td', class_ = 'celdas1'),html.find_all('table')[13+index].find_all('td', class_ = 'celdas0'))]
            else:
                prod_bibliografica[i] = [x.text.split('.- ')[1].replace('  ','').split('\n') for x in mix_list(html.find_all('table')[13+index].find_all('td', class_ = 'celdas1'),html.find_all('table')[13+index].find_all('td', class_ = 'celdas0'))]
            for j in prod_bibliografica[i]:
                if isinstance(j,str):
                    pass
                else:
                    while '' in j:
                        j.remove('')
        self.produccion.append(prod_bibliografica)

        prod_tecnica = {}
        for index, i in enumerate(titulos[24:47]):
            prod_tecnica[i] = [x.text.split('.- ')[1].replace('  ','').split('\n') for x in mix_list(html.find_all('table')[23+index].find_all('td', class_ = 'celdas1'),html.find_all('table')[23+index].find_all('td', class_ = 'celdas0'))]
            for j in prod_tecnica[i]:

                while '' in j:

                    j.remove('')
        self.produccion.append(prod_tecnica)


        apropiacion_social = {}
        for index, i in enumerate(titulos[48:66]):
            
            apropiacion_social[i] = [x.text.split('.- ')[1].replace('  ','').split('\n') if (len(x.text.split('.- '))>1) else (x.text.replace('  ','').split('\n')) for x in mix_list(html.find_all('table')[47+index].find_all('td', class_ = 'celdas1'),html.find_all('table')[47+index].find_all('td', class_ = 'celdas0')) ]
            for j in apropiacion_social[i]:
                while '' in j:
                    j.remove('')
        self.produccion.append(apropiacion_social)

        actividades_formacion = {}
        for index, i in enumerate(titulos[68:71]):
            actividades_formacion[i] = [x.text.split('.- ')[1].replace('/',' ').replace('  ','').split('\n') for x in mix_list(html.find_all('table')[63+index].find_all('td', class_ = 'celdas1'),html.find_all('table')[63+index].find_all('td', class_ = 'celdas0'))]
            for j in actividades_formacion[i]:
                while '' in j:
                    j.remove('')
        self.produccion.append(actividades_formacion)

        actividades_evaluacion = {}
        for index, i in enumerate(titulos[72:]):
            actividades_evaluacion[i] = [x.text.split('.- ')[1].replace('  ','').split('\n') for x in mix_list(html.find_all('table')[67+index].find_all('td', class_ = 'celdas1'),html.find_all('table')[67+index].find_all('td', class_ = 'celdas0'))]
            for j in actividades_evaluacion[i]:
                while '' in j:
                    j.remove('')
        self.produccion.append(actividades_evaluacion)
        for index,j in enumerate(self.produccion[1]['Artículos publicados']):
            self.produccion[1]['Artículos publicados'][index] = Publication(j,'paper',True).pub_dict()

        return self
    

    def get_common_inv(self,lista_names,lista_cvlac):
        lista_names = lista_names.reset_index()
        html = _get_soup(self.page)
        tables = [x['href'] for x in html.find_all('table')[4].find_all('a')]
        active_raw = [x.text for x in html.find_all('table')[4].find_all('tr')[2:]]
        active = []
        cvlac = [get_cvlac_link(x) for x in lista_cvlac.values ]

        for i in active_raw:
            if 'Actual' in i:
                active.append(True)
            else:
                active.append(False)
        for index,i in enumerate(tables):
            if i in cvlac and active[index]:
                self.investigadores_de_interes.append(lista_names.iloc[cvlac.index(i)].values[1])
    
    def fill_authors(self):
        if self.filled_authors:
            pass
        else:
            files = glob.glob("../Autores CVLac/*.obj")
            for index,i in enumerate(self.investigadores):
                if i and '../Autores CVLac\\'+ i[1][-10:]+'.obj' not in files:
                    a = Author(i[1])
                    a.fill()
                    file = open('../Autores CVLac/' + a.link[-10:] + '.obj', 'wb')
                    pickle.dump(a,file)
                    self.investigadores[index] = a
                elif '../Autores CVLac\\'+i[1][-10:]+'.obj' in files:
                    file = open('Autores CVLac/' + i[1][-10:] + '.obj', 'rb')
                    a = pickle.load(file) 
                    self.investigadores[index] = a
                    print(self.investigadores[index].name)
                self.filled = True
    

    def to_xlsx(self):
        os.makedirs('../Informacion Grupos',exist_ok=True)
        self.fill_group()
        filename = ''.join(e for e in self.name if e.isalnum())

        with pd.ExcelWriter('../Informacion Grupos/' + filename + '.xlsx', engine='xlsxwriter') as writer:
            a = pd.DataFrame()
            name = [self.name, self.link]
            cat = [self.data['Clasificación']]
            area = [self.data['Área de conocimiento']]
            if self.investigadores_de_interes:
                int_integ = self.investigadores_de_interes
            if self.filled_authors:
                integ = [x.name for x in self.investigadores]
            else:
                integ = [x[0] for x in self.investigadores]
                cvlac = [x[1] for x in self.investigadores]
            lineas = self.lineas_de_inv.copy()
            inst = self.instituciones.copy()
            if len(lineas)>len(integ):
                while len(name) != len(lineas):
                    name.append('')
                while len(cat) != len(lineas):
                    cat.append('')
                while len(area) != len(lineas):
                    area.append('')
                while len(integ) != len(lineas):
                    integ.append('')
                while len(inst) != len(lineas):
                    inst.append('')
                while len(cvlac) != len(lineas):
                    cvlac.append('')
                if self.investigadores_de_interes:
                    while len(int_integ) != len(lineas):
                        int_integ.append('')
            else:
                while len(name) != len(integ):
                    name.append('')
                while len(cat) != len(integ):
                    cat.append('')
                while len(area) != len(integ):
                    area.append('')
                while len(lineas) != len(integ):
                    lineas.append('')
                while len(inst) != len(integ):
                    inst.append('')
                if self.investigadores_de_interes:
                    while len(int_integ) != len(integ):
                        int_integ.append('')

            a['Nombre'] = name
            a['Categoria Colciencias'] = cat
            a['Area de conocimiento'] = area
            a['Instituciones'] = inst
            a['Integrantes'] = integ
            a['CvLAC'] = cvlac
            a['Lineas'] = lineas
            if self.investigadores_de_interes:
                a['Investigadores de Interés'] = int_integ

            a.to_excel(writer,sheet_name = 'Informacion', index = False)

            for i in self.produccion:
                for j in i.keys():
                    if j == 'Artículos publicados':
                        a = pd.DataFrame(columns = list(i[j][0].keys()) )
                        for index,k in enumerate(i[j]):
                            a = a.append(k, ignore_index=True) 
                        a.to_excel(writer,sheet_name = j, index = False)



                    else:
                        if i[j]:
                            lengths = [len(x) for x in i[j]]
                            a = pd.DataFrame(columns = list((range(max(lengths)))))
                            for index,k in enumerate(i[j]):
                                while len(k)<max(lengths):
                                    k.append('')
                                a.loc[index] = k
                            if len(j) >31:
                                j = j[:31]
                            a.to_excel(writer,sheet_name = j.replace('/',' '), index = False)
        return self.name


    def save_group(self):
        file = open('../GrupLAC/' + self.link[-14:] +'.obj', 'wb')
        pickle.dump(self,file)

                 
def create_author_obj(links,xlsx):

    os.makedirs('../CvLAC',exist_ok=True)
    files = glob.glob("../CvLAC/*.obj")
    for i in links:
        try:
            if isinstance(i, float) or isinstance(i, int) or (len(str(i))<15):
                i = get_cvlac_link(i)
            if i and '../CvLAC\\'+ i[-10:]+'.obj' not in files:
                a = Author(i)
                if xlsx:
                    a.to_xlsx()
                a.save_author()
                print(a.name)
        except:
            print( 'Hay un problema con ' + i)



def create_group_obj(links,xlsx):
    """Crear los objetos de los grupos de investigación"""
    
    os.makedirs('../GrupLAC',exist_ok=True)
    files = glob.glob("../GrupLAC/*.obj")
    
    for i in links.tolist():
        try:
            if len(i)<15:
                i = get_gruplac_link(i)

            if not '../GrupLAC\\'+i[-14:]+'.obj' in files:
                a = Group(i)
                if xlsx:
                    a.to_xlsx()
                a.save_group()
        except:
            print( 'Hay un problema con ' + i)


def CVLac():
    lista = pd.read_excel(r'Lista completa.xlsx', sheet_name = 'Personal', header = 0).fillna('')

    createobj(lista['CVLac'].tolist())
    
def create_authors_xlsx():

    files = glob.glob("../CvLAC/*.obj")
    authors = []
    for i in files:
        authors.append(pickle.load(open(i,'rb')))
    a = pd.DataFrame()
    names = []
    cat = []
    for i in authors:
        try:
            cat.append(i.category)
            names.append(i.name)
        except:
            names.append(i.name)
            cat.append('N/A')

    a['Nombre'] = names
    a['Categoria'] = cat
    a.to_excel('../cvlac.xlsx', index = False)

def create_group_xlsx():
    """Si ya existen los objetos de los grupos, crear un archivo xlsx con el resumen de cada uno de ellos"""

    files = glob.glob("../GrupLAC/*.obj")
    
    for i in files:
        try:
            a = pickle.load(open(i,'rb'))
            a.to_xlsx()
        except:
            print( 'Hay un problema con ' + i)

def create_group_xlsx_com(lista_names,lista_cvlac):
    """Si ya existen los objetos de los grupos, crear un archivo xlsx con el resumen de cada uno de ellos si tienen investigadores en común con una lista"""

    files = glob.glob("../GrupLAC/*.obj")
    
    for i in files:
        try:
            a = pickle.load(open(i,'rb'))
            a.get_common_inv(lista_names,lista_cvlac)
            a.to_xlsx()
        except:
            print( 'Hay un problema con ' + i)



def create_groups_resume():
    files = glob.glob("../GrupLAC/*.obj")
    groups = []
    cate = []
    names = []
    integr = []
    institucion = []
    for i in files:
        obj = pickle.load(open(i,'rb'))
        groups.append(obj)
    with pd.ExcelWriter('../groups.xlsx') as writer:
        for i in groups:
            for j in i.instituciones:
                institucion.append(j)
                names.append(i.name)
                cate.append(i.data['Clasificación'])
                integr.append(len(i.investigadores))

            a = pd.DataFrame()
            name = [i.name]
            cat = [i.data['Clasificación']]
            area = [i.data['Área de conocimiento']]
            integ = [x[0] for x in i.investigadores]
            lineas = i.lineas_de_inv
            inst = i.instituciones
            if len(lineas)>len(integ):
                while len(name) != len(lineas):
                    name.append('')
                while len(cat) != len(lineas):
                    cat.append('')
                while len(area) != len(lineas):
                    area.append('')
                while len(integ) != len(lineas):
                    integ.append('')
                while len(inst) != len(lineas):
                    inst.append('')
            else:
                while len(name) != len(integ):
                    name.append('')
                while len(cat) != len(integ):
                    cat.append('')
                while len(area) != len(integ):
                    area.append('')
                while len(lineas) != len(integ):
                    lineas.append('')
                while len(inst) != len(integ):
                    inst.append('')

            a['Nombre'] = name
            a['Categoria Colciencias'] = cat
            a['Area de conocimiento'] = area
            a['Instituciones'] = inst
            a['integrantes'] = integ
            a['Lineas'] = lineas
            filename = ''.join(e for e in i.name if e.isalnum())
            if len(filename) >31:                
                a.to_excel(writer,sheet_name = filename[:31], index = False)
            else:
                a.to_excel(writer,sheet_name = filename, index = False)

    b = pd.DataFrame()
    b['Nombre del Grupo'] = names
    b['Categoría'] = cate
    b['Instituciones'] = institucion
    b['Investigadores'] = integr
    b.to_excel('../resumen.xlsx')

       
def get_gruplac_link(code):
    code = code.replace(' ','')
    try:
        link = 'https://sba.colciencias.gov.co/Buscador_Grupos/busqueda?q='+code
        html = _get_soup(_get_page(link))
        link = html.find('div',class_="nonblock nontext clearfix colelem").find('a')['href']
        return link
    except:
        pass

def get_cvlac_link(code):
    if isinstance(code, float) or isinstance(code, int) or (len(str(code))<15):
        code = 'https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=' + str(code)
    elif(not 'minciencias' in code):
        code = code.replace('http://scienti.colciencias.gov.co:8081/','https://scienti.minciencias.gov.co/')
        
    else:
        pass
    return code
    

create_groups_resume()