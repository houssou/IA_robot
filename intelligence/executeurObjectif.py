from cartographie.lecteurCarte import LecteurCarte
from cartographie.chercheurChemin import ChercheurChemin
from intelligence.lecteurObjectif import LecteurObjectif
from intelligence.robot import Robot
from threading import Thread
import time
import __builtin__
import signal
import sys
import webInterface
from webInterface.interface import RunningState


def waitForFunnyAction(executeurObjectif):
    print "Funny Action thread running"
    objectifFunnyAction = None
    for objectif in executeurObjectif.listeObjectifs:
        if objectif.nom == "Funny Action":
            objectifFunnyAction = objectif
    if objectifFunnyAction == None:
        print("WARNING, no Funny Action found in objectif list. The objectif name must be \"Funny Action\"")
        return
    while executeurObjectif.robot.getRunningTime() <= executeurObjectif.matchDuration and not __builtin__.stopThread:
        if webInterface.instance and webInterface.instance.runningState != RunningState.PLAY:
            return
        time.sleep(0.5)
    if(__builtin__.stopThread):
        return
    print("Starting Funny Action... {}s".format(executeurObjectif.robot.getRunningTime()))
    objectifFunnyAction.executer(executeurObjectif.robot)

class ExecuteurObjectif:

    def __init__(self,robot,ojectifs,carte, chercheurChemin, fenetre=None):
        self.robot = robot
        self.fichierObjectifs = ojectifs
        self.fichierCarte = carte
        self.matchDuration = 100
        self.robot.matchDuration = self.matchDuration
        self.fenetre = fenetre
        self.score = 0

        chercher = chercheurChemin
        lecteurObjectif = LecteurObjectif(self.fichierObjectifs, robot, self.matchDuration)


        carte = LecteurCarte(self.fichierCarte, robot.largeur)

        self.listePointInteret  = carte.lire()
        if lecteurObjectif.tree is not None:
            self.listeObjectifs = lecteurObjectif.lire()
        else:
            self.listeObjectifs = []

    def selectionnerObjectif(self, listObjectif):
        listPossible = []
        for objectif in listObjectif:
            if objectif.nom == "Attente du GO":
                if not objectif.isFini():
                    return objectif
            elif objectif.isPossible():
                listPossible.append(objectif)
        listPossibleOrdered = sorted(listPossible, key=lambda objetcif: objectif.estimateValue())
        for objectif in listPossibleOrdered:
            if objectif.nom == "Funny Action":
                continue
            return objectif
        return None

    def executerObjectifs(self):
        #thread de funny Action
        self.funnyThread = Thread(target=waitForFunnyAction, args=(self,))
        self.funnyThread.start()

        #Mode intellingent, execution selon estimation temp/point
        listeObjectifEchoue = []
        listeObjectifs = list(self.listeObjectifs)
        while self.robot.getRunningTime() < self.matchDuration:
            objectif = self.selectionnerObjectif(listeObjectifs)
            if objectif == None:
                print("No possible objectif, looking in failed ones... ")
                listeObjectifs += listeObjectifEchoue
                listeObjectifEchoue = []
                objectif = self.selectionnerObjectif(listeObjectifs)
            if objectif == None:
                if webInterface.instance and webInterface.instance.runningState != RunningState.PLAY:
                    return
                print("No possible Objectif for the moment... time="+str(self.robot.getRunningTime())+"s")
                time.sleep(1)
                continue
            print "\n------- {} ------- {:.2f}s".format(objectif.nom, self.robot.getRunningTime())
            success=self.executerSingleObjectif(objectif)
            if webInterface.instance and webInterface.instance.runningState == RunningState.STOP:
                print "Stop requested"
                return
            if not success:  # en cas d'echec, on repousse l'objectif
                print "\t!!!warning: action impossible pour le moment, arret de l'objectif"
                # objectif.enPause()
                objectif.reset()
                listeObjectifEchoue.append(objectif)
                listeObjectifs.remove(objectif)
                break
            if success and objectif.isFini():
                self.score += objectif.getPoints()
                if self.robot:
                    self.robot.displayScore(self.score)
                if objectif.repetitions > 0:
                    objectif.repetitions -= 1
                    objectif.reset()
                else:
                    listeObjectifs.remove(objectif)  # on retire l'objectif reussi
        print "Fin du match"

    def executerSingleObjectif(self, objectif):
        while self.robot.getRunningTime() < self.matchDuration:  # tant que les actions de l'objectif n'ont pas ete faites
            if webInterface.instance and webInterface.instance.runningState == RunningState.STOP:
                print "Stop requested"
                return
            self.robot.objectifEnCours = objectif
            success = objectif.executerActionSuivante(self.robot)  # executer l'action suivante
            time.sleep(0.05)
            if (self.fenetre != None):
                self.fenetre.win.redraw()
            if not success:
                return False
            if success and objectif.isFini():
                return True
        return False


    def afficherObjectifs(self, listeObjectifs=None):
        if(listeObjectifs == None):
            listeObjectifs = self.listeObjectifs
        print "Objectifs de", self.fichierObjectifs
        i=0
        for objectif in listeObjectifs:
            i=i+1
            print i,":",objectif.nom, objectif.etat
