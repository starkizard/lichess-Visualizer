import chess,chess.uci,chess.svg
import lichess.api
import argparse
import io, os , shutil

import matplotlib.pyplot as plt
import numpy as np

from lichess.format import PYCHESS
from cairosvg import svg2png
from tqdm import tqdm

Username=""
GameList=[]

def parse():
    global Username
    parser=argparse.ArgumentParser()
    parser.add_argument("username")
    args= parser.parse_args()
    Username=str(args.username)

def genGames():

    global GameList
    global Username

    try:
        GameList=list(lichess.api.user_games(Username,max=10,format=PYCHESS))
    except:
        print("Wrong username")
        return 0
    if( not len(GameList)):
        print("No games found")
        return 0

    return 1

def analysis():

    engine= chess.uci.popen_engine("stockfish")
    engine.uci()
    InfoHandler=chess.uci.InfoHandler()
    engine.info_handlers.append(InfoHandler)

    count=0
    print(len(GameList))
    for game in GameList:

        if not os.path.exists('./MOVES/{}'.format(count)):
            os.makedirs('./MOVES/{}'.format(count))
        
        if not os.path.exists('./GRAPHS/{}'.format(count)):
            os.makedirs('./GRAPHS/{}'.format(count))

        ply=1
        eng,jogo,gm_lst,num_scores = [],[],[],[]    
        board = game.board()
        engine.position(board)
        inverted=False
        print("\n\nEngine is now evaluating game ",count+1)
        mainline = game.main_line()
        for move in tqdm(mainline):
            #print(move , " is the move" ,InfoHandler.info["score"] , " is the score" )
            san = board.san(move)
            board.push(move)
            engine.position(board)
            eng_aux = engine.go(movetime=100)
            eng.append( (board.san(eng_aux[0]) , InfoHandler.info["depth"] ) )
            svg2png(bytestring = chess.svg.board(board = board, size = 400, lastmove = move, flipped = inverted), write_to="MOVES/{}/{}.png".format(count, ply))
            jogo.append( (ply,san,InfoHandler.info["score"][1]) ) 
            ply+=1
            #print(ply)

        for x in jogo:
            color = x[0]&1
            if( x[2][1] == None ):
                score = x[2][0] * [1,-1][color]
                if(score>=0): score = "+" + str(score)
                else :score=str(score)

            else: score = "#{}{}".format(["-",""][color] , abs(x[2][1]))

            nta = [str(x[0]//2)+"...",str(x[0]//2 +1)+". "][color]+str(x[1])
            gm_lst.append((x[0],["Black","White"][color],nta,score))
            
            if score[0]=="#": 
                num_scores.append(99999* ([1,-1][score[1]=="-"]) )
            else: num_scores.append(int(score))
            
        

        ply =  1
        z = np.zeros(len(num_scores))
        num_scores = np.array(num_scores)
        fig = plt.figure(figsize=(4.32, 2.88))
        ax = fig.add_subplot(111)
        ax.set_facecolor("#d9d9d9")
        fig.patch.set_facecolor("#d9d9d9") 
        for x in tqdm(gm_lst):
                t = list(range(1, len(num_scores[:ply])+1, 1))
                plt.plot(t, num_scores[:ply]/100, color='black', marker='o', markersize=2)
                if abs(max(num_scores[:ply], key=abs))/100<300/100:
                        plt.ylim(-300/100, 300/100)
                else:
                        plt.ylim(-500/100, 500/100)
                plt.fill_between(t, num_scores[:ply]/100, 0, where=num_scores[:ply] >= z[:ply], facecolor='blue', interpolate=True)
                plt.fill_between(t, num_scores[:ply]/100, 0, where=num_scores[:ply] <= z[:ply], facecolor='red', interpolate=True)
                plt.xticks(np.arange(1, ply+1, 5) if ply>5 else np.arange(1, 5+1, 1))
                plt.title("Position after {}, Eval: {}".format(gm_lst[ply-1][2], num_scores[ply-1]/100))
                plt.savefig("./GRAPHS/{}/{}.png".format(count, ply), facecolor=fig.get_facecolor(), edgecolor='none')
                ply += 1




        count+=1


def deletefiles():
    shutil.rmtree("./GRAPHS")
    shutil.rmtree("./MOVES")
    os.makedirs("./GRAPHS")
    os.makedirs("./MOVES")

def startup():
    parse()
    if(genGames()):
        deletefiles()
        analysis()
    else:
        return 1

startup()

