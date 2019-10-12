days = {0:"Sunes", 1:"Maens", 2:"Secces",
        3:"Ojfryghs", 4:"Tezres", 5:"Yrdes", 6:"Ilebs"
    }

months = {0:["Jaurze", 11], 1:["Fryare", 5], 2:["Marne", 12],
          3:["Aereth", 11], 4:["Muth", 9], 5:["Jyne", 10],
          6:["Jylei", 9], 7:["Aegeth",12], 8:["Syvn",10],
          9:["Eithn",11], 10:["Niven",20], 11:["Decura",7]
        }


class Time:
    def convert_format(self):
        min_num = self.sec/60
        for i in range(0,int(min_num)):
            if int(self.sec) >= 60:
                self.sec = self.sec - 60
                self.min += 1
        hour_num = self.min/60
        for i in range(0,int(hour_num)):
            if self.min >= 60:
                self.min = self.min - 60
                self.hour += 1

        if self.hour >= 24:
            self.hour = 0
            self.day += 1
            self.weekday = self.weekday+1 if self.weekday < 6 else 0
            self.moonphase = self.moonphase + 1 if self.moonphase < 63 else 0

            if self.getLeapYear() and self.month == 1:
                if self.monthday < months[self.month][1]+1: self.monthday += 1
                else:
                    self.monthday = 1; self.month += 1

            else:
                if self.monthday < months[self.month][1]: self.monthday += 1
                else:
                    self.monthday = 1
                    if self.month < 11: self.month += 1
                    else:
                        self.month = 0
                        self.year += 1

                        print( "%d: day of Dissolve lands on %s"%(self.year, days[self.weekday]) )


    def getLeapYear(self):
        return self.year % 4 == 0 and (self.year % 100 != 0 or self.year % 400 == 0)

    def getWeekday(self):
        self.weekday = self.getEpoch()%7

    def getMoonphase(self):
        self.moonphase = self.getEpoch()%63

    def getEpoch(self):
        d = int(self.monthday)
        for m in range(self.month):
            d += months[m][1]

        y = self.year-1
        d += ( (self.year)*127 ) + int( ((y/4) - (y/100)) + (y/400) )
        return d

    def __init__(self,dirn, sec=0, minu=0, hour=0, day=1,
     month=0, monthday=1, year=920, subdiv=1):
        if dirn == 'up':
            self.mili = 0.0
        else:
            self.mili = 1.0

        self.sec = sec
        self.min = minu
        self.hour = hour
        self.day = day

        self.month = month
        self.monthday = monthday
        self.year = year

        self.getWeekday()
        self.getMoonphase()

        self.subdiv = 1
        self.dirn = dirn
        self.convert_format()

    def count_up(self,timescale):
        self.mili += ((1/60)*(self.subdiv**timescale))
        if self.mili >= 1.0:
            diff = divmod(self.mili, 2)
            self.mili = diff[1]
            self.sec += diff[0]

        if self.sec >= 60 or self.min >= 60 or self.hour >= 24:
            self.convert_format()

    def count_down(self,timescale):
        self.mili -= ((1/60)*(self.subdiv**timescale))
        if self.min <= 0 and self.hour > 0:
            self.min = 59
            self.hour -= 1
        if int(self.sec) <= 0 and self.min > 0:
            self.sec = 59
            self.min -= 1
        if self.mili <= 0.0 and self.sec > 0:
            self.mili = self.mili + 1.0
            self.sec -= 1
        if (self.mili < 0):
            return False
        return True

    def convert_read(self):
        read = (
        str(self.hour)+':'+str(self.min)+':'+str(int(self.sec)))
        return read

    def convert_calendar(self):
        return "%s, %d of %s, %d"%(days[self.weekday],
         self.monthday, months[self.month][0], self.year)

    def update(self,timescale):
        return self.timeDict[self.dirn](self,timescale)
    
    timeDict = {'up':count_up,'down':count_down}