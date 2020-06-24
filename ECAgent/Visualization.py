import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from ECAgent.Core import Model

# Can be used to customize CSS of Visualizer
external_stylesheets = ['https://rawgit.com/BrandonGower-Winter/ABMECS/master/Assets/VisualizerCustom.css',
                        'https://rawgit.com/BrandonGower-Winter/ABMECS/master/Assets/VisualizerBase.css']


class VisualInterface:
    """
    Ths is the base class for Visual Interfaces.
    VisualInterface's utilize the dash package to create a WebApp to allow individuals to view the results of their
    model once a run has been completed or in real-time.

    There are a few things to note about the VisualInterface class:
    * By calling the VisualInterface.__init__() method, your WebApp will have features setup for you: Namely, play,
    stop, restart and step. It'll also include a banner with your System's name as a title on it.
    * A frameFreq of 0.0 means that your system is static and will only ever be constructed once.
    If you want a dynamic WebApp, you must set the frameFreq to some non-zero positive number. If your frameFreq is 0.0,
    the play, stop, restart and step buttons will not be added to your WebApp.
    * The server/WebApp will start once you call the VisualInterface.app.run_server().
    * The frameFreq property determines how frequently (in milliseconds) the SystemManager.executeSystems() method is
    called and how often your your graphs will update.
    """

    def __init__(self, name, model: Model, frameFreq: float = 0.0):

        self.name = name
        self.model = model
        self.frameFreq = frameFreq

        self.running = False  # Is used to determine whether a dynamic model is running or not.

        # Create app
        self.app = dash.Dash(
            self.name, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
            external_stylesheets=external_stylesheets
        )
        # Create parameter lists
        self.displays = []
        self.parameters = []

        self.createBaseLayout()

    def isStatic(self) -> bool:
        return self.frameFreq == 0.0

    def execute(self):
        self.render()

    def render(self):
        pass

    def createBaseLayout(self):
        """Creates the base layout"""

        # Create banner
        banner = html.Div(
            className="app-banner row",
            children=[
                html.H2(className="h2-title", children=self.name),
                html.H2(className="h2-title-mobile", children=self.name),
            ],
        )

        # Add parameter header
        addLabel(self, 'parameter-heading', 'Parameters:')

        # If framerate > 0, create the play, stop, and restart buttons and Timestep label
        if not self.isStatic():
            # Add Play/Restart/Step Buttons
            banner.children.append(
                html.Div(
                    className='div-play-buttons',
                    id='dynamic-button',
                    children=[
                        html.Button("Play", id='play-stop-button', n_clicks=0),
                        html.Button('Restart', id='restart-button', n_clicks=0),
                        html.Button('Step', id='step-button', n_clicks=0),
                        dcc.Interval(
                            id='interval-component',
                            interval=self.frameFreq,
                            n_intervals=0
                        )
                    ]
                )
            )

            # Add Timestep label
            self.parameters.append(addLabel(self, 'timestep-label', 'Timestep: 0'))

            # Apply Play/Stop Callback
            self.app.callback(
                dash.dependencies.Output('play-stop-button', 'children'),
                [dash.dependencies.Input('play-stop-button', 'n_clicks')]
            )(self.play_button_callback)
            # Apply executeSystems() on interval callback and Step button callback
            self.app.callback(
                dash.dependencies.Output('timestep-label', 'children'),
                [dash.dependencies.Input('interval-component', 'n_intervals'),
                 dash.dependencies.Input('step-button', 'n_clicks')]
            )(self.execute_system_on_play_callback)

        self.app.layout = html.Div(
            children=[
                # Error Message
                html.Div(id="error-message"),
                # Top Banner
                banner,
                # Body of the App
                html.Div(
                    className="row app-body",
                    children=[
                        # User Controls
                        html.Div(
                            className="four columns card",
                            children=html.Div(
                                className="bg-white user-control",
                                children=self.parameters)
                        ),
                        # Graph
                        html.Div(
                            className="eight columns card-left",
                            children=self.displays,
                            style={'margin-left': 0}
                        ),
                        dcc.Store(id="error", storage_type="memory"),
                    ],
                ),
            ]
        )

# #################################### Class Callbacks ###########################################
    def play_button_callback(self, n_clicks):
        if n_clicks % 2 == 0:
            self.running = False
            return 'Play'
        else:
            self.running = True
            return 'Stop'

    def execute_system_on_play_callback(self, n_intervals, n_clicks):
        context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
        if context == 'step-button':
            if not self.running:
                self.model.systemManager.executeSystems()
        elif self.running:
            self.model.systemManager.executeSystems()

        return "Timestep: {}".format(self.model.systemManager.timestep)

# ############################## Graph and Parameter Functionality ##############################


