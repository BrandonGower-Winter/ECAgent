import json

from ECAgent.Visualization import *


if __name__ == '__main__':
    model = Model()
    vs = VisualInterface("Test Visual", model, frameFreq=1000)

    heatmapData = []

    with open('Data/test_heatmap.json') as json_file:
        data = json.load(json_file)

        count = 0
        for x in range(data['width']):
            row = []
            for y in range(data['height']):
                row.append(data['land_properties'][count]['fertility'])
                count += 1

            heatmapData.append(row)

    fig1 = createBarGraph('Test Bar Graph', [
        [[1, 2, 3], [4, 1, 2], 'Test 1'],
        [[1, 2, 3], [1, 2, 3], 'Test 2']
    ])

    fig3 = createHeatMap('Test HeatMap',
                         data=heatmapData,
                         xLabel="xPos", yLabel="yPos", zLabel="Fertility",
                         height=1000)

    def createScatter(n_intervals):
        data = []
        for x in range(model.systemManager.timestep):
            data.append(x)

        return createScatterPlot('Test Scatter Plot', [
        [data, data, 'Example']], template='plotly_dark')

    addGraph(vs, 'test-bar', fig1)
    addLiveGraph(vs, 'test-scatter', 500, createScatter)
    addGraph(vs, 'test-heatmap', fig3, addBreak=False)

    addLabel(vs, 'test-label', 'Test Label...')

    def set_val(value):
        pass

    addSlider(vs, 'test-slider', "Test Slider", set_val)
    vs.app.run_server(debug=True)