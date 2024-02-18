import os

for file in os.scandir('./src'):
    if file.is_file():
        with open(file.path, 'r') as oldfile:
            with open(f'./out/{file.name}', 'w') as newfile:
                for line in oldfile:
                    text = line
                    if ': _CursesWindow' in line:
                        text = text.replace(': _CursesWindow', '')
                    if ' -> _CursesWindow' in line:
                        text = text.replace(' -> _CursesWindow', '')
                    if ', _CursesWindow' in line:
                        text = text.replace(', _CursesWindow', '')
                    if 'from curses import _CursesWindow\n' in line:
                        text = text.replace('from curses import _CursesWindow\n', '')

                    newfile.write(text)
