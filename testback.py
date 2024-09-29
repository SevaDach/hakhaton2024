try:
    from fastapi import FastAPI, File, UploadFile, Form
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
    from pathlib import Path
    # import shutil
    import threading
    import uvicorn
    import pandas as pd
    import io
    import os
    import asyncio
    import httpx
    import random
    import string
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    from fastapi.responses import StreamingResponse
    from pipeline_wordcloud import pipeline_text
    from fastapi.staticfiles import StaticFiles

except ModuleNotFoundError:
    import os, sys
    os.system(f'{sys.executable} -m pip install -r req.txt')
    exit(0)

app = FastAPI(root_path='')

app.mount("/generated", StaticFiles(directory="generated"), name="generated")

def generate_name():
    return ''.join(random.choices(string.ascii_lowercase, k=8))

def ind_exel(n):
    result = ''
    if n == 0:
        return ''
    while n > 0:
        n -= 1  # Adjust for 0-indexed logic (Excel is 1-indexed)
        result = chr(n % 26 + 65) + result  # Convert to A-Z (65 is ASCII 'A')
        n //= 26
    return result+': '

def get_upload(file):
    f_content = file.file._file
    f_type = file.filename.split(".")[-1]
    f_name = generate_name()
    best_colormaps = ['MTC Special','viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Spectral', 'coolwarm', 'YlGnBu', 'RdYlBu', 'PuBuGn', 'hsv']
    if f_type == 'csv':
        df = pd.read_csv(f_content)
    elif f_type == 'xlsx':
        df = pd.read_excel(f_content)
    elif f_type == 'txt':
        with open(f'{f_name}.txt', 'wb') as f:
            f.write(f_content.getvalue())
        return {
            "inputs": {
                "choose color scheme of clowd": {"type": "dropdown", "items": best_colormaps, "default": "red"},
                "filter profanity": {"type": "checkbox", "default": True}
            },
            "target_id": f"{f_name}.txt",
        }
    else:
        return 0 # пиздец а не файл
    df.to_excel(f"{f_name}.xlsx", index=False, engine='openpyxl')
    
    cols = [f'{ind_exel(int(num))}{x}' for num, x in enumerate(["My info is in row"] + list(df.columns), 0)]
    # rows = len(df) не нужно пока что 
        
    return {
        "inputs": {
            "choose color scheme of clowd": {"type": "dropdown", "items": best_colormaps, "default": "red"},
            "choose column": {"type": "dropdown", "items": cols},
            "type number of row (ONLY if you use rows)": {"type": "text", "default": ""},
            "filter profanity": {"type": "checkbox", "default": True}
        },
        "target_id": f"{f_name}.xlsx"
    }

async def a_get_upload(file):
    return await asyncio.to_thread(get_upload, file)

@app.post('/rest/upload')
async def return_upload(file: UploadFile = File(...)):
    return await a_get_upload(file)



