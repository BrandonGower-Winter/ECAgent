from ECAgent.Core import Agent, Environment, Component, Model


class PositionComponent(Component):
    """ A position component. It contains three float properties: x, y, z.
    This component can be used to store the position of an Agent in a 1-3D world.
    It is used by the LineWorld, GridWorld and CubeWorld classes to do exactly that."""

    def __init__(self, agent, model, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        super().__init__(agent, model)
        self.x = x
        self.y = y
        self.z = z


class LineWorld(Environment):
    """ LineWorld is a discrete environment with only 1 axis (x-axis). It can be used in place of the base Environment
    class. All agents added to a LineWorld class are given a PositionComponent to denote their place in the world.

    A LineWorld's dimensions are defined by a width property.

    LineWorld.addComponent(comp) adds component comp to each of the cells in the environment."""

    def __init__(self, width, id: str = 'ENVIRONMENT'):

        if width < 1:
            raise Exception("Cannot create a LineWorld with a negative width.")

        super().__init__(id)
        self.width = width
        self.cells = []

        # Create cells
        for x in range(width):
            self.cells.append(Agent(str(x), None))

    def addAgent(self, agent: Agent, xPos: int = 0):
        """Adds an agent to the environment. Overrides the base class function.
        This function will also add a PositionComponent to the agent object.
        If the xPos is greater than the width of the world, an error will be thrown."""

        if xPos >= self.width or xPos < 0:
            raise Exception("Cannot add the Agent to position not on the map.")

        agent.addComponent(PositionComponent(agent, agent.model, x=xPos))
        super().addAgent(agent)

    def removeAgent(self, agentID: str):
        """ Removes the agent from the environment. Will also remove the PositionComponent from the agent"""
        if agentID in self.agents:
            self.agents[agentID].removeComponent(PositionComponent)

        super().removeAgent(agentID)

    def setModel(self, model: Model):
        super().setModel(model)

        for cell in self.cells:
            cell.model = model

    def getAgentsAt(self, xPos: int):
        """Returns a list of agents at position xPos. Will return [] empty if no agents are in that cell"""
        return [self.agents[agentKey] for agentKey in self.agents if self.agents[agentKey][PositionComponent].x == xPos]

    def getDimensions(self):
        return self.width


class GridWorld(Environment):
    """ GridWorld is a discrete environment with 2 axes (x,y-axes). It can be used in place of the base Environment
    class. All agents added to a GridWorld class are given a PositionComponent to denote their place in the world.

    A GridWorld's dimensions are defined by a width and height properties.

    GridWorld.addComponent(comp) adds component comp to each of the cells in the environment."""

    def __init__(self, width, height, id: str = 'ENVIRONMENT'):

        if width < 1 or height < 1:
            raise Exception("Cannot create a GridWorld with a negative width or height.")

        super().__init__(id)
        self.width = width
        self.height = height
        self.cells = []

        # Create cells
        for y in range(height):
            for x in range(width):
                self.cells.append(Agent(str(x + (y * self.width)), None))

    def addAgent(self, agent: Agent, xPos: int = 0, yPos: int = 0):
        """Adds an agent to the environment. Overrides the base class function.
        This function will also add a PositionComponent to the agent object.
        If the xPos or yPos is greater than the width of the world, an error will be thrown."""

        if xPos >= self.width or xPos < 0 or yPos >= self.height or yPos < 0:
            raise Exception("Cannot add the Agent to position not on the map.")

        agent.addComponent(PositionComponent(agent, agent.model, x=xPos, y=yPos))
        super().addAgent(agent)

    def removeAgent(self, agentID: str):
        """ Removes the agent from the environment. Will also remove the PositionComponent from the agent"""
        if agentID in self.agents:
            self.agents[agentID].removeComponent(PositionComponent)

        super().removeAgent(agentID)

    def setModel(self, model: Model):
        super().setModel(model)

        for cell in self.cells:
            cell.model = model

    def getAgentsAt(self, xPos: int, yPos: int):
        """Returns a list of agents at position xPos. Will return [] empty if no agents are in that cell"""
        return [self.agents[agentKey] for agentKey in self.agents
                if self.agents[agentKey][PositionComponent].x == xPos and self.agents[agentKey][PositionComponent].y == yPos]

    def getDimensions(self):
        return self.width, self.height
