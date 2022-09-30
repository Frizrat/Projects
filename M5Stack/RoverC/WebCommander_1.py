from m5stack import *
from m5ui import *
from uiflow import *
import time, hat, network
import usocket as socket

def web_page(): return """
<html>
  <head>
    <title>Commande le super robot</title>
    <meta charset="UTF-8">
    <style>
      * { text-align: center; color: white; font-family: Arial, Helvetica, sans-serif; }
      body { background-color: grey; padding: 0 10px;}
      main { background-color: black; border-radius: 10px; height: 85%; display: flex; }
      li { text-decoration: none; cursor: pointer; } h2 { font-size: 30px; }
      .commande { font-size: 100px; margin: 0 25px; position: absolute; bottom: calc(15% - 50px);}

      .deplacement h2 { margin: 10px; }
      .deplacement li { background-color: grey; height: 110px; width: 110px; display: inline-block; }
      .deplacement li.active { background-color: darkgray; }
      .haut, .bas, .centre { transform: rotate(90deg); }
      .centre { color: grey; margin: 0 -30px; }
      .bas { margin-top: -20px; }
      
      .rotation { right: 50px; margin-bottom: 25px; }
      .rotation h2 { color: red; }
      .rotation li { background-color: grey; padding: 10px; border-radius: 10px; display: inline; }
      .rotation li span { background-color: red; padding: 0 27px; border-radius: 90px; }
      .rotation li.active span { background-color: darkred; }
    </style>
    <script>
      function deplacement(li) {
        const xhr = new XMLHttpRequest();
        if (!li.className.includes('active')) {
          try {
            document.querySelector('.active').className = document.querySelector('.active').className.replace('active', '')
          } catch {}
          li.className += ' active';
          xhr.open('POST', li.getAttribute('data-url'));
        } else {
          li.className = li.className.replace('active', '');
          xhr.open('POST', '?x=0&y=0&z=0');
        }
        xhr.send()
      }
    </script>
  </head>
  <body>
    <h1>Commande le super robot</h1>
    <main>
      <div class="deplacement commande">
        <h2>Déplacement</h2>
        <li data-url="?x=0&y=70&z=0" class="haut" onclick="deplacement(this)"><span><</span></li>
        <br>
        <li data-url="?x=-70&y=0&z=0" class="gauche" onclick="deplacement(this)"><span><</span></li>
        <li data-url="?x=0&y=0&z=0" class="centre" onclick="deplacement(this)"><span class="centre"><</span></li>
        <li data-url="?x=70&y=0&z=0" class="droite" onclick="deplacement(this)"><span>></span></li>
        <br>
        <li data-url="?x=0&y=-70&z=0" class="bas" onclick="deplacement(this)"><span>></span></li>
      </div>

      <div class="rotation commande">
        <h2>Rotation</h2>
        <li data-url="?x=0&y=0&z=50" onclick="deplacement(this)"><span><</span></li>
        <li data-url="?x=0&y=0&z=-50" onclick="deplacement(this)"><span>></span></li>
      </div>
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
    # selon le lien interragi avec le m5
    if '/?' in request:
        x = int(request.split("x=")[1].split("&")[0])
        y = int(request.split("y=")[1].split("&")[0])
        z = int(request.split("z=")[1].split(" ")[0])
                   
        hat_roverc1.SetSpeed(x, y, z)
    conn.send('HTTP/1.1 200 OK\n Content-Type: text/html\n Connection: close\n\n')
    conn.sendall( web_page() )
    conn.close()
