#!/usr/bin/env python

# Author: Derrick H. Karimi
# Copyright 2014
# Unclassified

import re
import botlog


class PID:
    def __init__(self):
        self.Kp = 0
        self.Kd = 0
        self.Ki = 0
        self.initialize()

    def SetKp(self, Kp):
        self.Kp = Kp

    def SetKi(self, Ki):
        self.Ki = Ki

    def SetKd(self, Kd):
        self.Kd = Kd

    def SetPrevErr(self, preverr):
        self.prev_err = preverr

    def initialize(self):
        self.currtm = 0
        self.prevtm = self.currtm
        self.prev_err = 0
        self.Cp = 0
        self.Ci = 0
        self.Cd = 0

    def GenOut(self, error):
        """ Performs a PID computation and returns a control value based on the
        elapased time (dt) and the error signal from a summing junction. """

        self.currtm = self.currtm + 1  #get t
        dt = self.currtm - self.prevtm  #get delta t
        de = error - self.prev_err  #get delta error

        self.Cp = self.Kp * error  #proportional term
        self.Ci += error * dt  #integral term

        self.Cd = 0
        if dt > 0:  #no div by zero
            self.Cd = de / dt  #derivative term

        self.prevtm = self.currtm  #save t for next pass
        self.prev_err = error  #save t-1 error

        return self.Cp + (self.Ki * self.Ci) + (self.Kd * self.Cd)


class PIDAutoTuner():
    def __init__(self, Kp=1, Ki=1, Kd=1):
        self.pid = PID()
        self.pid.SetKp(Kp)  # proportial gain
        self.pid.SetKd(Kd)  #   derivative gain
        self.pid.SetKi(Ki)  #   integral gain

    def get_next_value(self, err):
        return self.pid.GenOut(err)


class AutoTuner():
    def __init__(
            self,
            aggressive_increase,
            initial_value,
            min_clamp,
            max_clamp,
            alpha=0.5,
            beta=5.0):

        self.min_clamp = min_clamp
        self.max_clamp = max_clamp
        self.alpha = alpha
        self.beta = beta
        self.value = initial_value
        self.old_value = initial_value
        self.aggressive_increase = aggressive_increase
        self.wins = 0
        self.losses = 0
        self.ties = 0

    def get_next_value(self, success):

        if success is None:
            self.ties + self.ties + 1
        elif success:
            self.wins = self.wins + 1
        else:
            self.losses = self.losses + 1

        if success is None:
            x = 1
        elif success and self.aggressive_increase:
            # drift down slowly
            x = 1 - (self.alpha / self.beta)
        elif not success and self.aggressive_increase:
            # drift up quikly
            x = 1 + (self.alpha * self.beta)
        elif success and not self.aggressive_increase:
            # drift up slowly
            x = 1 + (self.alpha / self.beta)
        elif not success and not self.aggressive_increase:
            # drift down quickly
            x = 1 - (self.alpha * self.beta)
        else:
            raise Exception("What is wrong with the world")

        self.old_value = self.value
        self.value = x * self.value

        if self.value < self.min_clamp:
            self.value = self.min_clamp
        if self.value > self.max_clamp:
            self.value = self.max_clamp

        return self.value

    def __str__(self):
        ratio = 0
        if (self.wins + self.losses + self.ties != 0):
            ratio = self.wins / float(self.wins + self.losses + self.ties)

        return (
            "Old Value: " + str(
                round(self.old_value, 3)) + "-> New Value: " + str(
                round(self.value, 3)) + ", record: " +
            str(self.wins) + "-" + str(self.losses) + "-" + str(self.ties)
            + ": " + str(round(ratio, 3)) + "%" )


if __name__ == "__main__":
    import random
    import time
    import sys
    import math


    best = 99999
    bestgoods = -99999

    while True:

        k1 = random.uniform(-100, 100)
        k2 = random.uniform(-100, 100)
        k3 = random.uniform(-100, 100)

        army_strength = 10000
        pirate_strength = 1000
        attack_ratio = 0.05
        at = PIDAutoTuner(k1, k2, k3)
        # at = AutoTuner(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]))
        attack_strength = 500
        avg_accuracy = None
        goods = 0
        bads = 0

        for i in range(10):
            attack_strength = attack_ratio * army_strength

            if attack_strength > pirate_strength:
                losses = 1 / 100.0
                goods = goods + 1
            else:
                losses = -1 / 100.0
                bads = bads + 1

            army_growth = 1.07
            pirate_growth = 1.05

            if attack_strength != 0:
                accuracy = (attack_strength - pirate_strength) / attack_strength

            if avg_accuracy is None:
                avg_accuracy = accuracy
            else:
                avg_accuracy = (0.5 * avg_accuracy) + (0.5 * accuracy)

            autotuner = at.get_next_value(losses)
            # print "error:", round(accuracy,3), "avg_error:", round(avg_accuracy,3), "losses:", round(losses,3), "attack_strength:", round(attack_strength,1), "pirate_strength:", round(pirate_strength,1), "attack_ratio:", attack_ratio, "autotuner:", round(autotuner,3)

            attack_ratio = autotuner
            pirate_strength = pirate_strength * pirate_growth
            army_strength = army_strength * army_growth

        if math.fabs(avg_accuracy) < math.fabs(best):
            best = avg_accuracy
            print "avg_error:", avg_accuracy, "k:", k1, k2, k3, "record:", goods, "-", bads

        if goods > bestgoods:
            bestgoods = goods
            print "avg_error:", avg_accuracy, "k:", k1, k2, k3, "record:", goods, "-", bads

        








