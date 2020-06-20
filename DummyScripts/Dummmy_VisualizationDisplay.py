from ECAgent.Visualization import *


if __name__ == '__main__':
    model = Model()
    vs = VisualSystem("Test Visual", model)
    vs.displays.append(html.Div(
                                className="bg-white",
                                children=[
                                    html.H5("Animal data plot"),
                                    dcc.Graph(id="plot")
                                ]
                            ))
    vs.displays.append(html.Br())
    vs.displays.append(html.Div(
        className="bg-white",
        children=[
            html.H5("Animal data plot"),
            dcc.Graph(id="not-plot")
        ]
    ))
    model.systemManager.addSystem(vs)
    vs.app.run_server(debug=True)