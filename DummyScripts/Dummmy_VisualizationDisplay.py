import json
import numpy as np

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
        [[1, 2, 3], [4, 1, 2], {'name': 'Test 1'}],
        [[1, 2, 3], [1, 2, 3], {'name': 'Test 2'}]
    ])

    fig3 = createHeatMap('Test HeatMap',
                         data=heatmapData,
                         heatmap_kwargs={'colorbar': {'title': 'Heat'},
                                         'xgap': 0.1, 'ygap': 0.1},
                         layout_kwargs={'height': 1000})

    fig4 = createContourMap("Test Contour Map",
                            [[10, 10.625, 12.5, 15.625, 20],
                             [5.625, 6.25, 8.125, 11.25, 15.625],
                             [2.5, 3.125, 5., 8.125, 12.5],
                             [0.625, 1.25, 3.125, 6.25, 10.625],
                             [0, 0.625, 2.5, 5.625, 10]],
                            contour_kwargs={'colorscale': 'Electric'},
                            layout_kwargs={'height': 1000})

    addRect(fig4, 2, 2, width=2, fillcolor='red', opacity=0.5)
    addCircle(fig3, 10, 10, radius=5, opacity=0.5)

    tbl1 = createTable('Test table',
                       ['A Scores', 'B Scores'],
                       [[100, 90, 80, 90],[95, 85, 75, 95]],
                       header_kwargs=dict(line_color='darkslategray', fill_color='lightskyblue', align='left'),
                       cell_kwargs=dict(line_color='darkslategray', fill_color='lightcyan', align='left'))

    def createScatter(figure: go.Figure):
        data = [x for x in range(model.systemManager.timestep + 1)]

        return createScatterPlot('Test Scatter Plot', [
        [data, data, {'name': 'Example'}]], layout_kwargs={'template': 'plotly_dark'})


    def liveLabelCallback(children):
        return "Random Output: {}".format(model.random.randrange(0, model.systemManager.timestep if model.systemManager.timestep != 0 else 1))

    fig5 = createPieChart('Pie Chart', ['Test 1', 'Test 2', 'Test 3'], [50, 10, 40],
                          pie_kwargs=dict(marker=dict(colors=['gold', 'darkorange', 'green'],
                                                      line=dict(color='#000000', width=2))))

    fig6 = createScatterGLPlot('Scatter GL plot',
                               [[np.random.rand(1000), np.random.randn(1000), {'name': 'Test Scatter'}]])

    fig7 = createHeatMapGL('Test HeatMapGL',
                         data=heatmapData,
                         heatmap_kwargs={'colorbar': {'title': 'Heat'}},
                         layout_kwargs={'height': 1000})

    labels = ['Bar Graph', 'Scatter Plot', 'Heatmap', 'Contour Graph', 'Test Table']
    tabs = [
        createGraph('test-bar', fig1),
        createLiveGraph('test-scatter', createScatter(None), vs, createScatter),
        createGraph('test-heatmap', fig3),
        createGraph('test-contour', fig4),
        createGraph('test-table', tbl1)
    ]

    vs.addDisplay(createTabs(labels, tabs))
    vs.addDisplay(createTabs(['Scatter GL', 'Heatmap GL'],
                              [createGraph('test-scattergl', fig6), createGraph('test-heatmapgl', fig7)]))
    vs.addDisplay(createGraph('test-pie', fig5), add_break=False)
    vs.addParameter(createLabel('test-label', 'Test Label...'))
    vs.addParameter(createLiveLabel('test-live-label', 'Random Output: ', vs, liveLabelCallback))

    def set_val(value):
        pass

    vs.addParameter(createSlider('test-slider', "Test Slider", vs, set_val))
    vs.app.run_server(debug=True)