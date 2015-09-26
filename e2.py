#!/usr/bin/env python

import sys
from urllib.request import urlopen
import shutil
import bz2
import psycopg2
import subprocess


url = 'http://radarparlamentar.polignu.org/static/db-dump/radar.sql.bz2'
tmp = '/tmp/radar.bz2'
sql = '/tmp/radar.sql'

db_user = 'radar'
db_pass = 'radar'
db_host = '127.0.0.1'
db_name = 'radar'
 

if sys.argv[0] == 'load':
    with urlopen(url) as r, open(tmp, 'wb') as f:
        shutil.copyfileobj(r, f)
    with bz2.BZ2File(tmp, 'r') as src, open(sql, 'wb') as dst:
        shutil.copyfileobj(src, dst)
    # Ugly hack ahead. It takes some time to complete.
    db_load = 'PGPASSWORD={} /usr/bin/psql -U {} -d {} -h {} -a -f {}'.format(
            db_pass, db_user, db_name, db_host, sql)
    p = subprocess.Popen(db_load, shell=True)
    p.communicate()


db_uri = 'postgresql://{}:{}@{}/{}'.format(
        db_user, db_pass, db_host, db_name)


with psycopg2.connect(db_uri) as conn:
    cursor = conn.cursor()
    cursor.execute(
        '''
        select
            nome,
            count(modelagem_voto.legislatura_id) as abstencoes,
            t.cnt as total,
            cast(count(modelagem_voto.legislatura_id) as float) / cast(t.cnt as float) * 100.0 as perc
        from modelagem_voto
            inner join (select legislatura_id as id, count(modelagem_voto.legislatura_id) as cnt
                from modelagem_voto
                group by modelagem_voto.legislatura_id) as t
                on modelagem_voto.legislatura_id=t.id
            inner join modelagem_legislatura
                on modelagem_voto.legislatura_id=modelagem_legislatura.id
            inner join modelagem_parlamentar
                on modelagem_legislatura.parlamentar_id=modelagem_parlamentar.id
        where opcao = 'ABSTENCAO' and t.cnt > 10
        group by modelagem_voto.legislatura_id, t.cnt, nome
        order by perc desc
        limit 10''')
    print('Senadores com maiores índices de abstenção (>10 votos):')
    print ('%-16s %12s %8s %9s' % ('nome', 'Abstenções', 'Total', '%'))
    for i in cursor.fetchall():
        print('%-16s %12d %8d %f' % i)






