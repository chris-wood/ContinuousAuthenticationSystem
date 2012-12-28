'''
File: Profile.py
Author: Nate Smith (originally StatObj class)
Contributor: Christopher Wood, caw4567@rit.edu
'''

class Profile(object):
    '''
    A class for storing stats per character
    '''
    count = 0
    mean = 0
    m2 = 0  # second moment 
    variance = None
    std_dev = None

    def update(self, x):
        '''
        Update the stats with a new value
        '''
        self.count += 1
        delta = x - self.mean
        self.mean += delta/self.count
        self.m2 += delta * (x - self.mean)
    
    def finalize(self):
        '''
        Derive other stats
        '''
        # estimated population variance/stddev
        if self.count > 1:
            self.variance = self.m2/(self.count - 1)
            self.std_dev = self.variance ** 0.5
        else:
            # technically not correct but it seems to make sense in this context
            self.std_dev = self.variance = float('inf')
        
        # sample variance/stddev
        #self.variance_n = self.m2/self.count
        #self.std_dev_n = self.varience_n ** 0.5
