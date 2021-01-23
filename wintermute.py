# TODO:
#
# dont send empty msg
# look where to refresh after clean
# exceptios!!!(((

import glob
import shutil
import datetime
import time
from asciimatics.screen import Screen
from asciimatics.renderers import ColourImageFile
from pyrogram import Client

default_status_msg = "[F2 chat] [F10 exit]"
cur_chat = 0
chats_list = []             # [id, title/fname, msgs[], unred_msgs_cnt, unread_mntns_cnt]
cursor_pos = 0
input_text = ""
cur_time = int(time.time())

new_msgs = False

app = None
session_name = ""

while True:
    print("\nAvailable sessions:")
    sessions = glob.glob("*.session")
    for i in range(0, len(sessions)):
        print("[" + str(i) + "]: " + sessions[i][:-8])
    print("[C]: Create new session")
    print("[Q]: Quit")
    res = input("Select session: ")
    if res.isnumeric():
        if int(res) >= 0:
            if int(res) < len(sessions):
                session_name = sessions[int(res)][:-8]
                break
    elif res.lower() == "c":
        session_name = input("Enter new session name: ")
        app = Client(session_name)
        app.start()
        app.stop()
        exit()
    elif res.lower() == "q":
        exit()
app = Client(session_name)

def get_chats():
    global chats_list
    chats_list.clear()
    with app:
        for dialog in app.iter_dialogs():
            chats_list.append([dialog.chat.id, dialog.chat.title or dialog.chat.first_name, [], dialog.unread_messages_count, dialog.unread_mentions_count])

def print_borders(screen):
    tsize = shutil.get_terminal_size()
    for i in range(1, tsize.columns - 1):
        screen.print_at(chr(0x2550), i, 0)
        screen.print_at(chr(0x2550), i, tsize.lines - 1)
        screen.print_at(chr(0x2550), i, tsize.lines - 3)
    for i in range(1, tsize.lines - 1):
        screen.print_at(chr(0x2551), 0, i)
        screen.print_at(chr(0x2551), tsize.columns - 1, i)
    for i in range(1, tsize.lines - 3):
        screen.print_at(chr(0x2551), 32, i)
    screen.print_at(chr(0x2566), 32, 0)
    screen.print_at(chr(0x2569), 32, tsize.lines - 3)
    for i in range(33, tsize.columns - 1):
        screen.print_at(chr(0x2550), i, tsize.lines - 6)
    screen.print_at(chr(0x2560), 32, tsize.lines - 6)
    screen.print_at(chr(0x2563), tsize.columns - 1, tsize.lines - 6)
    screen.print_at(chr(0x2554), 0, 0)
    screen.print_at(chr(0x2557), tsize.columns - 1, 0)
    screen.print_at(chr(0x255A), 0, tsize.lines - 1)
    screen.print_at(chr(0x255D), tsize.columns - 1, tsize.lines - 1)
    screen.print_at(chr(0x2560), 0, tsize.lines - 3)
    screen.print_at(chr(0x2563), tsize.columns - 1, tsize.lines - 3)

def print_status_area(screen, text):
    tsize = shutil.get_terminal_size()
    screen.clear_buffer(2, 1, 0, 1, tsize.lines - 2, tsize.columns - 2, 1)
    screen.print_at(str(text)[:tsize.columns -2], 1, tsize.lines - 2, 2, 1, 0)

def print_chat_list(screen, chats):
    tsize = shutil.get_terminal_size()
    x = 1
    width  = x + 30
    y = 1
    height = tsize.lines - 5
    screen.clear_buffer(7, 1, 0, x, y, width, height)
    for i in range(0, min(height, len(chats))):
        unr = ""
        #if chats[i][4] > 0:
        #    unr += "@" + str(chats[i][4]) + " "
        if chats[i][3] > 0:
            unr += str(chats[i][3]) + " "
        if i == cur_chat:
            screen.print_at(unr + str(chats[i][1])[:width], x, i + 1, 7, 3, 0)
        else:
            screen.print_at(unr + str(chats[i][1])[:width], x, i + 1, 7, 1, 0)

