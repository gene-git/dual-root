# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com
'''
Set process priority
'''
import psutil

class Prio:
    ''' set nice and ionice '''
    def __init__(self, nice:int=15, ionice_class:int=3, ionice_level:int=6):
        self.nice = nice if nice is not None else 15
        self.ionice_class = ionice_class if ionice_class is not None else 3
        self.ionice_level = ionice_level if ionice_level is not None else 6

        self.check_values()

    def set_prio(self, pid=None):
        '''
        Set the current values
        '''
        proc = psutil.Process(pid=pid)
        args = self.ionice_args()

        try:
            proc.nice(self.nice)
            proc.ionice(**args)
        except psutil.Error:
            pass

    def ionice_args(self):
        ''' 
        return dictionary psutil.ionice args
         - map ionice_class to enum 
         {ioclass=None, value=None)
        '''
        ionice_arg = {}
        match self.ionice_class:
            case 0:
                ionice_arg = {'ioclass': psutil.IOPRIO_CLASS_NONE}
            case 1:
                ionice_arg = {'ioclass': psutil.IOPRIO_CLASS_RT, 'value:': self.ionice_level}
            case 2:
                ionice_arg = {'ioclass': psutil.IOPRIO_CLASS_BE, 'value':  self.ionice_level}
            case 3:
                ionice_arg = {'ioclass': psutil.IOPRIO_CLASS_IDLE}
            case _:
                ionice_arg = {'ioclass': psutil.IOPRIO_CLASS_NONE}
        return ionice_arg

    def check_values(self):
        ''' ensure valid (io)nice values '''
        if self.nice < -20 :
            self.nice = -20
        elif self.nice > 20 :
            self.nice = 20

        if self.ionice_class < 0:
            self.ionice_class = 0
        elif self.ionice_class > 3:
            self.ionice_class = 3

        if self.ionice_level < 0:
            self.ionice_level = 9
        elif self.ionice_level > 7:
            self.ionice_level = 7
