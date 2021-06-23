import json
from time import ctime

sections = []
with open('server_log.txt', encoding='utf-8') as f:
    section = {'time': 0., 'logs': []}
    while True:
        line = f.readline()
        if line != '':
            if line.startswith('='):
                if len(section['logs']) > 0:
                    sections.append(section)
                t = float(line.strip('=').split(':')[0])
                section = {'time': t, 'logs': []}
            else:
                section['logs'].append(json.loads(line[:-1]))
        else:
            sections.append(section)
            break

for section in sections:
    print('=' * 10 + 'New section starting at '+ ctime(section['time']))

    event_dict = {}
    for log in section['logs']:
        t = log['time']
        sid = log['sid']
        event = log['event']
        if event == 'connect':
            event_dict[sid] = []
        elif event == 'query':
            event_dict[sid].append((log['query'], log['response']))

    for sid, queries in event_dict.items():
        print(f'sid={sid}:')
        for query, response in queries:
            print(query)
        

        
