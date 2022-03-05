import xmltodict
import json
import os, sys
import subprocess
from decimal import Decimal


def a_speed(input_file, speed, out_file):
    try:
        cmd = "ffmpeg -y -i %s -filter_complex \"atempo=tempo=%s\" -write_xing 0 %s" % (input_file, speed, out_file)
        res = subprocess.call(cmd, shell=True)

        if res != 0:
            return False
        return True
    except Exception:
        return False

def a_intercept(input_file, str_second, duration, out_file):
    try:
        cmd = "ffmpeg -y -i %s -ss %s -t %s -write_xing 0 %s" % (input_file, str_second, duration, out_file)
        res = subprocess.call(cmd, shell=True)

        if res != 0:
            return False
        return True
    except Exception:
        return False

def xtj(content): #xml to json
    xprase = xmltodict.parse(content)
    jcontent = json.dumps(xprase, indent=1)
    return jcontent

def jtx(content): #json to xml
    return xmltodict.unparse(content)

dir = sys.path[0]+'/'
os.chdir(sys.path[0])



# Input
print("--- Dynamix Chart Spliter by MidRed ---")

# Open chart xml file
if os.path.isfile("tchart.xml"):
    xml = open("tchart.xml").read()
else:
    print(r'ERROR: Cannot find chart file.')
    print(r'Please rename the chart you want to cut as "tchart", and move the chart file to the current file directory, then restart the program.')
    chartFile = input(r'Or you can manually drag the chart file here:')
    xml = open(chartFile).read()
j = json.loads(xtj(xml))
print("Chart Name:"+j['CMap']['m_path'])


# Open music file
musicFileName = "tmusic"
isHaveTargetMusic = 0
for i in range(0,4):
    sub=['.wav','.mp3','.ogg','.flac'][i]
    if os.path.exists(dir+musicFileName+sub):
        musicFileName = musicFileName+sub
        isHaveTargetMusic = 1
        break
if not isHaveTargetMusic:
    print(r'ERROR: Cannot find music file.')
    print(r'Please rename the music you want to choose as "tmusic", and move the music file to the current file directory, then restart the program.')
    musicFile = input(r'Or you can manually drag the music file here:')
    musicFileName = os.path.basename(musicFile)
print("Music File Name:"+musicFileName)


bpm = float(j['CMap']["m_barPerMin"])*4

print("Song BPM:%f"%bpm)
print("Enter the following parameters (Number Only)")
print("Note: If one time point has multiple notes, the program will sort the notes as Middle->Left->Right, each side the notes will be sorted from left to right. Both in ascending order")
start = int(input("Start note(included):"))-1
end = int(input("End note(included):"))-1
speed = float(input("Speed(Range from 0.5x to 2x):"))
offset = float(j['CMap']['m_timeOffset'])

fileName = j['CMap']['m_path']+"-%s~%s"%(str(start+1),str(end+1))
    


# Rearrange note [priority: Time, M->L->R, Leftmost->Rightmost](ascending)
# Place the HOLD note Sub in another list
print("Reconstructing Chart...")
chart = j['CMap']
chartRe = []
chartReSub = {"m_notes":[],"m_notesLeft":[],"m_notesRight":[]}
for k in range(0,3):
    side = ['m_notes','m_notesLeft','m_notesRight'][k]
    for note in chart[side]['m_notes']['CMapNoteAsset']:
        if note["m_type"] == "SUB":
            chartReSub[side].append(note)
        struct = {
            "side":k,
            "time":float(note["m_time"]),
            "type":note["m_type"],
            "pos":float(note["m_position"]),
            "width":float(note["m_width"]),
            "subID":int(note["m_subId"])
        }
        if len(chartRe) == 0:
            chartRe.append(struct)
        else:
            chartRe.insert(0, struct)
            for i in range(0,len(chartRe)-1):
                CompNote = chartRe[i+1]
                if CompNote["time"]==struct["time"]:
                    if CompNote["side"]==struct["side"]:
                        if CompNote["pos"]>struct["pos"]:
                            chartRe[i], chartRe[i+1]=chartRe[i+1], chartRe[i]
                        else:
                            break
                    elif CompNote["side"]>struct["side"]:
                        chartRe[i], chartRe[i+1]=chartRe[i+1], chartRe[i]
                    else:
                        break
                elif CompNote["time"]<struct["time"]:
                    chartRe[i], chartRe[i+1]=chartRe[i+1], chartRe[i]
                else:
                    break