def print_chat_area(screen):
    global cur_chat
    global chats_list
    tsize = shutil.get_terminal_size()
    x = 33
    width  = tsize.columns - x - 1
    y = 1
    height = tsize.lines - 7
    msgs_list = chats_list[cur_chat][2]
    screen.clear_buffer(7, 1, 0, x, y, width, height)
    screen.refresh()
    t_y = y + height - 1
    for i in range(0, len(msgs_list)):
        s_from = ""
        if msgs_list[i].from_user is not None:
            s_from = msgs_list[i].from_user.first_name
        else:
            s_from = msgs_list[i].chat.title
        t_str = datetime.datetime.fromtimestamp(msgs_list[i].date).strftime("%d.%m.%y %H:%M:%S") + " <" + s_from + ">: "
        if msgs_list[i].media:
            if msgs_list[i].audio:
                t_str += "[Audio]\n"
            if msgs_list[i].document:
                t_str += "[Document]\n"
            if msgs_list[i].photo:
                t_str += "[Photo]\n"
            if msgs_list[i].animation:
                t_str += "[Animation]\n"
            if msgs_list[i].sticker:
                t_str += "[Sticker]\n"
            if msgs_list[i].video:
                t_str += "[Video]\n"
            if msgs_list[i].voice:
                t_str += "[Voice]\n"
            if msgs_list[i].video_note:
                t_str += "[Video note]\n"
            if msgs_list[i].contact:
                t_str += "[Contact]\n"
            if msgs_list[i].location:
                t_str += "[Location]\n"
            if msgs_list[i].venue:
                t_str += "[Venue]\n"
            if msgs_list[i].caption:
                t_str += str(msgs_list[i].caption)
        else:
            t_str += str(msgs_list[i].text)
        t_lines = []
        while len(t_str) > width or t_str.find("\n") != -1:
            sn = t_str.find("\n", 0, width)
            if sn != -1:
                t_lines.append(t_str[:sn + 1])
                t_str = t_str[sn + 1:]
                continue
            if len(t_str) > width:
                t_lines.append(t_str[:width])
                t_str = t_str[width:]
                continue
        t_lines.append(t_str)
        for ii in range(len(t_lines) - 1, -1, -1):
            b_t_y = t_y
            try:
                if t_lines[ii].find("[Photo]") != -1:
                    with app:
                        tfile = app.download_media(msgs_list[i].photo)
                    ih = min(30,int(2*height/3))
                    renderer = ColourImageFile(screen, tfile, height=ih)
                    image, colours = renderer.rendered_text
                    t_y -= ih
                    for (j, line) in enumerate(image):
                        if t_y + j >= y:
                            screen.paint(line, x, t_y + j, colour_map=colours[j])
                if t_y < y:
                    return
            except:
                t_y = b_t_y
            screen.print_at(t_lines[ii], x, t_y, 7, 1, 0)
            t_y -= 1
            if t_y < y:
                return

