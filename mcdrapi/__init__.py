from mcdreforged.api.all import ServerInterface
from mcdreforged.api.command import SimpleCommandBuilder, Text
from mcdreforged.api.types import InfoCommandSource
from flask import Flask, request

server = ServerInterface.get_instance()

def on_load(): {

}

app = Flask(__name__)

class CommandArg():
    name: str

class CommandResponse():
    type: str
    content: str | None
    ternaryOperator: str | None

class Command():
    name: str
    args: list[CommandArg]
    response: str | CommandResponse

class TernaryOperator():
    condition: str
    iftrue: str
    iffalse: str
    def __init__(self, condition: str, iftrue: str, iffalse: str):
        self.condition = condition
        self.iftrue = iftrue
        self.iffalse = iffalse

commandsresponse: dict[str, str | CommandResponse]

@app.get('/api/v1/')
def Root():
    return {
        "success": True,
        "version": server.get_server_information().version
    }

@app.post('/api/v1/command')
def CreateCommand():
    if not request.is_json:
        return {
            "success": False,
            "error": 'Request must be JSON'
        }, 415
    else:
        builder = SimpleCommandBuilder()
        body: Command = request.get_json()
        builder.command(body.name, CommandCallback)
        for arg in body.args:
            builder.arg(arg.name, Text)
        if (isinstance(body.response, str)):
            commandsresponse[body.name] = body.response
        else:
            if body.response.content is not None:
                commandsresponse[body.name] = body.response.content
            elif body.response.ternaryOperator is not None:
                commandsresponse[body.name] = body.response.ternaryOperator
        
def CommandCallback(command: InfoCommandSource):
    info = command.get_info()
    response = commandsresponse[info.content.split(' ')[0]]

    if isinstance(response, str) | response.content is not None:
        if (info.is_player):
            response.replace('{player}', info.player)
        else:
            response.replace('{player}', 'Server')
        server.reply(info, response)
    else:
        response = ParseTernaryOperator(response)
        if eval(response.condition):
            server.reply(info, response.iftrue)
        else:
            server.reply(info, response.iffalse)

    

def ParseTernaryOperator(raw: str): 
    if not ('?' in raw & ':' in raw):
        return None
    else:
        parsedbyquestionmark = raw.split('?')
        condition = parsedbyquestionmark[0]
        parsedbycolon = parsedbyquestionmark[1].split(':')
        iftrue = parsedbycolon[0]
        iffalse = parsedbycolon[1]
        return TernaryOperator(condition, iftrue, iffalse)