# Locate the note and create new map
print("\nGenerating Chart...")
chartRe = chartRe[start:end+1]
baseBar = chartRe[0]["time"]
endBar = chartRe[len(chartRe)-1]["time"]-baseBar
chart["m_notes"]["m_notes"]['CMapNoteAsset'].clear()
chart["m_notesLeft"]["m_notes"]['CMapNoteAsset'].clear()
chart["m_notesRight"]["m_notes"]['CMapNoteAsset'].clear()
for i in range(0,len(chartRe)):
    note = chartRe[i]
    if note["type"]=="SUB":
        # Only when meet hold note do we insert sub to avoid uncessary problems, rather than insert it directly
        continue
    side = ['m_notes','m_notesLeft','m_notesRight'][note["side"]]
    xmlNote = {
        "m_id":0,
        "m_type":note["type"],
        "m_time":note["time"]-baseBar,
        "m_position":note["pos"],
        "m_width":note["width"],
        "m_subId":note["subID"],
        "status":"Perfect"
    }
    listLen = len(chart[side]["m_notes"]['CMapNoteAsset'])
    if listLen == 0:
        chart[side]["m_notes"]['CMapNoteAsset'].append(xmlNote)
    else:
        xmlNote['m_id']=chart[side]["m_notes"]['CMapNoteAsset'][listLen-1]["m_id"]+1
        chart[side]["m_notes"]['CMapNoteAsset'].append(xmlNote)
    if xmlNote['m_type']=="HOLD":
        for sub in chartReSub[side]:
            sub["m_id"]=int(sub["m_id"])
            if sub["m_id"]==note["subID"]:
                sub["m_id"]=chart[side]["m_notes"]['CMapNoteAsset'][listLen]["m_id"]+1
                sub["m_time"]=float(sub["m_time"])-baseBar
                if sub["m_time"]>endBar:
                    sub["m_time"]=endBar
                chart[side]["m_notes"]['CMapNoteAsset'].append(sub)
                chart[side]["m_notes"]['CMapNoteAsset'][listLen]["m_subId"]=sub["m_id"]

def t2b(time):  # time to bar
    return time * Decimal(bpm) / Decimal(240.0)

def b2t(bar):   # bar to time
    return Decimal(240.0)*bar/Decimal(bpm)

# unit:s, used for cut music less at start and more at end(if can)
defaultOffset = 1

# Process music
startTime = round(float(b2t(Decimal(baseBar))), 7)
if startTime-defaultOffset>=0:
    startTime -= defaultOffset
    chart["m_timeOffset"] = round(float(Decimal(chart["m_timeOffset"])-t2b(Decimal(defaultOffset))), 7)
endTime = round(float(b2t(Decimal(baseBar+endBar))), 7) + defaultOffset
print("From:%ss to %ss"%(startTime,endTime))

print("\nGenerating Music...")
a_intercept(dir+musicFileName,str(startTime),str(endTime-startTime),dir+fileName+".mp3")
if speed-1 != 0:
    a_speed(dir+fileName+".mp3", str(speed), dir+fileName+"-%sx.mp3"%str(speed))
    os.remove(dir+fileName+".mp3")
    fileName += "-%sx"%str(speed)

# Change chart speed
if speed!=1:
    chart["m_timeOffset"]=chart["m_timeOffset"]/speed
    for k in range(0,3):
        side = ['m_notes','m_notesLeft','m_notesRight'][k]
        for i in range(0,len(chart[side]['m_notes']['CMapNoteAsset'])):
            chart[side]['m_notes']['CMapNoteAsset'][i]["m_time"]=chart[side]['m_notes']['CMapNoteAsset'][i]["m_time"]/speed

# Finish
j['CMap'] = chart
with open(fileName+".xml", "w", encoding='utf-8') as f:
    f.write(jtx(j))
print("--- Convert Successfully ---")
print("Chart file: %s.xml\nMusic file: %s.mp3\nMusic Speed: %fx"%(fileName,fileName,speed))


"""except Exception as e:
    print(e)
finally:
    os.system('pause')"""