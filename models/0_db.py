# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

db.define_table('farmacia',
    Field('cnpj', length=14, required=True),
    Field('nome', required=True),
    Field('endereco', 'text', required=True),
    format='%(cnpj)s - %(nome)s'
)

db.farmacia.cnpj.requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'farmacia.cnpj')]
db.farmacia.nome.requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'farmacia.nome')]
db.farmacia.endereco.requires=IS_NOT_EMPTY()

##### adicionar campos a tabela auth para mapear a entidade 'farmaceutico'
auth.settings.extra_fields['auth_user']=[
	Field('crf'),
	Field('farmacia', 'reference farmacia')
]
#auth.settings.table_user_name.crf.requires=IS_NOT_IN_DB(db, auth.settings.table_user_name.crf)

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

#db.auth_user.crf.requires=IS_NOT_IN_DB(db, auth_user.crf)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

db.define_table('doenca_cronica',
    #Field('cid10', length=10),
    Field('nome', required=True),
    format='%(nome)s'
)

db.doenca_cronica.nome.requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'doenca_cronica.nome')]

db.define_table('alergia',
    Field('nome', required=True),
    format='%(nome)s'
)

db.alergia.nome.requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'alergia.nome')]

db.define_table('tratamento',
    Field('descricao', 'text', required=True),
    format='%(descricao)s'
)

db.tratamento.descricao.requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'tratamento.descricao')]

db.define_table('sintoma',
    #Field('cid10', length=10),
    Field('nome', required=True),
    format='%(nome)s'
)

db.sintoma.nome.requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'sintoma.nome')]

db.define_table('doenca',
    #Field('cid10', length=10),
    Field('nome', required=True),
    format='%(nome)s'
)

db.doenca.nome.requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'doenca.nome')]



db.define_table('paciente',
    Field('nome', length=100, required=True),
    Field('rg', length=12),
    Field('sexo', default='masculino'),
    Field('data_nascimento', 'date', required=True),
    Field('telefone', length=15),
    Field('celular', length=15),
    Field('email', length=100),
    Field('foto', 'upload', length=1024),
    format='%(rg)s - %(nome)s'
)

db.paciente.nome.requires=IS_NOT_EMPTY()
db.paciente.rg.requires=IS_NOT_IN_DB(db, 'paciente.rg')
db.paciente.sexo.requires=IS_IN_SET(('masculino', 'feminino'))
db.paciente.data_nascimento.requires=[IS_NOT_EMPTY(), 
	IS_DATE(format=T('%d/%m/%Y'), error_message='precisa ser DD-MM-YYYY!')]
db.paciente.email.requires=IS_EMPTY_OR(IS_EMAIL())
db.paciente.foto.requires=[IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg','png','.gif'))), 
	IS_EMPTY_OR(IS_LENGTH(1048576, 1024))]

db.define_table('paciente_has_doenca_cronica',
    Field('paciente', 'reference paciente'),
    Field('doenca_cronica', 'reference doenca_cronica')
)

# inibir duplicidade de tupla na tabela paciente_has_doenca_cronica
# testar quando estiver construindo o view
"""
db.paciente_has_doenca_cronica.doenca_cronica.requires=IS_NOT_IN_DB(
	db(db.paciente_has_doenca_cronica.paciente==request.vars.paciente), 'paciente_has_doenca_cronica.doenca_cronica'
)
"""

# facilitar operacoes na tabela paciente_has_doenca_cronica
paciente_and_doenca_cronica = (db.paciente.id==db.paciente_has_doenca_cronica.paciente) & (db.doenca_cronica.id==db.paciente_has_doenca_cronica.doenca_cronica)

db.define_table('doenca_has_sintoma',
	Field('doenca', 'reference doenca'),
	Field('sintoma', 'reference sintoma')
)

# facilitar operacoes na tabela doenca_has_sintoma
doenca_and_sintoma = (db.doenca.id==db.doenca_has_sintoma.doenca) & (db.sintoma.id==db.doenca_has_sintoma.sintoma)

db.define_table('doenca_has_tratamento',
	Field('doenca', 'reference doenca'),
	Field('tratamento', 'reference tratamento')
)

# facilitar operacoes na tabela doenca_has_tratamento
doenca_and_tratamento = (db.doenca.id==db.doenca_has_tratamento.doenca) & (db.tratamento.id==db.doenca_has_tratamento.tratamento)

db.define_table('paciente_has_alergia',
	Field('paciente', 'reference paciente'),
	Field('alergia', 'reference alergia')
)

# facilitar operacoes na tabela paciente_has_alergia
paciente_and_alergia = (db.paciente.id==db.paciente_has_alergia.paciente) & (db.alergia.id==db.paciente_has_alergia.alergia)