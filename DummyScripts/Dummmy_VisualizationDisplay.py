from ECAgent.Visualization import *


if __name__ == '__main__':
    model = Model()
    vs = VisualSystem("Test Visual", model, frameFreq=0.1)

    fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])

    addDCCGraph(vs, 'animal', 'Animal Graph', fig)
    addDCCGraph(vs, 'not-animal', 'Not Animal Graph', fig, addBreak=False)

    model.systemManager.addSystem(vs)
    vs.app.run_server(debug=True)