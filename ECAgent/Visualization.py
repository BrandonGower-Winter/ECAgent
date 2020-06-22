import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from sys import maxsize
from ECAgent.Core import System, Model

# Can be used to customize CSS of Visualizer
external_stylesheets = ['https://rawgit.com/BrandonGower-Winter/ABMECS/master/Assets/VisualizerCustom.css',
                        'https://rawgit.com/BrandonGower-Winter/ABMECS/master/Assets/VisualizerBase.css']


class VisualSystem(System):
    """
    Ths is the base class for Visual Systems. It inherits from the ECAgent.Core.System class.
    VisualSystems's utilize the dash package to create a WebApp to allow individuals to view the results in of their
    model once completed or in real-time. By overriding the render() function you can create your own WebApps using any
    of dash's components.

    There are a few things to note about the VisualSystem class:
    * By calling the super.init() method, your WebApp will have features setup for you: Namely, play, stop, restart and
    step. It'll also include a banner with your System's id as a name on it.
    * A frameFreq of 0.0 means that your system is static and will only be called once every 'self.frequency' steps.
    If you want a dynamic WebApp, you must set the frameFreq to some non-zero positive number. If your frameFreq is 0.0,
    the play, stop, restart and step buttons will not be added to your WebApp.
    * The server will start once you initialize a VisualSystem.
    * frameFreq is different to frequency. frameFreq is the rate at which SystemManage.executeSystems() method
     is called while frequency is how how often your render() method will be called.
     You can calculate how often your WebApp will update it's contents like so: frameFreq * frequency.
    """

    def __init__(self, id, model: Model, frameFreq: float = 0.0,
                 priority: int = -1, start: int = 0, end: int = maxsize, frequency: int = 1):
        super().__init__(id, model, priority, frequency, start, end)

        self.frameFreq = frameFreq

        # Create app
        self.app = dash.Dash(
            self.id, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
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
                html.H2(className="h2-title", children=self.id),
                html.H2(className="h2-title-mobile", children=self.id),
            ],
        )
        # If framerate > 0, create the play, stop, and restart iteration info
        if self.frameFreq > 0:
            banner.children.append(
                html.Div(
                    className='div-play-buttons',
                    id='dynamic-button',
                    children=[
                        html.Button("Play", id='play-stop-button', n_clicks=0),
                        html.Button('Restart', id='restart-button', n_clicks=0),
                        html.Button('Step', id='next-button', n_clicks=0)
                    ]
                )
            )

            # Apply Callbacks
            self.app.callback(
                dash.dependencies.Output('play-stop-button', 'children'),
                [dash.dependencies.Input('play-stop-button', 'n_clicks')]
            )(play_button_callback)

        # Do that here...
        # Add parameter header
        addLabel(self, 'parameter-heading', 'Parameters:')

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
                            children=self.displays
                        ),
                        dcc.Store(id="error", storage_type="memory"),
                    ],
                ),
            ]
        )


# ####################################### Callbacks ###########################################


def play_button_callback(n_clicks):
    if n_clicks % 2 == 0:
        return 'Play'
    else:
        return 'Stop'


# ############################## Graph and Parameter Functionality ##############################


def addDCCGraph(vs: VisualSystem, graphID: str, title: str, figure: go.Figure, classname: str = 'bg-white',
                addBreak: bool = True):
    vs.displays.append(html.Div(
        className=classname,
        children=[
            html.H5(title),
            dcc.Graph(id=graphID, figure=figure)
        ]
    ))
    if addBreak:
        vs.displays.append(html.Br())


def addLabel(vs: VisualSystem, label_id, content):
    vs.parameters.append(
        html.Div(
            className="padding-top-bot",
            children=[
                html.H6(content, id=label_id),
            ],
        )
    )
