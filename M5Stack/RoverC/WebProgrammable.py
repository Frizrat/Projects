from m5stack import *
from m5ui import *
from uiflow import *
import time, hat, network
import usocket as socket

def web_page(): return """
<html>
  <head>
    <title>Programme le super robot</title>
    <meta charset="UTF-8">
    <style>
      * { text-align: center; font-family: Arial, Helvetica, sans-serif; }
      a { text-decoration: none; font-size: 50px; } h2 { font-size: 30px; }
    </style>
    <script>
      function Instruction() {
        const instru = document.querySelector('.instruction');
        var newInstru = document.createElement('div');
        newInstru.className = 'instruction';
        newInstru.innerHTML = instru.innerHTML;
        document.querySelector('main').appendChild(newInstru);
      }

      function Programme() {
        var link = '';
        for (let instruction of document.querySelectorAll('.instruction')) {
          link += instruction.querySelector('select').value;
          link += '_';
          link += instruction.querySelector('#temps').value;
          link += ';';
        }
        window.location = window.location.origin + '?programme=' + link;
      }
    </script>
  </head>
  <body>
    <h1>Programme le super robot</h1>
    <main>
      <div class="instruction">
        <select name="direction" id="direction">
          <option value="y">Avancer</option>
          <option value="x">Latéral</option>
          <option value="z">Tourner</option>
        </select>
        <br>
        <form action="temps">
          <label for="temps">Temps (0.1s à 2s)</label>
          <br>
          <input type="range" id="temps" min="100" max="2000" step="100" value="200">
        </form>
      </div>
    </main>
    <input type="submit" value="+" onclick="Instruction()">
    <br>
    <input type="submit" value="Envoyer au robot" onclick="Programme()">
  </body>
</html>
"""

setScreenColor(0x030545)
hat_roverc1 = hat.get(hat.ROVERC)
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
    conn, addr = s.accept()	# accepte la connection
    request = str(conn.recv(1024))
    if request.find('/?') == 6:
        for prog in request.split('/?')[1].split(' ')[0].split(';')[:-1]:
            x = 70 if 'x_' in prog else 0
            y = 70 if 'y_' in prog else 0
            z = 70 if 'z_' in prog else 0
            t = int(prog.split('_')[1].split(' ')[0])

            hat_roverc1.SetSpeed(x, y, z)
            time.sleep_ms(t)
            hat_roverc1.SetSpeed(0, 0, 0)

    conn.send('HTTP/1.1 200 OK\n Content-Type: text/html\n Connection: close\n\n')
    conn.sendall( web_page() )
    conn.close()