def createScatterPlot(title, data: [[[float], [float], str]], **layout_kwargs):
    """Creates a Scatter plot Figure. This function supports multiple traces supplied to the 'data' parameter
    Data should be supplied in the following format:
    [[xdata_1,ydata_1, trace_name_1], [xdata_2, ydata_2, trace_name_2], ..., [xdata_n,ydata_n, trace_name_n]]

    The 'trace_name' property is optional. If it is supplied, the trace in question will have its name set to the
    value of 'trace_name'.
    """
    traces = []
    for data_packet in data:
        scatter = go.Scatter(x=data_packet[0], y=data_packet[1])
        traces.append(scatter)
        if len(data_packet) > 2:
            scatter.name = data_packet[2]

    return go.Figure(data=traces, layout=go.Layout(title=title, **layout_kwargs))


def createBarGraph(title: str, data: [[[float], [float], str]], **layout_kwargs):
    """Creates a Bar Graph Figure. This function supports multiple traces supplied to the 'data' parameter
        Data should be supplied in the following format:
        [[xdata_1,ydata_1, trace_name_1], [xdata_2, ydata_2, trace_name_2], ..., [xdata_n,ydata_n, trace_name_n]]

        The 'trace_name' property is optional. If it is supplied, the trace in question will have its name set to the
        value of 'trace_name'.
        """
    traces = []
    for data_packet in data:
        bar = go.Bar(x=data_packet[0], y=data_packet[1])
        traces.append(bar)
        if len(data_packet) > 2:
            bar.name = data_packet[2]

    return go.Figure(data=traces, layout=go.Layout(title=title, **layout_kwargs))


def createHeatMap(title: str, data: [[float]], xLabel: str = None, yLabel: str = None, zLabel: str = None,
                  xData: [] = None, yData: [] = None, colorScale: [[float, str]] = None, **layout_kwargs):

    """Creates a HeatMap Figure object using Plotly graph objects. The data object determines the dimensions of the
    heatmap. The len(data) will be the height. The len(data[i]) will be the width of the heatmap. The Heatmap is
    constructed in a bottom-up and left-to-right manner.

    Discrete X and Y categories can be specified, this is done by supplying xData and yData with the X and Y category
    name respectively. The len(xData) must be equal to the width of your Heatmap, while len(yData) must be equal to the
    height of your Heatmap.

    A custom color scale can be supplied, ensure that it follows the correct format and that the threshold values are
    normalized and that the color scales are in rgb like so 'rgb(r_val, g_val, b_val)'"""

    return go.Figure(data=go.Heatmap(
        z=data,
        x=xData,
        y=yData,
        colorbar={'title': zLabel},
        colorscale=colorScale,
        xgap=0.1,
        ygap=0.1
    ), layout=go.Layout(title=title, **layout_kwargs))


def addGraph(vs: VisualInterface, graphID: str, figure: go.Figure, classname: str = 'bg-white', addBreak: bool = True):
    vs.displays.append(html.Div(
        className=classname,
        children=[
            dcc.Graph(id=graphID, figure=figure)
        ],
        style={'height': figure.layout.height}
    ))
    if addBreak:
        vs.displays.append(html.Br())


def addLiveGraph(vs: VisualInterface, graphID: str, height, callback, classname: str = 'bg-white',
                 addBreak: bool = True):
    vs.displays.append(html.Div(
        className=classname,
        children=[
            dcc.Graph(id=graphID)
        ],
        style={'height': height}
    ))
    # Add Callback
    vs.app.callback(
        dash.dependencies.Output(graphID, 'figure'),
        [dash.dependencies.Input('interval-component', 'n_intervals')]
    )(callback)

    if addBreak:
        vs.displays.append(html.Br())


def addLabel(vs: VisualInterface, label_id, content):
    vs.parameters.append(
        html.Div(
            className="padding-top-bot",
            children=[
                html.H6(content, id=label_id),
            ],
        )
    )


def addSlider(vs: VisualInterface, slider_id: str, slider_name: str, set_val, min_val: float = 0.0,
              max_val: float = 1.0, step: float = 0.01):
    """This function will add a slider to the parameter window of the visual interface. It will also automatically add
    a callback function that will supply your custom function 'set_val' with the value of the slider"""

    # Add html
    vs.parameters.append(
        html.Div(
            className="padding-top-bot",
            children=[
                html.H6('{}: [{}]'.format(slider_name, max_val), id=slider_id + '-title'),
                dcc.Slider(
                    id=slider_id,
                    min=min_val,
                    max=max_val,
                    value=max_val,
                    step=step
                )
            ],
        )
    )

    # Add callback

    def set_slider_val(value):
        set_val(value)
        return '{}: [{}]'.format(slider_name, value)

    vs.app.callback(dash.dependencies.Output(slider_id + '-title', 'children'),
                    [dash.dependencies.Input(slider_id, 'value')])(set_slider_val)
