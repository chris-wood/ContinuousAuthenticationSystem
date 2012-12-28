'''
File: Profile.py
Author: Nate Smith (originally StatObj class)
Contributor: Christopher Wood, caw4567@rit.edu
'''

# a class for storing stats per character
class Profile(object):
    count = 0
    mean = 0
    m2 = 0  # second moment ?
    variance = None
    std_dev = None

    # update the stats with a new value
    def update(self, x):
        self.count += 1
        delta = x - self.mean
        self.mean += delta/self.count
        self.m2 += delta * (x - self.mean)
    
    # derive other stats
    def finalize(self):
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