def print_input_area(screen, key):
    global cursor_pos
    global input_text
    tsize = shutil.get_terminal_size()
    x = 33
    width  = tsize.columns - x - 1
    y = tsize.lines - 5
    height = 2
    refresh = False
    # -301 tab
    if key == -301:
        input_text = input_text[:cursor_pos] + "    " + input_text[cursor_pos:]
        cursor_pos += 4
        refresh = True
    # -300 backspace
    if key == -300:
        if cursor_pos > 0:
            input_text = input_text[:cursor_pos - 1] + input_text[cursor_pos:]
            cursor_pos -= 1
            refresh = True
    # -208 pgdn
    if key == -208:
        cursor_pos += 2 * width
        cursor_pos = min(len(input_text), cursor_pos)
        refresh = True
    # -207 pgup
    if key == -207:
        cursor_pos -= 2 * width
        cursor_pos = max(0, cursor_pos)
        refresh = True
    # -206 down
    if key == -206:
        cursor_pos += width
        cursor_pos = min(len(input_text), cursor_pos)
        refresh = True
    # -205 right
    if key == -205:
        if cursor_pos < len(input_text):
            cursor_pos += 1
            refresh = True
    # -204 up
    if key == -204:
        cursor_pos -= width
        cursor_pos = max(0, cursor_pos)
        refresh = True
    # -203 left
    if key == -203:
        if cursor_pos > 0:
            cursor_pos -= 1
            refresh = True
    # -201 end
    if key == -201:
        if cursor_pos < len(input_text):
            cursor_pos = len(input_text)
            refresh = True
    # -200 home
    if key == -200:
        if cursor_pos > 0:
            cursor_pos = 0
            refresh = True
    # -102 del
    if key == -102:
        if cursor_pos < len(input_text):
            input_text = input_text[:cursor_pos] + input_text[cursor_pos + 1:]
            refresh = True
    # printable chars
    if key >= 32:
        input_text = input_text[:cursor_pos] + chr(key) + input_text[cursor_pos:]
        cursor_pos += 1
        refresh = True
    # enter
    if key == 10:
        global cur_chat
        global chats_list
        with app:
            app.send_message(chats_list[cur_chat][0], input_text)
        get_msgs()
        print_chat_area(screen)
        input_text = ""
        cursor_pos = 0
        refresh = True
    if refresh:
        screen.clear_buffer(7, 1, 0, x, y, width, height)
        start_pos = 0
        while start_pos + 2 * width <= cursor_pos:
            start_pos += 2 * width
        screen.print_at(input_text[start_pos:start_pos + width], x, y, 7, 1, 0)
        if len(input_text) > start_pos + width:
            screen.print_at(input_text[start_pos + width:start_pos + 2 * width], x, y + 1, 7, 1, 0)
        if cursor_pos >= start_pos + width:
            if len(input_text) == cursor_pos:
                screen.print_at(" ", x + cursor_pos - start_pos - width, y + 1, 7, 3, 0)
            else:
                screen.print_at(input_text[cursor_pos], x + cursor_pos - start_pos - width, y + 1, 7, 3, 0)
        else:
            if len(input_text) == cursor_pos:
                screen.print_at(" ", x + cursor_pos - start_pos, y, 7, 3, 0)
            else:
                screen.print_at(input_text[cursor_pos], x + cursor_pos - start_pos, y, 7, 3, 0)
        screen.refresh()

def get_msgs():
    global cur_chat
    global chats_list
    global new_msgs
    with app:
        mm = app.get_history(chats_list[cur_chat][0], limit=50)
        if len(mm) > 0:
            if len(chats_list[cur_chat][2]) > 0:
                if mm[0] != chats_list[cur_chat][2][0]:
                    new_msgs = True
            chats_list[cur_chat][2].clear()
            chats_list[cur_chat][2] = mm
            app.read_history(chats_list[cur_chat][0])

def get_updates(screen):
    global cur_time
    global chats_list
    global new_msgs
    new_time = int(time.time())
    if new_time > cur_time + 5:
        cur_time = new_time
        get_chats()
        get_msgs()
        if new_msgs:
            new_msgs = False
            print_chat_list(screen, chats_list)
            print_chat_area(screen)
            screen.refresh()

def mainloop(screen):
    global default_status_msg
    global cur_chat
    global chats_list

    screen.clear()
    print_borders(screen)
    get_chats()
    get_msgs()
    print_chat_area(screen)
    print_chat_list(screen, chats_list)
    print_status_area(screen, default_status_msg)
    screen.refresh()

    while True:
        get_updates(screen)
        key = screen.get_key()
        if key is not None:
            print_input_area(screen, key)
        # -3 F2 select chat
        if key == -3:
            print_status_area(screen, "F2 select " + str(chats_list[cur_chat][1]))
            screen.refresh()
            while (True):
                c_key = screen.get_key()
                if c_key is not None:
                    if c_key == -3:                     # F2
                        get_msgs()
                        print_chat_area(screen)
                        print_status_area(screen, default_status_msg)
                        screen.refresh()
                        break
                    if c_key == -206:                   # down
                        if cur_chat < len(chats_list):
                            cur_chat += 1
                    if c_key == -204:                   # up
                        if cur_chat > 0:
                            cur_chat -= 1
                    print_status_area(screen, "F2 select " + str(chats_list[cur_chat][1]))
                    print_chat_list(screen, chats_list)
                    screen.refresh()
        # -11 F10 exit
        if key == -11:
            exit()

Screen.wrapper(mainloop)