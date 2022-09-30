from m5stack import *
from m5ui import *
from uiflow import *
import hat, network
import usocket as socket

def web_page(): return """
<html>
  <head>
    <title>Commande le super robot</title>
    <meta charset="UTF-8">
    <style>
      * { text-align: center; font-family: Arial, Helvetica, sans-serif; }
      a { text-decoration: none; font-size: 50px; } h2 { font-size: 30px; }
      .direction { text-align: left; margin-left: 45%; width: 10%; }
      .vitesse input { width: 25%; }
    </style>
    <script>
      window.onload = (() => {
        document.querySelector('.direction').value = 'y';
        try {
          document.querySelector('.vitesse input').value = window.location.search.split('=')[1];
          document.querySelector('.direction').value = window.location.search.split('?')[1].split('=')[0];
          document.getElementById(document.querySelector('.direction').value).checked = true;
        } catch{}
      })
      function Commande() {
        const direction = document.querySelector('.direction').value;
        const valeur = document.querySelector('.vitesse input').value;
        window.location = `?${direction}=${valeur}`;
      }
    </script>
  </head>
  <body>
    <h1>Commande le super robot</h1>
    <main>
      <form class="direction" value="y">
        <input type="radio" id="x" name="axe" value="x" onclick="document.querySelector('.direction').value = 'x';">
        <label for="x">Latéral</label><br>
        <input type="radio" id="y" name="axe" value="y" onclick="document.querySelector('.direction').value = 'y';" checked>
        <label for="y">Avancer</label><br>
        <input type="radio" id="z" name="axe" value="z" onclick="document.querySelector('.direction').value = 'z';">
        <label for="z">Tourner</label>
      </form>
      
      <form class="vitesse">
        <label for="vitesse">Vitesse (0 à 100)</label>
        <br>
        <input type="range" id="vitesse" min="0" max="100" step="10" value="20" onchange="Commande()">
      </form>
      <a href="/"><span>Stop</span></a>
    </main>
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
        valeur = request.split("=")
        x = int(valeur[1].split(' ')[0]) if '?x' in valeur[0] else 0
        y = int(valeur[1].split(' ')[0]) if '?y' in valeur[0] else 0
        z = int(valeur[1].split(' ')[0]) if '?z' in valeur[0] else 0
    elif request.find('/favicon') != 6: x = 0; y = 0; z = 0
    hat_roverc1.SetSpeed(x, y, z)

    conn.send('HTTP/1.1 200 OK\n Content-Type: text/html\n Connection: close\n\n')
    conn.sendall( web_page() )
    conn.close()
