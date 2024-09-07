import PySimpleGUI as sg
import pandas as pd
import mysql.connector
import os

# Koneksi ke database MySQL
mysqldb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='comic'
)

mycursor = mysqldb.cursor()

sg.theme('DarkGreen3')

EXCEL_FILE = 'comic.xlsx'

# Membaca file Excel
df = pd.read_excel(EXCEL_FILE)

# Daftar genre
genres = [
    '4-Koma', 'Action', 'Adaptation', 'Adult', 'Adventure', 'Anthology', 'Award Winning', 
    'Boys\' Love', 'Bully', 'Comedy', 'Cooking', 'Crime', 'Crossdressing', 'Dark Fantasy',
    'Delinquent', 'Delinquents', 'Demon', 'Demons', 'Doujinshi', 'Drama', 'Ecchi', 'Fantasy',
    'Full Color', 'Game', 'Games', 'Gang', 'Gender Bender', 'Genderswap', 'Ghosts', 'Girls',
    'Girls\' Love', 'gore', 'gorre', 'Gyaru', 'Harem', 'Hero', 'Historical', 'Horror', 'Incest',
    'Isekai', 'Josei', 'Josei(W)', 'Leveling', 'Loli', 'Lolicon', 'Long Strip', 'Mafia', 'Magi',
    'Magic', 'Magical Girls', 'Manga', 'Manhua', 'Manhwa', 'Martial Art', 'Martial Arts', 'Mature',
    'Mecha', 'Medical', 'Military', 'Mirror', 'Modern', 'Monster Girls', 'Monsters', 'Murim',
    'Music', 'Mystery', 'Necromancer', 'Office Workers', 'Official Colored', 'One-Shot', 'Oneshot',
    'Overpowered', 'Parody', 'Pets', 'Philosophical', 'Police', 'Post-Apocalyptic', 'Project',
    'Psychological', 'Regression', 'Reincarnation', 'Revenge', 'Reverse Harem', 'Romance',
    'Royal family', 'Royalty', 'School', 'School Life', 'Sci-fi', 'Seinen', 'Seinen(M)', 'Seinin',
    'Sexual Violence', 'Shotacon', 'Shoujo', 'Shoujo Ai', 'Shoujo(G)', 'Shounen', 'Shounen Ai',
    'Shounen(B)', 'Shounn', 'Slice of Life', 'Smut', 'Sports', 'Super Power', 'Superhero',
    'Supernatural', 'Supranatural', 'Survival', 'System', 'Thriller', 'Time Travel', 'Tragedy',
    'Vampire', 'Vampires', 'Video Games', 'Villainess', 'Violence', 'Virtual Reality', 'Web Comic',
    'Webtoon', 'Webtoons', 'Wuxia', 'Yaoi', 'Yuri', 'Zombies'
]

# Layout aplikasi
Layout = [
    [sg.Text('Data Komik')],
    [sg.Text('Judul', size=(15,1)), sg.InputText(key='Judul')],
    [sg.Text('Penulis', size=(15,1)), sg.InputText(key='Penulis')],
    [sg.Text('Tgl Baca', size=(15,1)), sg.InputText(key='Tanggal Baca'),
     sg.CalendarButton('Kalender', target='Tanggal Baca', format='%Y-%m-%d')],
    [sg.Text('Genre', size=(15,1)), sg.Combo(genres, key='Genre', default_value='Action')],
    [sg.Text('Status', size=(15,1)), 
     sg.Radio('Selesai', 'status', key='selesai'),
     sg.Radio('Sedang Dibaca', 'status', key='sedang_dibaca')],
    [sg.Submit(), sg.Button('Clear'), sg.Button('Open Excel'), sg.Button('View Data'), sg.Button('Exit')]
]

def select():
    results = []
    # Mengubah query untuk mengurutkan berdasarkan tgl_baca dari yang terlama hingga terbaru
    mycursor.execute("SELECT judul, penulis, tgl_baca, genre, status FROM comic ORDER BY tgl_baca ASC, id DESC")
    for res in mycursor:
        results.append(list(res))
    
    headings = ['Judul', 'Penulis', 'Tanggal Baca', 'Genre', 'Status']

    layout2 = [
        [sg.Table(values=results,
                  headings=headings,
                  max_col_width=35,
                  auto_size_columns=True,
                  display_row_numbers=True,
                  justification='right',
                  num_rows=20,
                  key='-Table-',
                  row_height=35)]
    ]   

    window2 = sg.Window("List Data", layout2)
    event, values = window2.read()
    window2.close()

# Membuat window
window = sg.Window('Data Komik yang Dibaca', Layout)

# Fungsi untuk membersihkan input
def clear_input():
    for key in values:
        window[key]('')
    return None

# Loop untuk menangani event
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'View Data':
        select()
    if event == 'Clear':
        clear_input()    
    if event == 'Open Excel':
        os.startfile(EXCEL_FILE) 
    if event == 'Submit':
        judul = values['Judul']
        penulis = values['Penulis']
        tgl_baca = values['Tanggal Baca']
        genre = values['Genre']
        status = None
        if values.get('selesai'):
            status = 'Selesai'
        elif values.get('sedang_dibaca'):
            status = 'Sedang Dibaca'
        
        # Mengatasi tanggal kosong
        if not tgl_baca:
            tgl_baca = None

        sql = 'INSERT INTO comic (judul, penulis, tgl_baca, genre, status) VALUES (%s, %s, %s, %s, %s)'
        val = (judul, penulis, tgl_baca, genre, status)
        try:
            mycursor.execute(sql, val)
            mysqldb.commit()
            
            # Menyimpan data baru ke dataframe dan ke file Excel
            new_data = {
                'Judul': judul,
                'Penulis': penulis,
                'Tanggal Baca': tgl_baca,
                'Genre': genre,
                'Status': status
            }
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)
            sg.popup('Data Berhasil Disimpan')
        except mysql.connector.Error as err:
            sg.popup(f"Terjadi kesalahan: {err}")
        
        clear_input()

window.close()
