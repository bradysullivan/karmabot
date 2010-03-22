import urllib

try:
    import json
except ImportError:
    import simplejson as json

import thing
import command
from utils import Cache


@thing.facet_classes.register
class GitHubFacet(thing.ThingFacet):
    name = "github"
    commands = command.thing.add_child(command.FacetCommandSet(name))

    def __init__(self, thing_):
        thing.ThingFacet.__init__(self, thing_)
        self.get_info = Cache(self._get_info, expire_seconds=10 * 60)

    @classmethod
    def does_attach(cls, thing):
        return False

    @commands.add(u"forget that {thing} is on github",
                  help=u"unset {thing}'s github username",
                  exclusive=True)
    def unset_github_username(self, thing, context):
        del self.data
        self.thing.detach_persistent(self)

    @commands.add(u"{thing} has github username {username}",
                  help=u"set {thing}'s github username to {username}")
    def set_github_username(self, thing, username, context):
        self.username = username

    @property
    def username(self):
        if self.has_data and "username" in self.data:
            return self.data["username"]
        else:
            return self.thing.name

    @username.setter
    def set_username(self, value):
        if "username" not in self.data or value != self.data["username"]:
            self.data["username"] = value
            self.get_info.reset()

    def _get_info(self):
        about_url = "http://github.com/{0}.json"
        about = urllib.urlopen(about_url.format(self.username))
        return json.load(about)

    @commands.add(u"{thing} commits",
                  help=u"show the last 3 commits by {thing}")
    def get_github_commits(self, thing, context):
        info = self.get_info()
        pushes = filter(lambda x: x["type"] == "PushEvent", info)
        lines = []
        for push in pushes[:3]:
            lines.append(u"\"{last_commit_msg}\" -- {url}".format(
                    url=push["repository"]["url"],
                    last_commit_msg=push["payload"]["shas"][0][2]))
        context.reply("\n".join(lines))


@command.thing.add(u"{thing} is on github",
                   help=u"link {thing}'s github account to their user",
                   exclusive=True)
@command.thing_command
def set_githubber(thing, context):
    thing.attach_persistent(GitHubFacet)


@thing.presenters.register(set(["github"]))
def present(thing, context):
    github = thing.facets["github"]
    text = u"http://github.com/{0}".format(github.username)
    return text
