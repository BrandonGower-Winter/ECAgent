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
                         zLabel="Fertility",
                         height=1000)

    fig4 = createContourMap("Test Contour Map",
                            [[10, 10.625, 12.5, 15.625, 20],
                             [5.625, 6.25, 8.125, 11.25, 15.625],
                             [2.5, 3.125, 5., 8.125, 12.5],
                             [0.625, 1.25, 3.125, 6.25, 10.625],
                             [0, 0.625, 2.5, 5.625, 10]],
                            contour_kwargs={'colorscale': 'Electric'},
                            layout_kwargs={'height': 1000})

    def createScatter(n_intervals):
        data = []
        for x in range(model.systemManager.timestep):
            data.append(x)

        return createScatterPlot('Test Scatter Plot', [
        [data, data, 'Example']], template='plotly_dark')

    addGraph(vs, 'test-bar', fig1)
    addLiveGraph(vs, 'test-scatter', 500, createScatter)
    addGraph(vs, 'test-heatmap', fig3)
    addGraph(vs, 'test-contour', fig4, addBreak=False)
    addLabel(vs, 'test-label', 'Test Label...')

    def set_val(value):
        pass

    addSlider(vs, 'test-slider', "Test Slider", set_val)
    vs.app.run_server(debug=True)