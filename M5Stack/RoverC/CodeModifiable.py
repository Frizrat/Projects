from m5stack import *
from m5ui import *
from uiflow import *
import time, network
import usocket as socket

def web_page(): return """
<html>
  <head>
    <title>Programme le super robot</title>
    <meta charset="UTF-8">
    <style>
      * { text-align: center; font-family: Arial, Helvetica, sans-serif; }
      a { text-decoration: none; font-size: 50px; } h2 { font-size: 30px; }
      textarea { display: block; width: 100%; height: 85%; text-align: left; }
      
    </style>
    <script>
      function Code() {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', window.location.href);
        xhr.send(`codeStart:${document.querySelector('textarea').value}:codeEnd`);
        alert('Fichier monCode.py créé');
      }
    </script>
  </head>
  <body>
    <h1>Programme le super robot</h1>
    <main>
      <textarea name="code" id="code">
from m5stack import *
from m5ui import *
from uiflow import *
import time, hat, random

setScreenColor(0x030545)
hat_roverc1 = hat.get(hat.ROVERC)
label0 = M5TextBox(57, 6, "ROVER", lcd.FONT_DejaVu40, 0x01e2b1, rotate=90)

def buttonA_wasPressed():
    hat_roverc1.SetSpeed(
        0,
        int(random.randint(30, 100)),
        0,
    )
    wait(2)
    hat_roverc1.SetSpeed(0, 0, 0)

btnA.wasPressed(buttonA_wasPressed)        
      </textarea>
    </main>
    <input type="submit" value="Envoyer au robot" onclick="Code()">
  </body>
</html>
"""

setScreenColor(0x030545)
label0 = M5TextBox(57, 6, "192.168.4.1", lcd.FONT_DejaVu40, 0x01e2b1, rotate=90)

ap = network.WLAN(network.AP_IF)
ap.active(True)

# defini le nom et le mot de passe
ap.config(essid='SuperRobot')
ap.config(authmode=3, password='SuperRobot')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# defini l'url de la page et le nombre max
s.bind(('192.168.4.1',80))
s.listen(1)
while True:
    conn, addr = s.accept() # accepte la connection
    request = str(conn.recv(1024))
    if 'codeStart:' in request:
        code = request.split('codeStart:')[1].split(':codeEnd')[0]
        print(code.replace('\\n', '\n'))
        with open('apps/monCode.py', 'w+', encoding='utf-8') as w:
            w.write(code.replace('\\n', '\n'))

    conn.send('HTTP/1.1 200 OK\n Content-Type: text/html\n Connection: close\n\n')
    conn.sendall( web_page() )
    conn.close()
