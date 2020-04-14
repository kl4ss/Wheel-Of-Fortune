# import time
# from threading import Thread

# answer = None

# def check():
#     time.sleep(2)
#     if answer != None:
#         return
#     print("Too Slow")
#     input("Player 2  Input: ")

# Thread(target = check).start()

# answer = input("Input something: ")

from threading import Timer

# def check_exceeded_time_limit():
#     print("Times up")
#     return True

t = Timer(10.0)

t.start()  # after 30 seconds, "hello, world" will be printed
answer = input("Guess a letter, you have 10 seconds : ")
t.cancel()
print(t.is_alive())
del t

# timeout = 10
# t = Timer(timeout, print, ['Sorry, times up'])
# t.start()
# prompt = "You have %d seconds to choose the correct answer...\n" % timeout
# answer = input(prompt)
# t.cancel()