def filter_profanity(answers):
    l_words = [x for x in answers if type(x) == str] # and len(x) < 3]
    bad_words = ['анус', 'аборт', 'бздун', 'беспезды', 'бздюх', 'бля', 'блудилище', 'блядво', 'блядеха', 'блядина', 'блядистка', 'блядище', 'блядки', 'блядование', 'блядовать', 'блядовитый', 'блядовозка', 'блядолиз', 'блядоход', 'блядский', 'блядство', 'блядствовать', 'блядун', 'блядь', 'бляди', 'бляд', 'блядюга', 'блядюра', 'блядюшка', 'блядюшник', 'бордель', 'вагина', 'вафлист', 'вжопить', 'вжопиться', 'вздрачивание', 'вздрачивать', 'вздрачиваться', 'вздрочить', 'вздрочиться', 'вздрючить', 'вздрючивание', 'вздрючивать', 'взъебка', 'взъебщик', 'взъебнуть', 'вислозадая', 'влагалище', 'вхуйнуть', 'вхуйнуться', 'вхуякать', 'вхуякаться', 'вхуя', 'вхуякивать', 'вхуякиваться', 'вхуякнуть', 'вхуякнуться', 'вхуяривание', 'вхуяривать', 'вхуяриваться', 'вхуярить', 'вхуяриться', 'вхуячивание', 'вхуячивать', 'вхуячиваться', 'вхуячить', 'вхуячиться', 'вхуяшивать', 'вхуяшиваться', 'вхуяшить', 'вхуяшиться', 'въебать', 'въебаться', 'въебашивать', 'въебашиваться', 'въебашить', 'въебашиться', 'въебенивать', 'въебениваться', 'въебенить', 'въебениться', 'выблядок', 'выебанный', 'выебат', 'выебаться', 'высрать', 'высраться', 'выссать', 'выссаться', 'высераться', 'выссереть', 'говнецо', 'говнистый', 'говниться', 'говно', 'говновоз', 'говнодав', 'говноеб', 'говноед', 'говномес', 'говномер', 'говносерка', 'говнюк', 'голожопая', 'гомик', 'гомосек', 'гондон', 'гонорея', 'давалка', 'двужопник', 'дерьмо', 'дерьмоед', 'дерьмовый', 'дилдо', 'додрочить', 'додрочиться', 'доебать', 'доебаться', 'доебенивать', 'доебениваться', 'доебенить', 'доебениться', 'долбоеб', 'допиздить', 'допиздиться', 'допиздовать', 'допиздоваться', 'допиздовывать', 'допиздовываться', 'допиздохать', 'допиздохаться', 'допиздохивать', 'допиздохиваться', 'допиздошить', 'допиздошиться', 'допиздошивать', 'допиздошиваться', 'допиздюлить', 'допиздюлиться', 'допиздюливать', 'допиздюливаться', 'допиздюрить', 'допиздюриться', 'допиздюривать', 'допиздюриваться', 'допиздюхать', 'допиздюхаться', 'допиздюхивать', 'допиздюхиваться', 'допиздякать', 'допиздякаться', 'допиздякивать', 'допиздякиваться', 'допиздярить', 'допиздяриться', 'допиздяривать', 'допиздяриваться', 'допиздяхать', 'допиздяхаться', 'допиздяхивать', 'допиздяхиваться', 'допиздячить', 'допиздячиться', 'допиздячивать', 'допиздячиваться', 'допиздяшить', 'допиздяшиться', 'допиздяшивать', 'допиздяшиваться', 'допиздоболивать', 'допиздоболиваться', 'допиздоболиться', 'допиздюкать', 'допиздюкаться', 'допиздюкивать', 'допиздюкиваться', 'допизживать', 'дотрахать', 'дотрахаться', 'дохуйнуть', 'дохуякать', 'дохуякаться', 'дохуякивать', 'дохуякиваться', 'дохуяривать', 'дохуяриваться', 'дохуярить', 'дохуяриться', 'дохуячить', 'дохуячиться', 'дохуячивать', 'дохуячиваться', 'дрисня', 'дристать', 'дристун', 'дроченье', 'дрочилыцик', 'дрочить', 'дрочиться', 'дрочка', 'дрючить', 'дрючиться', 'дурак', 'дуроеб', 'выебать', 'ебало', 'ебальник', 'ебальные', 'ебальный', 'ебанатик', 'ебанашка', 'ебанутый', 'ебануть', 'ебануться', 'ебать', 'ебат', 'ебаться', 'ебатьс', 'ебитесь', 'ебло', 'еблом', 'еблысь', 'ебля', 'ебнуть', 'ебнуться', 'ебня', 'ебучий', 'заебла', 'надроченный', 'объебешь', 'поебать', 'жирнозадый', 'жопа', 'жопой', 'жопастая', 'жопоеб', 'жопенци', 'жопища', 'жопка', 'жопник', 'жополиз', 'жополизание', 'жопоногий', 'жопочка', 'жопочник', 'жопство', 'жопу', 'забздеть', 'заблядовать', 'заблядоваться', 'задница', 'задрачивать', 'задрачиваться', 'задроченный', 'задрочить', 'задрочиться', 'задрючить', 'задрючиться', 'заебанный', 'заебать', 'заебаться', 'заебательская', 'заебашивать', 'заебашиваться', 'заебашить', 'заебашиться', 'заебенивать', 'заебениваться', 'заебенить', 'заебениться', 'залупа', 'залупу', 'залупаться', 'залупенить', 'залупень', 'залупить', 'залупляться', 'залупистый', 'запиздарить', 'запизденная', 'запизденелый', 'запиздить', 'запиздиться', 'запиздоболивать', 'запиздоболиваться', 'запиздоболить', 'запиздоболиться', 'запиздовать', 'запиздоваться', 'запиздовывать', 'запиздовываться', 'запиздохать', 'запиздошить', 'запиздошиться', 'запиздошивать', 'запиздошиваться', 'запиздюкать', 'запиздюкаться', 'запиздюкивать', 'запиздюкиваться', 'запиздюлить', 'запиздюлиться', 'запиздюливать', 'запиздюливаться', 'запиздюрить', 'запиздюриться', 'запиздюривать', 'запиздюриваться', 'запиздюхать', 'запиздюхаться', 'запиздюхивать', 'запиздюхиваться', 'запиздючить', 'запиздючиться', 'запиздючивать', 'запиздючиваться', 'засранец', 'засранка', 'засранный', 'засратый', 'засрать', 'засраться', 'зассать', 'затраханный', 'затрахать', 'затрахаться', 'затрахивать', 'затрахиваться', 'захуить', 'захуйнуть', 'захуйнуться', 'захуякать', 'захуякаться', 'захуякивать', 'захуякиваться', 'захуярить', 'захуяриться', 'захуяривать', 'захуяриваться', 'захуячить', 'захуячиться', 'захуячивать', 'захуячиваться', 'захуяшить', 'захуяшиться', 'захуяшивать', 'захуяшиваться', 'злоебучий', 'издрочиться', 'измандить', 'измандиться', 'измандовать', 'измандоваться', 'измандовывать', 'измандовываться', 'изъебать', 'изъебаться', 'изъебашить', 'изъебашиться', 'изъебашивать', 'изъебашиваться', 'изъебенить', 'изъебениться', 'изъебенивать', 'изъебениваться', 'изъеб', 'испиздеться', 'испиздить', 'испражнение', 'испражняться', 'исхуякать', 'исхуякаться', 'исхуякивать', 'исхуякиваться', 'исхуярить', 'исхуяриться', 'исхуяривать', 'какать', 'какашка', 'кастрат', 'кастрировать', 'клитор', 'клоака', 'кнахт', 'кончить', 'косоебить', 'косоебиться', 'кривохуй', 'курва', 'курвиный', 'лахудра', 'лох', 'лохудра', 'лохматка', 'манда', 'мандавошка', 'мандавоха', 'мандить', 'мандиться', 'мандоватая', 'мандовать', 'мандохать', 'мандохаться', 'мандохивать', 'мандохиваться', 'мандошить', 'мастурбатор', 'минет', 'минетить', 'минетка', 'минетчик', 'минетчица', 'мозгоеб', 'мозгоебатель', 'мозгоебать', 'мозгоебка', 'мокрожопый', 'мокропиздая', 'моча', 'мочиться', 'мудак', 'мудашвили', 'мудило', 'мудильщик', 'мудистый', 'мудить', 'мудоеб', 'наебанный', 'наебка', 'наебщик', 'наебывать', 'наебываться', 'наебыш', 'набздеть', 'наблядоваться', 'надроченный', 'надрочивать', 'надрочить', 'надрочиться', 'надристать', 'наебать', 'наебаться', 'наебнуть', 'наебнуться', 'накакать', 'накакаться', 'накакивать', 'напиздить', 'напиздошить', 'напиздюрить', 'напиздюриться', 'насрать', 'насраться', 'нассать', 'нассаться', 'натрахать', 'натрахаться', 'натрахивать', 'натрахиваться', 'нахуякать', 'нахуякаться', 'нахуякивать', 'нахуякиваться', 'нахуярить', 'нахуяриться', 'нахуяриться', 'нахуяривать', 'нахуяриваться', 'нахуячить', 'нахуячиться', 'нахуячивать', 'нахуячиваться', 'нахуяшить', 'недоебанный', 'недоносок', 'неебущий', 'нищеебство', 'оебыват', 'обдристанный', 'обдристать', 'обдрочиться', 'обосранец', 'обосранная', 'обосраный', 'обосрать', 'обосраться', 'обоссанец', 'обоссаный', 'обоссать', 'обоссаться', 'обоссаться', 'обоссывать', 'обоссываться', 'обпиздить', 'обпиздиться', 'обпиздовать', 'обпиздоваться', 'обпиздовывать', 'обпиздовываться', 'обпиздохать', 'обпиздохаться', 'обпиздохивать', 'обпиздохиваться', 'обпиздошить', 'обтрахать', 'обтрахаться', 'обтрахивать', 'обтрахиваться', 'обхуярить', 'обхуяриться', 'обхуячить', 'объебать', 'объебаться', 'объебенить', 'объебнуть', 'объебон', 'одинхуй', 'однапизда', 'однохуйственно', 'оебать', 'оебашивать', 'оебашить', 'оебенивать', 'оебенить', 'опедерастить', 'опизденеть', 'опизденный', 'опизденно', 'опиздеть', 'опиздить', 'остоебеть', 'остоебенить', 'остоебенило', 'остопиздеть', 'остопиздело', 'остохуело', 'остохуеть', 'отдрачивать', 'отдрачиваться', 'отдрочить', 'отдрочиться', 'отпиздить', 'отпиздошить', 'отпиздяшить', 'отпиздяшиться', 'отпиздяшивание', 'отпиздяшивать', 'отпиздяшиваться', 'отсасывать', 'отсасываться', 'отсосать', 'отсосаться', 'оттраханная', 'оттрахать', 'оттрахаться', 'оттрахивать', 'оттрахиваться', 'отхерачить', 'отхуякать', 'отхуякаться', 'отхуякивать', 'отхуякиваться', 'отхуярить', 'отхуяриться', 'отхуяривать', 'отхуяриваться', 'отхуячить', 'отхуячиться', 'отхуячивать', 'отхуячиваться', 'отхуяшить', 'отхуяшиться', 'отхуяшивать', 'отхуяшиваться', 'отъебать', 'отъебывание', 'отъебывать', 'отъебываться', 'отъебашить', 'отъебашивание', 'отъебашивать', 'отъебашиваться', 'отъебенить', 'отъебениться', 'отъебенивать', 'отъебениваться', 'отъебнуть', 'отьебаться', 'отьебашиться', 'отьебенивание', 'отьебнуться', 'охуевать', 'охуевающий', 'охуевший', 'охуение', 'охуенно', 'охуенные', 'охуеть', 'охуительно', 'охуительный', 'охуякать', 'охуякаться', 'охуякивать', 'охуякиваться', 'охуякнуть', 'охуякнуться', 'охуярить', 'охуяриться', 'охуяривать', 'охуяриваться', 'охуячить', 'охуячиться', 'охуячивать', 'охуячиваться', 'охуяшить', 'охуяшиться', 'охуяшивать', 'охуяшиваться', 'очко', 'перднуть', 'падла', 'падлюка', 'педераст', 'педерастина', 'педерастический', 'педерастия', 'педик', 'педрило', 'пежить', 'пенис', 'пердеж', 'пердеть', 'пердун', 'перебздеть', 'передрачивать', 'передрочить', 'передрочиться', 'переебаться', 'переебашить', 'перетрахать', 'перетрахаться', 'перетрахивать', 'перетрахиваться', 'перехуйнуть', 'перехуйнуться', 'перехуякнуть', 'перехуякнуться', 'перехуякать', 'перехуякаться', 'перехуякивать', 'перехуякиваться', 'перехуярить', 'перехуяриться', 'перехуяривать', 'перехуяриваться', 'перехуячить', 'перехуячиться', 'перехуячивать', 'пидорас', 'пидор', 'пизда', 'пизданутая', 'пиздануть', 'пиздануться', 'пиздато', 'пизденка', 'пизденочка', 'пиздень', 'пизденыш', 'пиздеть', 'пиздец', 'пиздища', 'пиздобол', 'пиздовать', 'пиздолиз', 'пиздомол', 'пиздосос', 'пиздоход', 'пиздуй', 'пиздун', 'пиздюга', 'пиздюлей', 'пиздюли', 'пиздюлина', 'пиздюк', 'пиздюкать', 'пиздюкаться', 'пиздюшка', 'пиздякать', 'пиздятина', 'пиздятиной', 'пиздячий', 'писька', 'писюлек', 'плоскозадая', 'поебочка', 'поебывать', 'поебываться', 'поблудить', 'поблядовать', 'поблядушка', 'подосрать', 'подосраться', 'подоссать', 'подпиздить', 'подпиздовать', 'подпиздоваться', 'подпиздовывать', 'подпиздовываться', 'подпиздохать', 'подпиздохаться', 'подпиздохивать', 'подпиздохиваться', 'подпиздошить', 'подпиздошиться', 'подпиздошивать', 'подпиздякать', 'подпиздякаться', 'подпиздякивать', 'подпиздякиваться', 'подпиздярить', 'подпиздяриться', 'подпиздяривать', 'подпиздяриваться', 'подпиздяхать', 'подпиздяхаться', 'подпиздяхивать', 'подпиздяхиваться', 'подпиздячить', 'подпиздячиться', 'подпиздячивать', 'подпиздячиваться', 'подпиздяшить', 'подпиздяшиться', 'подпиздяшивать', 'подпиздяшиваться', 'подристывать', 'подрочить', 'подсирать', 'подхуякнуть', 'подхуякнуться', 'подхуякать', 'подхуякаться', 'подхуякивать', 'подхуякиваться', 'подхуярить', 'подхуяриться', 'подхуяривать', 'подхуяриваться', 'подхуячивать', 'подхуячиться', 'подхуячивать', 'подхуячиваться', 'подхуяшить', 'подхуяшиться', 'подхуяшивать', 'подхуяшиваться', 'подъеб', 'подъебать', 'подъебаться', 'подъебашить', 'подъебнуть', 'подъебка', 'подъебывать', 'подъябывать', 'поебанный', 'поебать', 'поебаться', 'поебень', 'поебистика', 'поебон', 'поебончик', 'попердеть', 'попердеться', 'попердывать', 'попизденная', 'попиздеть', 'попиздистее', 'попиздить', 'попиздиться', 'попиздоватей', 'попиздоболивать', 'попиздоболиваться', 'попиздоболить', 'попиздоболиться', 'попиздовать', 'попиздоваться', 'попиздовывать', 'попиздовываться', 'попиздохать', 'попиздохаться', 'попиздохивать', 'попиздохиваться', 'попиздошить', 'попиздошиться', 'попиздошивать', 'попиздошиваться', 'попиздюкать', 'попиздюкаться', 'попиздюкивать', 'попиздюкиваться', 'попиздюлить', 'попиздюлиться', 'попиздюливать', 'попиздюливаться', 'попиздюрить', 'попиздюриться', 'попиздюривать', 'попиздюриваться', 'попиздюхать', 'попиздюхаться', 'попиздюхивать', 'попиздюхиваться', 'попиздякать', 'попиздякаться', 'попиздякивать', 'попиздякиваться', 'попиздярить', 'попиздяриться', 'попиздяривать', 'попиздяриваться', 'попиздяхать', 'попиздяхаться', 'попиздяхивать', 'попиздяхиваться', 'попиздячить', 'попиздячиться', 'попиздячивать', 'попиздячиваться', 'попиздяшить', 'попиздяшиться', 'попиздяшивать', 'попиздяшиваться', 'попизживать', 'попизживаться', 'потаскун', 'потаскуха', 'потраханная', 'потрахать', 'потрахаться', 'потрахивать', 'потрахиваться', 'похер', 'похуист', 'похуякать', 'похуякаться', 'похуякивать', 'похуякиваться', 'похуярить', 'похуяриться', 'похуяривать', 'похуяриваться', 'похуячить', 'похуячиться', 'похуячивать', 'похуячиваться', 'похуяшить', 'похуяшиться', 'похуяшивать', 'похуяшиваться', 'поц', 'пошмариться', 'поябывать', 'приебать', 'приебаться', 'приебывать', 'приебываться', 'приебашить', 'приебашиться', 'приебашивать', 'приебашиваться', 'приебенить', 'приебениться', 'приебенивать', 'приебениваться', 'приебехать', 'приебехаться', 'приебехивать', 'приебехиваться', 'приебистый', 'приебурить', 'приебуриться', 'приебуривать', 'приебуриваться', 'прижопить', 'прижопывать', 'прикинуть', 'примандовать', 'примандоваться', 'примавдовывать', 'примандовываться', 'примандохать', 'примандохаться', 'примандохивать', 'примандохиваться', 'примандошить', 'примандошиться', 'примандошивать', 'примандошиваться', 'примандюкать', 'примандюкаться', 'примандюкивать', 'примандюкиваться', 'примандехать', 'примандехаться', 'примандехивать', 'примандехиваться', 'примандюлить', 'примандюлиться', 'примандюливать', 'примандюливаться', 'примандюрить', 'примандюриться', 'примандюривать', 'примандюриваться', 'примандякать', 'примандякаться', 'примандякивать', 'примандякиваться', 'примандярить', 'примандяриться', 'примандяривать', 'примандяриваться', 'примандяхать', 'примандяхаться', 'примандяхивать', 'примандяхиваться', 'примандячить', 'примандячиться', 'примандячивать', 'примандячиваться', 'примандяшить', 'примандяшиться', 'примандяшивать', 'примандяшиваться', 'примудохать', 'примудохаться', 'примудохивать', 'примудохиваться', 'примандить', 'примандиться', 'припизденный', 'припиздень', 'припиздить', 'припиздиться', 'припиздывать', 'припиздываться', 'припиздовать', 'припиздоваться', 'припиздовывать', 'припиздовываться', 'припиздохать', 'припиздохаться', 'припиздохивать', 'припиздохиваться', 'припиздошить', 'припиздошиться', 'припиздошивать', 'припиздошиваться', 'припиздюкать', 'припиздюкаться', 'припиздюкивать', 'припиздюкиваться', 'припиздюлить', 'припиздюлиться', 'припиздюливать', 'припиздюливаться', 'припиздюрить', 'припиздюриться', 'припиздюривать', 'припиздюхать', 'припиздюриваться', 'припиздюхаться', 'припиздюхивать', 'припиздюхиваться', 'припиздякать', 'припиздякаться', 'припиздякивать', 'припиздякиваться', 'припиздярить', 'припиздяриться', 'припиздяривать', 'припиздяриваться', 'припиздяхать', 'припиздяхаться', 'припиздяхивать', 'припиздяхиваться', 'припиздячить', 'припиздячиться', 'припиздячивать', 'припиздячиваться', 'припиздяшить', 'припиздяшиться', 'припиздяшивать', 'припиздяшиваться', 'припиздронить', 'припиздрониться', 'припиздронивать', 'припиздрониваться', 'припизживать', 'припизживаться', 'прихуеть', 'прихуякать', 'прихуякаться', 'прихуякивать', 'прихуякиваться', 'прихуярить', 'прихуяриться', 'прихуяривать', 'прихуяриваться', 'прихуячить', 'прихуячиться', 'прихуячивать', 'прихуячиваться', 'прихуяшить', 'прихуяшиться', 'прихуяшивать', 'прихуяшиваться', 'притрахаться', 'проблядовать', 'проблядь', 'проблядушка', 'продрачивать', 'продрачиваться', 'продрочить', 'продрочиться', 'проебать', 'проебаться', 'проебашить', 'проебашиться', 'проебашивать', 'проебашиваться', 'проебенить', 'проебениться', 'проебашивать', 'проебашиваться', 'проебывать', 'проебываться', 'пропиздить', 'пропиздиться', 'пропиздоболивать', 'пропиздоболиваться', 'пропиздоболить', 'пропиздоболиться', 'пропиздовать', 'пропиздоваться', 'пропиздовывать', 'пропиздовываться', 'пропиздохать', 'пропиздохаться', 'пропиздохивать', 'пропиздохиваться', 'пропиздошить', 'пропиздошиться', 'пропиздошивать', 'пропиздошиваться', 'пропиздюкать', 'пропиздюкаться', 'пропиздюкивать', 'пропиздюкиваться', 'пропиздюлить', 'пропиздюлиться', 'пропиздюливать', 'пропиздюливаться', 'пропиздюрить', 'пропиздюриться', 'пропиздюривать', 'пропиздюриваться', 'пропиздюхать', 'пропиздюхаться', 'пропиздюхивать', 'пропиздюхиваться', 'пропиздякать', 'пропиздякаться', 'пропиздякивать', 'пропиздякиваться', 'пропиздярить', 'пропиздяриться', 'пропиздяривать', 'пропиздяриваться', 'пропиздяхать', 'пропиздяхивать', 'пропиздяхиваться', 'пропиздячить', 'пропиздячиться', 'пропиздячивать', 'пропиздячиваться', 'пропиздяшить', 'пропиздяшиться', 'пропиздяшивать', 'пропиздяшиваться', 'пропизживать', 'пропизживаться', 'пропиздон', 'прохуякать', 'прохуякаться', 'прохуякивать', 'прохуякиваться', 'прохуярить', 'прохуяриться', 'прохуяривать', 'прохуяриваться', 'прохуячить', 'прохуячиться', 'прохуячивать', 'прохуячиваться', 'прохуяшить', 'прохуяшиться', 'прохуяшивать', 'прохуяшиваться', 'разблядоваться', 'раздрочить', 'раздрочиться', 'раззалупаться', 'разнохуйственно', 'разъебать', 'разъебаться', 'разъебашить', 'разъебашиться', 'разъебашивать', 'разъебашиваться', 'разъебенить', 'разъебениться', 'разъебенивать', 'разъебениваться', 'распиздить', 'распиздиться', 'распиздовать', 'распиздоваться', 'распиздовывать', 'распиздовываться', 'распиздохать', 'распиздохаться', 'распиздохивать', 'распиздохиваться', 'распиздошить', 'распиздошиться', 'распиздошивать', 'распиздошиваться', 'распиздон', 'распиздяй', 'расхуярить', 'расхуяриться', 'расхуяривать', 'расхуяриваться', 'расхуячить', 'расхуячиться', 'расхуячивать', 'расхуячиваться', 'сдрочить', 'сестроеб', 'сифилитик', 'сифилюга', 'скурвиться', 'смандить', 'смандиться', 'смандить', 'сперматозавр', 'спиздеть', 'стерва', 'стервоза', 'сука', 'суки', 'сукин', 'сукины', 'суходрочка', 'суходрочкой', 'сучара', 'сучий', 'сучка', 'сучье', 'схуякать', 'схуякаться', 'схуякивать', 'схуякиваться', 'схуярить', 'схуяриться', 'схуяривать', 'схуяриваться', 'схуячить', 'схуячиться', 'схуячивать', 'съебывать', 'съебываться', 'съебать', 'съебаться', 'съебашить', 'съебашиться', 'съебашивать', 'съебашиваться', 'съебенить', 'съебениться', 'съебенивать', 'тварь', 'толстожопый', 'толстозадая', 'торчило', 'траханье', 'трахать', 'трахаться', 'трахнуть', 'трахнуться', 'трепак', 'триппер', 'уебывать', 'уебываться', 'уебыш', 'ублюдок', 'уебать', 'уебашить', 'уебашивать', 'уебенить', 'уебище', 'усраться', 'усрачка', 'уссать', 'уссаться', 'ухуякать', 'ухуякаться', 'ухуякивать', 'ухуякиваться', 'ухуярить', 'ухуяриться', 'ухуяривать', 'ухуяриваться', 'ухуячить', 'ухуячиться', 'ухуячивать', 'ухуячиваться', 'ухуяшить', 'ухуяшиться', 'ухуяшивать', 'ухуяшиваться', 'фаллос', 'фекал', 'фекалий', 'фекалии', 'хер', 'херами', 'херня', 'херовина', 'херов', 'хрен', 'хреново', 'хреновое', 'хреновый', 'хуевина', 'хуев', 'хуево', 'хуевый', 'хуек', 'хуечек', 'худоебина', 'хуебень', 'хуев', 'хуева', 'хуевато', 'хуеватый', 'хуеглот', 'хуегрыз', 'хуедрыга', 'хуемудрие', 'хуемыслие', 'хуеньки', 'хуеплет', 'хуесос', 'хуета', 'хуетень', 'хуец', 'хуила', 'хуиный', 'хуистый', 'хуишко', 'хуище', 'хуи', 'хуило', 'хуйло', 'хуй', 'хуйство', 'хуйнуть', 'хуйня', 'хуйню', 'хули', 'хуюжить', 'хуюжиться', 'хуюживать', 'хуюживаться', 'хуюшки', 'хуя', 'хуяк', 'хуякать', 'хуями', 'хуярить', 'хуяриться', 'хуястый', 'хуячий', 'хуячить', 'хуячиться', 'хуяшить', 'целка', 'целку', 'целочка', 'черножопые', 'чернозадый', 'член', 'шалава', 'шлюха', 'шмара', 'шмарить', 'шмариться', 'хуйло', 'отъебись', 'отьебись', 'спам', 'мудила', 'пидарасы']
    words = [x for x in l_words if x.lower() not in bad_words]
    return words
