import shapefile
from TransModel import *

def linearDecayFunction(time, upper):
    upper = float(upper)
    if time > upper:
        return 0
    else:
        return (upper - time) / upper

def ployDecayFunction(time, upper):
    upper = float(upper)
    if time > upper:
        return 0
    else:
        x = time/upper
        return max(0, 1.018 + 0.5226 * x - 2.686 * (x ** 2) - 12.27 * (x ** 3) + 27.184 * (x ** 4) - 13.77 * (x ** 5))

class ScoreModel:
    transModels = []
    weights = []
    blockList = []
    def __init__(self):
        shapeReader = shapefile.Reader("block/nyc.shp")
        self.shapeWriter = shapefile.Writer()
        self.shapes = shapeReader.shapes()
        self.records = shapeReader.records()
        self.shapeWriter.field("BlockID", "C", 15)
        self.blockList = [record[4] for record in self.records]
        self.transModels.append(Walk(ployDecayFunction))
        self.transModels.append(Auto(ployDecayFunction))
        self.weights = [0.75, 0.25]
        for model in self.transModels:
            self.shapeWriter.field(model.name(), "N", 30)
            model.computeScore()
        self.shapeWriter.field("FusionScore", "N", 30)
            
    def run(self):
        self.shapeWriter._shapes = self.shapes
        for blockID in self.blockList:
            record = [blockID]
            fusionScore = 0;
            for idx,model in enumerate(self.transModels):
                record.append(model.blockScore[blockID])
                fusionScore += self.weights[idx] * record[-1]
            record.append(fusionScore)
            self.shapeWriter.records.append(record)
        self.shapeWriter.save("result/nyc")
            
if __name__ == "__main__":
    sm = ScoreModel()
    sm.run()

