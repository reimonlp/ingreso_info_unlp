import datetime
import re
from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/buscar", methods=['POST'])
def buscar():
    if request.method == 'POST':
        print(request.form['inputComision'])
        binario = comi2bin(request.form['inputComision'].upper())
        if not binario:
            return redirect(f'/', 302)
            pass
        else:
            return redirect(f'/c/{binario}', 302)
    return redirect(f'/', 302)


@app.route("/c/<string:binario>", methods=['GET'])
def search(binario):
    return render_template('buscar.html', binario=binario, comision=bin2comi(binario), events=ren_events(binario))


materias = [None, 'MAT0', 'EPA', 'COC']
dias = ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes')
horarios = (['08:30 a 10:30', '08:00 a 10:00'], ['11:30 a 13:30', '12:00 a 14:00'],
            ['14:30 a 16:30', '14:00 a 16:00'], ['17:30 a 19:30', '18:30 a 20:30'])
grilla = [
    [  # LUNES
        ((1, 0, ['0000'], ['0100']), (2, 0, ['0001'], ['0101']), (2, 1, [], ['0010', '0011', '0110', '0111'])),
        ((1, 0, ['0001'], ['0101']), (2, 0, ['0000'], ['0100']), (3, 1, [], ['0010', '0011', '0110', '0111'])),
        ((1, 0, ['1000'], ['1100']), (2, 0, ['1001'], ['1101']), (2, 1, [], ['1010', '1011', '1110', '1111'])),
        ((1, 0, ['1001'], ['1101']), (2, 0, ['1000'], ['1100']), (3, 1, [], ['1010', '1011', '1110', '1111'])),
    ], [  # MARTES
        ((1, 0, ['0010'], ['0110']), (2, 0, ['0011'], ['0111']), (3, 1, [], ['0000', '0001', '0100', '0101'])),
        ((1, 0, ['0011'], ['0111']), (2, 0, ['0010'], ['0110']), (1, 1, [], ['0000', '0001', '0100', '0101'])),
        ((1, 0, ['1010'], ['1110']), (2, 0, ['1011'], ['1111']), (3, 1, [], ['1000', '1001', '1100', '1101'])),
        ((1, 0, ['1010'], ['1110']), (2, 0, ['1010'], ['1110']), (1, 1, [], ['1000', '1001', '1100', '1101'])),
    ], [  # MIERCOLES
        ((3, 0, ['0000', '0001'], ['0100', '0101']), (1, 1, [], ['0010', '0011', '0110', '0111'])),
        ((3, 0, ['0010', '0011'], ['0110', '0111']), (2, 1, [], ['0000', '0001', '0100', '0101'])),
        ((3, 0, ['1000', '1001'], ['1100', '1101']), (1, 1, [], ['1010', '1011', '1110', '1111'])),
        ((3, 0, ['1010', '1011'], ['1110', '1111']), (2, 1, [], ['1000', '1001', '1100', '1101'])),
    ], [  # JUEVES
        ((1, 0, ['0100'], ['0000']), (2, 0, ['0101'], ['0001']), (2, 1, [], ['0010', '0011', '0110', '0111'])),
        ((1, 0, ['0101'], ['0001']), (2, 0, ['0100'], ['0000']), (1, 1, [], ['0010', '0011', '0110', '0111'])),
        ((1, 0, ['1100'], ['1000']), (2, 0, ['1101'], ['1001']), (2, 1, [], ['1010', '1011', '1110', '1111'])),
        ((1, 0, ['1101'], ['1001']), (2, 0, ['1100'], ['1000']), (1, 1, [], ['1010', '1011', '1110', '1111'])),
    ], [  # VIERNES
        ((1, 0, ['0110'], ['0010']), (2, 0, ['0111'], ['0011']), (1, 1, [], ['0000', '0001', '0100', '0101'])),
        ((1, 0, ['0111'], ['0011']), (2, 0, ['0110'], ['0010']), (2, 1, [], ['0000', '0001', '0100', '0101'])),
        ((1, 0, ['1110'], ['1010']), (2, 0, ['1111'], ['1011']), (1, 1, [], ['1000', '1001', '1100', '1101'])),
        ((1, 0, ['1111'], ['1011']), (2, 0, ['1110'], ['1010']), (2, 1, [], ['1000', '1001', '1100', '1101'])),
    ],
]


def ren_events(comision):
    events = ''
    try:
        weeks = 0
        date_ = datetime.date(2022, 2, 1)
        while date_ <= datetime.date(2022, 3, 4):
            wd = date_.weekday()
            if wd in range(0, 5):
                for i, h in enumerate(grilla[wd]):
                    for m in h:
                        if len(m) == 0:
                            continue
                        if comision not in m[2] and comision not in m[3]:
                            continue

                        materia = materias[m[0]]
                        horario = horarios[i][m[1]]
                        tipo = 'Teoría ' if m[1] == 1 else ''
                        imagen = ['university', 'project-diagram', 'video']
                        if comision[1:2] == '0' and weeks % 2 == 0:
                            alternancia = True
                        elif comision[1:2] == '1' and weeks % 2 != 0:
                            alternancia = True
                        else:
                            alternancia = False

                        if wd == 2 and not alternancia:
                            continue

                        if m[0] == 3 and comision in m[3]:
                            modo = '[webex]'
                            img = imagen[2]
                        elif comision in m[3]:
                            modo = '[IDEAS]'
                            img = imagen[1]
                        else:
                            modo = '[presencial]'
                            img = imagen[0]

                        events += "{" + f"title: '{tipo}{materia}', info: '{horario}<br><b>{modo}</b>', " + \
                            f"start: '2022-{date_.month:02d}-{date_.day:02d}', img: '{img}'" + "}, "

            if wd == 6:
                weeks += 1
            date_ += datetime.timedelta(days=1)

    except IndexError:
        pass
    except ValueError:
        pass
    return f'[{events}]'


def comi2bin(comision):
    valid = re.match(r'([MT])(\d{1,2})([AB])', comision)
    if not valid or not 1 <= int(valid.groups()[1]) <= 20:
        print("Comisión inválida\n")
        return False
    comi = valid.groups()

    ret = 8 if comi[0] == 'T' else 0
    ret += 4 if comi[2] == 'B' else 0

    for i in (1, 2, 3, 4):
        if i * 5 >= int(comi[1]):
            ret += i - 1
            break
    return format(ret, '04b')


def bin2comi(comision):
    comi = re.match(r'([01])([01])([01]{2})', comision).groups()
    turno = 'T' if comi[0] == '1' else 'M'
    div = 'B' if comi[1] == '1' else 'A'
    desde = '{}{:d}{}'.format(turno, int(comi[2], 2) * 5 + 1, div)
    hasta = '{}{:d}{}'.format(turno, int(comi[2], 2) * 5 + 5, div)
    return f'{desde} a {hasta}'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
    # while True:
    #     userinput = input("\nIngrese su comisión:  ").upper()
    #     a = comi2bin(userinput)
    #     if not a:
    #         continue
    #     print(f'{bin2comi(a)}: {a}')
