from flask import Flask, request, send_file, render_template
from io import BytesIO
import re

app = Flask(__name__)
BYTE_BLOCKS_AMOUNT = 3

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['exe_file']
        new_password = request.form['new_password']
        data = file.read()
        action = request.form.get('action')

        if action == 'patch':
            result_data = patch_exe(data, new_password)
        elif action == 'restore':
            result_data = restore_exe(data)
        else:
            return "Неизвестное действие", 400


        return send_file(
            BytesIO(result_data),
            as_attachment=True,
            download_name="result.exe"
        )

    return render_template('upload.html')


def find_password_block(data: bytes, pattern: bytes) -> list[int]:
    positions = []
    lines = [[-1] * 8]
    i = 0
    while True:
        if len(lines) == 3:
            break
        i = data.find(pattern, i)
        if i == -1:
            break
        i += 1
        if i != -1:
            context = data[i - 1 : i + 7]
            if context[3] == lines[-1][3] + 4:
                lines.append(context)
                positions.append(i - 1)
            else:
                lines.clear()
                lines.append(context)
                positions.clear()
                positions.append(i - 1)
    return positions

def patch_exe(data: bytes, new_password: str):
    data = bytearray(data)
    positions = find_password_block(data, b'\xC7\x44\x24')

    b = new_password.encode('utf-8')
    b += b'\x00'
    n = 4
    chunks = [b[i:i + n] for i in range(0, len(b), n)]
    print([b for b in data[positions[0]:positions[0] + 8]])
    print([b for b in data[positions[1]:positions[1] + 8]])
    print([b for b in data[positions[2]:positions[2] + 8]])
    for i in range(len(chunks)):
        for j in range(len(chunks[i])):
            data[positions[i] + n + j] = chunks[i][j]
    print(chunks)
    # for i in range(3):
    #
    # for chunk in chunks:
    #     for j in range(len(chunk)):
    #         data[positions[0] + n + j] = chunk[j]
    print([b for b in data[positions[0]:positions[0] + 8]])
    print([b for b in data[positions[1]:positions[1] + 8]])
    print([b for b in data[positions[2]:positions[2] + 8]])

    data = bytes(data)
    return data


def restore_exe(data: bytes) -> bytes:
    # TODO: здесь будет логика отката (сравнение и восстановление)
    return data


if __name__ == '__main__':
    app.run(debug=True)
