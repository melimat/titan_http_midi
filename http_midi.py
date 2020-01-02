import requests
import json
import mido
import pyautogui

masters_dict = {
    "GrandMaster" : 1,
    "FlashMaster" : 1,
    "SwopMaster" : 1,
    "PresetMaster" : 1,
    "PlaybackMaster" : 1,
    "RateGrandMaster" : 1,
    "RateMaster" : 2,
    "BPMMaster:0" : 360,
    "BPMMaster:1" : 360,
    "BPMMaster:2" : 360,
    "BPMMaster:3" : 360,
    "SizeGrandMaster" : 1,
    "SizeMaster" : 2,
    "ABMaster" : 1
}


global ip
ip = '10.0.0.40:4430'

handles_dict = {}

for i in range(60):
    page = i
    all_faders_req = requests.get("http://" + ip + "/titan/handles/Playbacks/" + str(i))
    json_loads = json.loads(all_faders_req.content)
    for eachelement in json_loads:
        index = int(eachelement["handleLocation"]["index"])
        titan_id = int(eachelement["titanId"])
        legend = str(eachelement["Legend"])
        if len(eachelement["properties"]) > 1:
            type_of_handle = str((eachelement["properties"])[1]["Value"].split(":")[0])
            if type_of_handle == "BPMMaster":
                type_of_handle = str(eachelement["properties"][1]["Value"])
        else:
            type_of_handle = str(eachelement["type"])
        print("Legend: {0} ; Page: {1} ; Index: {2} ; Type: {3} ; TitanID: {4}".format(legend, page, index, type_of_handle, titan_id))
        handles_dict[page, index] = {"id": titan_id, "type": type_of_handle, "swop" : False, "flash" : False}

def convert_value(raw_val, max_val):
    return float(raw_val/127)*max_val

def fader_handler(page, index_of_handle, raw_value):
    properties = handles_dict[page, index_of_handle]
    print(properties)
    if (properties["type"] in masters_dict.keys()):
        value = convert_value(raw_value, masters_dict[properties["type"]])
        requests.get("http://" + ip + '/titan/script/Masters/SetMaster?titanId=' + str(properties["id"]) + '&value=' + str(value))
    else:
        value = convert_value(raw_value, 1)
        requests.get('http://' + ip + '/titan/script/Playbacks/FirePlaybackAtLevel?titanIdr=' + str(properties["id"]) + '&level='+ str(value) +'&bool=false')

def swop_handler(page, index_of_control):
    properties = handles_dict[page, index_of_control - 32]
    if (properties["swop"] == False):
        requests.get("http://" + ip + "/titan/script/Playbacks/SwopPlayback?titanId=" + str(properties["id"]))
        properties["swop"] = True
    elif (properties["swop"] == True):
        requests.get("http://" + ip + "/titan/script/Playbacks/ClearSwopPlayback?titanId=" + str(properties["id"]))
        properties["swop"] = False

def flash_handler(page, index_of_control):
    properties = handles_dict[page, index_of_control - 48]
    print(properties)
    if ((properties["type"] == "cueListHandle") and (properties["flash"] == False)):
        print("tap")
        requests.get("http://" + ip + "/titan/script/CueLists/CutNextCueToLive?titanId=" + str(properties["id"]))
        properties["flash"] = True
    elif ((properties["type"] == "cueListHandle") and (properties["flash"] == True)):
        print("nothing")
        properties["flash"] = False
    else:
        if (properties["flash"] == False):
            requests.get("http://" + ip + "/titan/script/Playbacks/FlashPlayback?titanId=" + str(properties["id"]))
            properties["flash"] = True
        elif (properties["flash"] == True):
            requests.get("http://" + ip + "/titan/script/Playbacks/ClearFlashPlayback?titanId=" + str(properties["id"]))
            properties["flash"] = False
   


page_index = 0

with mido.open_input("nanoKONTROL2 1 SLIDER/KNOB 0") as inport:
    for msg in inport:
        raw_val = msg.value
        control = int(msg.control)
        if (control == 22):
            fader_handler(page_index, 8, raw_val)
        elif (control == 23):
            fader_handler(page_index, 9, raw_val)
        elif ((control == 58) and (raw_val == 127)):
            if (page_index == 0):
                page_index = 60
            else:
                page_index -= 1
            pyautogui.click(51, 974)
        elif ((control == 58) and (raw_val == 0)):
            pass
        elif ((control == 59) and (raw_val == 127)):
            if (page_index == 60):
                page_index = 0
            else:
                page_index += 1
            pyautogui.click(50, 764)
        elif ((control == 59) and (raw_val == 0)):
            pass
        elif ((control >= 32) and (control <= 39)):
            swop_handler(page_index, control)
        elif ((control >= 42) and (control <= 55)):
            flash_handler(page_index, control)
        elif ((control >= 0) and (control <= 7)):
            fader_handler(page_index, control, raw_val)
        else:
            pass