def red_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        red_value = 255  # Maximum red value to keep it bright
        green_value = random.randint(0, 50)  # Small random value for green (to keep red dominant)
        blue_value = random.randint(0, 50)  # Small random value for blue (to keep red bright)
        return f"rgb({red_value}, {green_value}, {blue_value})"

def create_wordcloud(rating, colour, name):
    # Create a WordCloud object with the specified color
    MTC = False
    if colour == "MTC Special":
        colour = 'viridis'
        MTC = True
    wordcloud = WordCloud(width=1000, height=1000, background_color="white", colormap=colour, random_state=42).generate_from_frequencies(rating)
    if MTC:
        wordcloud.recolor(color_func=red_color_func)
    # Display the generated word cloud
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")  # No axis for cleaner look

    # Save the word cloud as a PNG file with the given name
    file_name = f"{name}.png"
    plt.savefig(f"generated/{file_name}", format="png", bbox_inches="tight")
    plt.close()

@app.post('/rest/process/')
async def return_image(request: dict):
    
    if request['target_id'].endswith('.txt'):
        answers = open(request['target_id'], 'r', encoding = 'utf8').read()
        # пайплайн чето тут ретюрн уже с картинкой
    inputs = request['inputs']
    df = pd.read_excel(request['target_id'])
   
    if inputs['choose column'] == 'My info is in row' and \
        inputs['type number of row (ONLY if you use rows)'] != '':
        answers = df.iloc[int(inputs['type number of row (ONLY if you use rows)'])]
    elif inputs['choose column'] == 'My info is in row' and \
        inputs['type number of row (ONLY if you use rows)'] == '':
        return 0 # return error - polzovatel dolbaeb
    else:
        answers = df[inputs['choose column'].split(': ')[1]]

    if inputs['filter profanity']:
        answers = filter_profanity(answers)
    else:
        answers = [x for x in answers if type(x) == str]
    # ретюрнить ансеры в пайплайн
    rating = {'suka': 1, 'kaaaaaaal':2,'pizda':3, 'ebnis':15} # await pipeline_text(answers) заглушка, с тобой делать надо, дебагер выдает ошибку:     while len(data) > 60: TypeError: object of type 'coroutine' has no len()
    os.remove(f"{request['target_id']}")

    colour = request['inputs']['choose color scheme of clowd']
    create_wordcloud(rating, colour, request['target_id'])
    return {
        "image_url": f"/generated/{request['target_id']}.png"
    }
    

app.mount("/", StaticFiles(directory="frontend",html = True), name="static")


if __name__ =='__main__':
    import uvicorn
    uvicorn.run(app, port=80)