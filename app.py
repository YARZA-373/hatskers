from flask import Flask, request, send_file, render_template, jsonify, redirect, url_for, session
from io import BytesIO
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'verysecret'
BYTE_BLOCKS_AMOUNT = 3
bdata = b""

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        new_password = request.form['new_password']
        data = bdata
        action = request.form.get('action')


        if action == 'patch':
            result_data = patch_exe(data, new_password)
            return send_file(
                BytesIO(result_data),
                as_attachment=True,
                download_name="result.exe"
            )
        elif action == 'restore':
            result_data = restore_exe(data)
            return send_file(
                BytesIO(result_data),
                as_attachment=True,
                download_name="result.exe"
            )
        elif action == 'find password':
            password = find_password(data)
            return render_template('upload.html', found_password=password)
        else:
            return "Unknown action", 400

    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload():
    global bdata
    if 'exe_file' not in request.files:
        return jsonify({'error': 'Файл не получен'}), 400

    file = request.files['exe_file']
    bdata = file.read()

    return jsonify({})


@app.route('/get_number')
def get_number():
    password = find_password(bdata)
    return jsonify({'value': password})


def find_password_block(data: bytes, pattern: bytes) -> (list[int], list[str]):
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
    return positions, lines

def find_password(data: bytes) -> str:
    positions, lines = find_password_block(data, b'\xC7\x44\x24')
    password = lines[0][4:] + lines[1][4:] + lines[2][4:]
    if (ind := password.find(b'\x00')) != -1:
        password = password[:ind]
    password = password.decode('utf-8')
    return password


def patch_exe(data: bytes, new_password: str):
    data = bytearray(data)
    positions, lines = find_password_block(data, b'\xC7\x44\x24')

    b = new_password.encode('utf-8')
    b += b'\x00'
    n = 4
    chunks = [b[i:i + n] for i in range(0, len(b), n)]
    for i in range(len(chunks)):
        for j in range(len(chunks[i])):
            data[positions[i] + n + j] = chunks[i][j]

    data = bytes(data)
    return data


def restore_exe(data: bytes):
    load_dotenv()
    default_password = "password123"
    data = patch_exe(data, default_password)
    return data


if __name__ == '__main__':
    app.run(debug=True)
