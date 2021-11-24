import time
from time import sleep

number = 1
while True:
    print(number)
    sleep(0.25)
    if number == 1:
        number += 1
    else:
        number -= 1


