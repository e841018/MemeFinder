# %%
import json
import numpy as np
from time import ctime

print('cut into sections ' + '=' * 40)
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
    print(f"New section starting at {ctime(section['time'])} | {len(section['logs'])} logs")

print('group sids ' + '=' * 40)
session_dicts = []
for s, section in enumerate(sections):
    session_dict = {}
    for log in section['logs']:
        sid = log['sid']
        if sid in session_dict:
            session_dict[sid].append(log)
        else:
            session_dict[sid] = [log]
            if log['event'] != 'connect':
                assert log['event'] == 'disconnect'
    session_dicts.append(session_dict)

print('count events ' + '=' * 40)
event_types = {'connect', 'disconnect', 'query', 'start_quiz', 'submit'}
defect_sid = {}
def note(sid, description):
    if sid not in defect_sid:
        defect_sid[sid] = []
    defect_sid[sid].append(description)
sid_dict = {}
for s, session_dict in enumerate(session_dicts):
    for sid, logs in session_dict.items():
        event_dict = {
            'connect': [],
            'disconnect': [],
            'query': [],
            'start_quiz': [],
            'submit': []}
        for log in logs:
            event = log['event']
            assert event in event_types, log
            event_dict[event].append(log)
        if len(event_dict['connect']) != 1:
            note(sid, f"section {s}: len(connect) = {len(event_dict['connect'])}")
        if len(event_dict['disconnect']) != 1:
            note(sid, f"section {s}: len(disconnect) = {len(event_dict['disconnect'])}")
        if len(event_dict['start_quiz']) not in (0, 1):
            note(sid, f"section {s}: len(start_quiz) = {len(event_dict['start_quiz'])}")
        if len(event_dict['start_quiz']) == 1 and len(event_dict['submit']) == 20:
            sid_dict[sid] = (event_dict, logs)
for sid, (event_dict, logs) in sid_dict.items():
    print(f'sid = {sid} ' + '-' * 40)
    print('    ' + ctime(logs[0]['time']) + ' | '
        f"query: {len(event_dict['query']):3d} | " + 
        f"submit: {len(event_dict['submit']):2d} " )
    qids = []
    for log in logs:
        if log['event'] == 'submit':
            qids.append(log['submission'][0])
    assert qids == list(range(20))

print('calculate time and count ' + '=' * 40)
invalid_sids = {
    'xXa35Jvoc5w3mCuZAAAN',
    'S3RlB33oz9bj8lTeAAAn',
    'KvJOSHJ6A4AkY1LSAABR',
    'ag5ni0QTGMxdHY1_AAG3',
    '17lBVuqqHfDOSiLKAAGT',
}
for sid in invalid_sids:
    sid_dict.pop(sid)
t_seqs = []
q_seqs = []
for sid, (event_dict, logs) in sid_dict.items():
    if sid in defect_sid:
        print(defect_sid[sid])
    submissions = []
    for log in logs:
        event = log['event']
        if event == 'start_quiz':
            last_time = log['time']
            queries = []
        elif event == 'query':
            queries.append(log)
        elif event == 'submit':
            if log['submission'][1] == -1: # skip
                t = float('inf')
            else:
                t = log['time'] - last_time
            submissions.append((t, queries))
            last_time = log['time']
            queries = []
    spent_time = np.zeros(20)
    n_query = np.zeros(20, dtype=int)
    for i, (t, queries) in enumerate(submissions):
        spent_time[i] = t
        n_query[i] = len(queries)
    t_seqs.append(spent_time)
    q_seqs.append(n_query)
    print(f'sid = {sid} ' + '-' * 40)
    print('time  | ' + ' | '.join([f'{t:5.1f}' for t in spent_time[:10]]))
    print('query | ' + ' | '.join([f'{n:5d}' for n in n_query[:10]]))
    print('time  | ' + ' | '.join([f'{t:5.1f}' for t in spent_time[10:]]))
    print('query | ' + ' | '.join([f'{n:5d}' for n in n_query[10:]]))
    # if event == 'query':
    #     data = log['query'], log['response']
    # elif event == 'start_quiz':
    #     data = log['quiz']
    # elif event == 'submit':
    #     data = log['submission']

from matplotlib import pyplot as plt
def scatter_x_y(ax, valx, valy):
    lim = max(np.max(valx), np.max(valy)) * 1.1
    ax.set_aspect(1)
    ax.scatter(valx, valy)
    ax.plot([0, lim], [0, lim], 'k:')
    ax.set_xlim((0, lim))
    ax.set_ylim((0, lim))
    ax.set_xlabel('OCR+tag')
    ax.set_ylabel('OCR-only')

# %% figure for log
def mean_if_not_inf(seq):
    vs = []
    for v in seq[:10]:
        if v != float('inf'):
            vs.append(v)
    return np.mean(vs) if len(vs) else float('nan')
set1_times = [mean_if_not_inf(seq[:10]) for seq in t_seqs]
set2_times = [mean_if_not_inf(seq[10:]) for seq in t_seqs]
set1_skips = [np.sum(seq[:10]==float('inf')) for seq in t_seqs]
set2_skips = [np.sum(seq[10:]==float('inf')) for seq in t_seqs]
set1_qcnts = [np.mean(seq[:10]) for seq in q_seqs]
set2_qcnts = [np.mean(seq[10:]) for seq in q_seqs]

fig, axs = plt.subplots(1, 3, figsize=(10, 2.6))

scatter_x_y(axs[0], set1_times, set2_times)
axs[0].set_title('Average time spent [sec]')

scatter_x_y(axs[1], set1_qcnts, set2_qcnts)
axs[1].set_title('Average query count')

scatter_x_y(axs[2], set1_skips, set2_skips)
axs[2].set_title('Number of Skips (total 10)')
    
# %% figure for feedback spreadsheed
fb_set1_times = [1.0, 1.0, 0.5, 1.0, 0.5, 1.5, 1/3, 0.5, 0.5, 2.0, 2.0]
fb_set2_times = [1.0, 1.0, 0.5, 5.0, 1.0, 1.5, 1/6, 1.0, 0.5, 3.0, 3.0]
fb_set1_qcnts = [15.0, 2.0, 2.0, 4.0, 2.0, 2.5, 2.0, 2.0, 2.0, 4.0, 4.0]
fb_set2_qcnts = [10.0, 3.0, 2.0, 10.0, 3.0, 2.5, 1.0, 4.0, 5.0, 6.5, 5.0]
fb_set1_diffs = [4, 2, 4, 4, 2, 3, 3, 2, 1, 4, 3]
fb_set2_diffs = [3, 3, 4, 3, 4, 3, 2, 4, 1, 5, 4]
fb_set1_mfisbetter = [1, -1, 0, 1, 1, -1, -1, 1, 0, -1, 1]
fb_set2_mfisbetter = [1, -1, 0, 1, 0, -1, 0, -1, -1, -1, 1]

fig, axs = plt.subplots(1, 3, figsize=(10, 2.7))

scatter_x_y(axs[0], fb_set1_times, fb_set2_times)
axs[0].set_title('Percieved time spent [sec]')

scatter_x_y(axs[1], fb_set1_qcnts, fb_set2_qcnts)
axs[1].set_title('Percieved query count')

scatter_x_y(axs[2], fb_set1_diffs, fb_set2_diffs)
axs[2].set_title('Percieved difficulty')

print(np.mean(np.array(fb_set1_mfisbetter) > 0),
      np.mean(np.array(fb_set2_mfisbetter) > 0))
# %%
