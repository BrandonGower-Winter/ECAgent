import json

from ECAgent.Visualization import *


if __name__ == '__main__':
    model = Model()
    vs = VisualSystem("Test Visual", model, frameFreq=0.1)

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

    fig2 = createScatterPlot('Test Scatter Plot', [
        [[1, 2, 3], [4, 1, 2], 'Example 1'],
        [[1, 2, 3], [1, 2, 3], 'Example 2']
    ], template='plotly_dark')

    fig3 = createHeatMap('Test HeatMap',
                         data=heatmapData,
                         xLabel="xPos", yLabel="yPos", zLabel="Fertility",
                         height=1000)

    addDCCGraph(vs, 'test-bar', fig1)
    addDCCGraph(vs, 'test-scatter', fig2)
    addDCCGraph(vs, 'test-heatmap', fig3, addBreak=False)

    addLabel(vs, 'test-label', 'Test Label...')

    def set_val(value):
        pass

    addSlider(vs, 'test-slider', "Test Slider", set_val)
    model.systemManager.addSystem(vs)
    vs.app.run_server(debug=True)