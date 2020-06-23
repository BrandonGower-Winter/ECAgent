from ECAgent.Visualization import *


if __name__ == '__main__':
    model = Model()
    vs = VisualSystem("Test Visual", model, frameFreq=0.1)

    fig1 = createBarGraph('Test Bar Graph', [
        [[1, 2, 3], [4, 1, 2], 'Test 1'],
        [[1, 2, 3], [1, 2, 3], 'Test 2']
    ])

    fig2 = createScatterPlot('Test Scatter Plot', [
        [[1, 2, 3], [4, 1, 2], 'Example 1'],
        [[1, 2, 3], [1, 2, 3], 'Example 2']
    ], template='plotly_dark')

    addDCCGraph(vs, 'test-bar', fig1)
    addDCCGraph(vs, 'test-scatter', fig2, addBreak=False)

    addLabel(vs, 'test-label', 'Test Label...')

    def set_val(value):
        pass

    addSlider(vs, 'test-slider', "Test Slider", set_val)
    model.systemManager.addSystem(vs)
    vs.app.run_server(debug=True)