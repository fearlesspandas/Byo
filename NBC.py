class NBC:
    def __init__(self,G):
        self.Gesture = G
    def normpdf(self,x,mu,var):
        try:
            return (1/math.sqrt(2*var*math.pi))*math.exp((-1)*(x-mu)*(x-mu)/(2*var))
        except:
            print("exception")
            return 0

    def prob(self,x,v = None): #the probability of reading x given class v.
        totalprob = 1
        if v == None:
            v = self.Gesture.base_signals
            for i in range(0,len(x)):
                totalprob = totalprob*(self.normpdf(x[i],v['param']["means"][i],v['param']["var"][i]))
        else:
            for i in range(0,len(x)):
                totalprob = totalprob*(self.normpdf(x[i],v['param']["means"][i],v['param']["var"][i]))
        return totalprob

    def bayesprob(self,C_k,x): #takes class C_k and data x and returns probability of C_k given x
        a = self.prob(C_k["param"]["means"])*self.prob(x,C_k)
        b = self.prob(x,self.Gesture.base_signals)
        if b != 0:
            return a/b
        else:
            return 0
    def getdistparam(self,raw_data): #returns the mean and variance for each emg sensor taken from a sample of time length t, return dict of {"means" , "variances"}
        means = [0 for i in range(0,len(raw_data[0]))]
        var = [0 for i in range(0,len(raw_data[0]))]
        final = {}
        for i in range(0 ,len(raw_data[0])):
            for j in range(0,len(raw_data)):
                means[i] = ((j*means[i]) + raw_data[j][i])/(j+1)
        for i in range(0 ,len(raw_data[0])):
            for j in range(0,len(raw_data)):
                var[i] = ((j*var[i]) + ((raw_data[j][i])-means[i])*((raw_data[j][i])-means[i]))/(j+1)
        final['means'] = tuple(means)
        final['var'] = tuple(var)
        return final
    def getclass(self,x,gest_list= None,rettype = None,index = 0):#returns the class or class index of the highest probability given data point x
        maxIndex = None
        maxclass = None
        maxprob = 0
        if gest_list == None:
            gest_list = self.Gesture.activeGestures
        for y in gest_list:
            g = gest_list[y] #gesture
            p = self.bayesprob(g,x)
            if p > maxprob:
                maxIndex = y
                maxprob = p
                maxclass = g
        if not rettype:
            return maxclass
        else:
            return maxIndex
