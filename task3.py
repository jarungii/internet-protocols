import socket
import ssl
import base64
import certifi

host_addr = 'smtp.yandex.ru'
port = 465

# Чтение данных из файла
with open('info.txt', 'r') as info:
    m_user_name = info.readline().strip()
    user_name = info.readline().strip()
    application_password = info.readline().strip()


def generate_random_str():
    return "boundary_askljhvaxmsvhdkl"


def request(socket, request):
    print(f"Sending request: {request.decode()}")
    socket.send(request + b'\r\n')
    recv_data = b""
    while True:
        part = socket.recv(4096)
        recv_data += part
        if b"\r\n" in part:
            break
    print(f"Server response: {recv_data.decode()}")
    return recv_data.decode()


def create_letter():
    with open('headers.txt', 'r') as file:
        letter = file.read() + '\n'

    boundary = generate_random_str()

    letter += f"Content-Type: multipart/mixed; boundary=\"{boundary}\""
    letter += '\n\n'

    letter += f'--{boundary}\n'

    with open('body.txt', 'r') as file:
        letter += 'Content-Type: text/plain; charset="utf-8"\n\n'
        letter += file.read() + '\n'

    letter += f'--{boundary}\n'

    with open('cat.jpg', 'rb') as file:
        letter += 'Content-Type: image/jpeg; name="cat.jpg"\n'
        letter += 'Content-Transfer-Encoding: base64\n'
        letter += 'Content-Disposition: attachment; filename="cat.jpg"\n\n'
        letter += base64.b64encode(file.read()).decode()

    letter += '\n'
    letter += f'--{boundary}--' + '\n.\n'
    return letter


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((host_addr, port))
    context = ssl.create_default_context(cafile=certifi.where())
    wrapped_client = context.wrap_socket(client, server_hostname=host_addr)

    print(wrapped_client.recv(1024).decode())

    print(request(wrapped_client, bytes(f"EHLO {user_name}", 'utf-8')))

    base64login = base64.b64encode(user_name.encode())
    base64password = base64.b64encode(application_password.encode())

    print(request(wrapped_client, b'AUTH LOGIN'))
    print(request(wrapped_client, base64login))
    print(request(wrapped_client, base64password))

    sender = f'MAIL FROM:<{user_name}@yandex.ru>'
    recipient = f'RCPT TO:<{m_user_name}@mail.ru>'

    print(request(wrapped_client, bytes(sender, 'utf-8')))
    print(request(wrapped_client, bytes(recipient, 'utf-8')))

    print(request(wrapped_client, b'DATA'))

    letter = create_letter()

    print(request(wrapped_client, bytes(letter, 'utf-8')))
    print(request(wrapped_client, b'QUIT'))
