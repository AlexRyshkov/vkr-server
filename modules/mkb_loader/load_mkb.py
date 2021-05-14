import re
from models import Diagnose
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_string = 'mysql+pymysql://root:123456@localhost:3306/vkr'
db = create_engine(db_string)
Session = sessionmaker(db)
session = Session()

p = re.compile(r'(?P<code>^[^-]*?)\s(?P<name>.*)')
diagnoses = []
f = open('mkb.csv', 'r', encoding='utf-8')
lines = f.readlines()
for i in range(1, len(lines)):
    line = lines[i]
    field = line.split(';')[1]
    match = p.search(field)
    if match is None:
        continue
    code = match.group('code')
    name = match.group('name')
    diagnoses.append(Diagnose(code=code, name=name))
session.add_all(diagnoses)
session.commit()
