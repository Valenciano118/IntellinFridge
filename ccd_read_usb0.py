import os 
import evdev 
from evdev import *

path = '/dev/input/by-path/pci-0000:00:14.0-usb-0:2:1.0-event-kbd'

dev = evdev.InputDevice(path)
dev.grab()
print(dev)

key_mapping = {
    #Numeros
    ecodes.KEY_0 : '0',
    ecodes.KEY_1 : '1',
    ecodes.KEY_2 : '2',
    ecodes.KEY_3 : '3',
    ecodes.KEY_4 : '4',
    ecodes.KEY_5 : '5',    
    ecodes.KEY_6 : '6',
    ecodes.KEY_7 : '7',
    ecodes.KEY_8 : '8',
    ecodes.KEY_9 : '9',

    #Letras
    ecodes.KEY_A : 'a',
    ecodes.KEY_B : 'b',
    ecodes.KEY_C : 'c',
    ecodes.KEY_D : 'd',
    ecodes.KEY_E : 'e',
    ecodes.KEY_F : 'f',
    ecodes.KEY_G : 'g',
    ecodes.KEY_H : 'h',
    ecodes.KEY_I : 'i',
    ecodes.KEY_J : 'j',
    ecodes.KEY_K : 'k',
    ecodes.KEY_L : 'l',
    ecodes.KEY_M : 'm',
    ecodes.KEY_N : 'n',
    ecodes.KEY_O : 'o',
    ecodes.KEY_P : 'p',
    ecodes.KEY_Q : 'q',
    ecodes.KEY_R : 'r',
    ecodes.KEY_S : 's',
    ecodes.KEY_T : 't',
    ecodes.KEY_U : 'u',
    ecodes.KEY_V : 'v',
    ecodes.KEY_W : 'w',
    ecodes.KEY_X : 'x',
    ecodes.KEY_Y : 'y',
    ecodes.KEY_Z : 'z',
}
       
print("File path open succesffully.")
try:
    while True:
        has_to_upper = False
        caracteres = []
        for event in dev.read_loop():
            # Si el evento es una tecla de teclado y está presionada
            if event.type == ecodes.EV_KEY and event.value == 1:
                # Si el evento está en key_mappings sabemos que tenemos un valor que podemos agregar a la lista de caracteres
                if event.code in key_mapping:
                    key = key_mapping[event.code]
                    if has_to_upper:
                        caracteres.append(key.upper())
                        has_to_upper = False
                    else:
                        caracteres.append(key)
                #TODO: Comprobar si presiona shift por cada caracter mayúscula o si por el contrario lo mantiene pulsado, porque esto nos haría cambiar el funcionamiento de la lógica de esta función

                # Si el evento es un SHIFT marcamos la variable has_to_upper a True
                if event.code in (ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT):
                    has_to_upper = True

                # Si el evento es un ENTER, entonces sabemos que ha terminado de escribir el código de barras, por tanto reseteo el valor tanto de caracteres como de has_to_upper
                if event.code == ecodes.KEY_ENTER:
                    print("El resultado es:", "".join(caracteres))
                    caracteres = []
                    has_to_upper = False
except KeyboardInterrupt:
    print("Finalizando ejecución")
    exit(0)



