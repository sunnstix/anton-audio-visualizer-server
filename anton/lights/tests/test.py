import socket
import time
import colorsys

_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_arduinos(packet : bytes):
    """Sends packets to light controllers."""
    for ip in ["10.0.0.248"]:
        try:
            _sock.sendto(packet,(ip, 5020))
        except Exception as e:
            print(e)
            continue
        
if __name__ == "__main__":
    repetitions = 2
    pixel_stretch = 2
    rotate = int(True)
    mirrored = int(True)
    send_arduinos(bytes.fromhex('03') + repetitions.to_bytes(1,'big') + pixel_stretch.to_bytes(1,'big') + ((mirrored << 4) + rotate).to_bytes(1,'big'))
    for i in range(0,500,2):
        r,g,b = colorsys.hls_to_rgb(i%100/100.0, 0.5, 1.0)
        r1,g1,b1 = colorsys.hls_to_rgb(i%100/100.0, 0.5, 1.0)
        time.sleep(0.1)
        send_arduinos(bytes.fromhex('04')
                      + int(r*255).to_bytes(1,'big') + int(g*255).to_bytes(1,'big')+int(b*255).to_bytes(1,'big')
                      + int(r1*255).to_bytes(1,'big') + int(g1*255).to_bytes(1,'big')+int(b1*255).to_bytes(1,'big'))
    send_arduinos(bytes.fromhex('00'))
    
    