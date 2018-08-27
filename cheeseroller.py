#!/usr/bin/env python3

import random
import time

import lib

path = '/medieval/cheeseroller.phtml'
actions = ['Forward Somersault', 'Push Cheese Faster', 'Hold Cheese Steady', 'Dive Left', 'Dive Right']
log = open('cheeseroller.log', 'a')

def cheeseroller():
    np = lib.NeoPage()
    while True:
        np.get(path)
        if np.contains('Sorry, you can only play 3'):
            print('Played too much.')
            return
        last_time = 0
        if np.contains('DISTANCE TO FINISH LINE'):
            last_time = int(np.search(r'TIME TAKEN</b> : (\d+?) seconds')[1])
        else:
            # Not in game; buy cheese and play
            print('Starting new game')
            np.post(path, 'cheese_name=Spicy+Juppie', 'thingy=1')
            np.post(path, 'cheese_name=Spicy+Juppie', 'type=buy')
        won = False
        while not won:
            action = random.randint(1,5)
            print(f'Picking action {action}')
            np.post(path, 'cheese_action={action}')
            time_taken = -1
            if np.contains('DISTANCE TO FINISH LINE'):
                message = np.search(r'<hr noshade (.*?)>(.*?)<hr noshade')
                if message:
                    print(message[2])
                distance = np.search(r'DISTANCE TO FINISH LINE</b> : (\d+?)m')[1]
                time_taken = np.search(r'TIME TAKEN</b> : (\d+?) seconds')[1]
                print(f"DIST: {distance}, TIME: {time_taken}")
            elif np.contains('finish_cheese_race.gif'):
                time_taken = np.search(r'You Finished in (\d+?) seconds')[1]
                score = np.search(r'Your Score</b> : (\d+?)<br>')[1]
                rating = np.search(r'Your Rating</b> : (.+?)</center>')[1]
                print(f'Won! Time: {time_taken} sec - Score: {score} - Rating: {rating}')
                won = True
            else:
                print('Error?')
                break
            
            time_taken = int(time_taken)
            time_elapsed = time_taken - last_time
            last_time = time_taken
            log.write(f'{action},{time_elapsed}\n')

            time.sleep(0.7+random.random())

if __name__ == '__main__':
    cheeseroller()
