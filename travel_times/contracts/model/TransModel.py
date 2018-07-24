class TransModel:
    blockScore = {}
    def computeScore(self):
        pass

class Walk(TransModel):
    timeFiles = ["data/walk.csv", "data/walk_2.csv"]
    def __init__(self, decayFunction):
        self.decayFunction = decayFunction
        self.blocks = {}
        self.blockScore = {}
        blockFile = open("block/block.csv", "r")
        lines = blockFile.readlines()
        lines = lines[1:]
        for line in lines:
            elements = line.strip("\n").split(",")
            blockID = elements[1]
            self.blocks[blockID] = []
            self.blockScore[blockID] = 0.0
        blockFile.close()
        for fileName in self.timeFiles:
            timeFile = open(fileName, "r")
            lines = timeFile.readlines()
            lines = lines[1:]
            for line in lines:
                elements = line.strip("\n").split(",")
                if elements[3] != "None":
                    destinationID, blockID, transTime = elements[0], elements[1], int(elements[3])
                    self.blocks[blockID].append({"Destnation": destinationID, "Time": transTime})
            timeFile.close()
    
    def name(self):
        return "WalkScore"


    def computeEachBlock(self, blockID):
        score = 0.0
        for dst in self.blocks[blockID]:
            score += self.decayFunction(dst["Time"], 1800.0)
        return score

    def computeScore(self):
        maxScore = 1.0
        for blockID in self.blocks:
            self.blockScore[blockID] = self.computeEachBlock(blockID)
            maxScore = max(maxScore, self.blockScore[blockID])
        for blockID in self.blocks:
            self.blockScore[blockID] = self.blockScore[blockID] / maxScore * 100

class Auto(TransModel):
    K = 500
    def __init__(self, decayFunction):
        self.decayFunction = decayFunction
        blockFile = open("data/blocks_super.csv", "r")
        self.superBlock = [[] for i in range(self.K)]
        self.transTime = [[] for i in range(self.K)]
        lines = blockFile.readlines()
        lines = lines[1:]
        self.blockScore = {}
        self.superBlockScore = [0 for i in range(self.K)]
        for line in lines:
            elements = line.strip("\n").split(",")
            blockID, superID = elements[1], int(elements[2])
            self.superBlock[superID].append(blockID)
            self.blockScore[blockID] = 0.0
        timeFile = open("data/auto.csv", "r")
        lines = timeFile.readlines()
        lines = lines[1:]
        for line in lines:
            elements = line.strip("\n").split(",")
            if elements[3] != "None":
                destinationID, blockID, transTime = elements[0], int(elements[1]), int(elements[3])
                self.transTime[blockID].append({"Destnation": destinationID, "Time": transTime})

    def name(self):
        return "AutoScore"
    
    def computeEachBlock(self, blockID):
        score = 0.0
        for dst in self.transTime[blockID]:
            score += self.decayFunction(dst["Time"], 3600.0)
        return score

    def computeScore(self):
        maxScore = 1.0
        for i in range(self.K):
            self.superBlockScore[i] = self.computeEachBlock(i)
            maxScore = max(self.superBlockScore[i], maxScore)
            for blockID in self.superBlock[i]:
                self.blockScore[blockID] = self.superBlockScore[i]
        for blockID in self.blockScore:
            self.blockScore[blockID] = self.blockScore[blockID] / maxScore * 100
            
    
