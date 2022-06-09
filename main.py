import numpy as np
from sys import getsizeof

from lexer import Lexer

v = float(1.2)
print(getsizeof(v))

fizzbuzz = """
     for (int i in nums(1,101)) {
        if (mod(1,15) == 0) {
            write("FizzBuzz")
        } elif (mod(1,3) == 0) {
            write("Fizz")
        } elif (mod(1,5) == 0) {
            write("Buzz")
        } else {
            write(toStr(i))
        }
     }
"""

lexer = Lexer(fizzbuzz)
lexer.get_tokens()

