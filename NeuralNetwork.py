import numpy, os

def progressBar(progres, total):
    pourcent = (progres/float(total))*100
    barre = '█'*int(pourcent) + '-'*(100-int(pourcent))
    print(f'\r|{barre}| {pourcent:.2f}%', end='\r')
    if int(pourcent) >= 100: print('\n')

class NeuralNetwork:
    def __init__(self, inputSize, outputSize, hiddenLayers=0, hiddenSize=None, path='./weights/weight{}.npy'):
        self.neuralList = [inputSize]
        hidden = hiddenSize if hiddenSize != None else int((inputSize * outputSize)**0.5)
        self.neuralList.extend(hidden for _ in range(hiddenLayers))
        self.neuralList.append(outputSize)

        self.path = path
        self.createWeight()

    def createWeight(self):
        self.weightList = []
        for i in range(len(self.neuralList)-1):
            try: self.weightList.append(numpy.load(self.path.format(i)))
            except: self.weightList.append(numpy.random.randn(self.neuralList[i], self.neuralList[i+1]))

    def inputToOutput(self, inputValues):
        self.synapticList = [self.sigmoid(numpy.dot(inputValues, self.weightList[0]))]
        self.synapticList.extend(
            self.sigmoid(numpy.dot(self.synapticList[i], weight))
            for i, weight in enumerate(self.weightList[1:-1])
        )

        return self.sigmoid(numpy.dot(self.synapticList[-1], self.weightList[-1]))

    def sigmoid(self, exponent): return 1/(1+numpy.exp(-exponent))

    def sigmoidPrime(self, exponent): return exponent * (1-exponent)

    def outputToInput(self, inputValues, outputValues, output):
        deltaOutput = (outputValues - output) * self.sigmoidPrime(output)

        deltaList = [deltaOutput]
        deltaList.extend(
            deltaList[i].dot(weight.T) * self.sigmoidPrime(self.synapticList[-i - 1])
            for i, weight in enumerate(self.weightList[::-1][:-1])
        )
        deltaList.append(inputValues)
        deltaList.reverse()

        for i in range(len(self.weightList)): self.weightList[i] += deltaList[i].T.dot(deltaList[i+1])

    def training(self, inputValues, outputValues):
        output = self.inputToOutput(inputValues)
        self.outputToInput(inputValues, outputValues, output)

    def trainingFor(self, nbTraining, inputValues, outputValues, save=True):
        progressBar(0, nbTraining)
        for i in range(nbTraining):
            self.training(inputValues, outputValues)
            progressBar(i+1, nbTraining)
        if save: self.saveWeight()
    
    def saveWeight(self):
        folder = '/'.join(self.path.split('/')[:-1])
        if not os.path.exists(folder): os.makedirs(folder)
        for i, weight in enumerate(self.weightList): numpy.save(self.path.format(i), numpy.asarray(weight))

    def prediction(self, inputValuesUnknow): return self.inputToOutput(inputValuesUnknow)

