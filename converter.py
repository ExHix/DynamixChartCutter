import json
import os, sys

os.chdir(sys.path[0])
def write(s):
    with open('convert.xml', 'a+', encoding='utf-8') as file:
        file.write(s + '\n')


f = open('./chart.json')
chart = json.load(f)
with open('convert.xml', 'w', encoding='utf-8') as f:
    f.write('')

xmlHead = '''<?xml version="1.0" encoding="UTF-8" ?>
<CMap xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">'''

chartData = f'<m_path>{chart["m_Name"]}</m_path>\n' \
            f'<m_barPerMin>{chart["m_barPerMin"]*1.5}</m_barPerMin>\n' \
            f'<m_timeOffset>0</m_timeOffset>\n' \
            f'<m_leftRegion>PAD</m_leftRegion>\n' \
            f'<m_rightRegion>PAD</m_rightRegion>\n' \
            f'<m_mapID>{chart["m_mapID"]}</m_mapID>\n'

write(xmlHead)
write(chartData)

tmpChart=""

def ConvertNote(jsonNoteList, sideType):
    def noteType(s):
        print(s)
        print(type(s))
        if s == "0":
            return "NORMAL"
        elif s == "1":
            return "CHAIN"
        elif s == "2":
            return "HOLD"
        elif s == "3":
            return "SUB"
        else:
            return "UNKNOWN"
    global tmpChart
    tmpChart += '<' + str(sideType) + '>\n'
    tmpChart += "<m_notes>\n"

    noteList = jsonNoteList["m_notes"]
    """i = 0
    while i < len(noteList) - 1:
        k = 0
        while k < len(noteList) - i - 1:
            if noteList[k]['m_id'] > noteList[k+1]['m_id']:
                tmp = noteList[k]
                noteList[k] = noteList[k + 1]
                noteList[k + 1] = tmp
            k += 1
        i += 1"""
    for note in noteList:
        noteData = f'<CMapNoteAsset>\n' \
                   f'<m_id>{note["m_id"]}</m_id>\n' \
                   f'<m_type>{noteType(str(note["m_type"]))}</m_type>\n' \
                   f'<m_time>{note["m_time"]*1.5}</m_time>\n' \
                   f'<m_position>{note["m_position"]}</m_position>\n' \
                   f'<m_width>{note["m_width"]}</m_width>\n' \
                   f'<m_subId>{note["m_subId"]}</m_subId>\n' \
                   f'<status>Perfect</status>\n' \
                   f'</CMapNoteAsset>\n'
        tmpChart += noteData

    tmpChart += "</m_notes>\n"
    tmpChart += '</' + str(sideType) + '>\n'


ConvertNote(chart['m_notes'], "m_notes")
ConvertNote(chart['m_notesLeft'], "m_notesLeft")
ConvertNote(chart['m_notesRight'], "m_notesRight")

write(tmpChart)
write("</CMap>")
