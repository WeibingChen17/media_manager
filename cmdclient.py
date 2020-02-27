import cmd

from shared.constants import SUCCEED_CODE

def _checkIndexRange(ind, lst):
    if lst == None:
        print("No list is provided")
        return None
    try:
        ind = int(ind)
    except ValueError as e:
        print("Index must be integer")
        return None
    if ind < 0 or ind > len(lst):
        print("Index is out of range")
        return None
    return ind

class CmdClient(cmd.Cmd):
    prompt = "SEARCH > "

    def __init__(self, name, searcher=None, player=None, updater=None):
        super().__init__()
        self.intro = "Welcome to {} world!".format(name)
        self.searcher = searcher
        self.player = player
        self.editCmd = EditCmd(searcher, updater)
        self.res = None
        self.curr_idx = 0

    def do_exit(self, line):
        return True

    def emptyline(self):
        self.do_show("")

    # default to search
    def default(self, line):
        if len(line) == 0:
            return True

        query = line
        if ":" in line:
            try:
                query = eval("{" + line + "}")
            except:
                pass
        res = self.searcher.search(query)
        if not res:
            print("Search result is empty.")
            return False
        self.res = res
        self._show()
        if len(self.res) == 1:
            self.do_play('0')

    def _show(self, extra=None):
        if self.res == None:
            return True
        if extra == "sort size":
            self.res = sorted(self.res, key=lambda entry:entry.size, reverse=True)
        elif extra == "sort name":
            self.res = sorted(self.res, key=lambda entry:entry.name)
        elif extra == "only video":
            self.res = [entry for entry in self.res if entry.type and entry.type.startswith("video")]
        elif extra == "only image":
            self.res = [entry for entry in self.res if entry.type and entry.type.startswith("image")]
        if extra != None:
            self.curr_idx = 0
        elif self.curr_idx > len(self.res):
            self.curr_idx = 0
        end_idx = min(self.curr_idx + 20, len(self.res))
        for ind, entry in enumerate(self.res[self.curr_idx:end_idx]):
            print("{index:<5} {size:<10} {name} ".format(index=ind+self.curr_idx, name=entry.name, size=entry.size))
        self.curr_idx += 20

    def do_show(self, line):
        if len(line) == 0: 
            self._show()
        else:
            ind = _checkIndexRange(line, self.res)
            if ind != None:
                print(self.res[ind])

    def do_play(self, line):
        ind = _checkIndexRange(line, self.res)
        if ind != None:
            status = self.player.play(self.res[ind].path)
            if status != SUCCEED_CODE:
                print("Player is not able to play. Status = ", status)

    def do_edit(self, line):
        if len(line) == 0 and len(self.res) == 1:
            ind = 0
        else:
            ind = _checkIndexRange(line, self.res)
        if ind != None:
            self.editCmd.setMedieEntry(self.res[ind])
            self.editCmd.cmdloop()

    def do_sort(self, line):
        if len(line) == 0:
            # todo
            # self._show("sort rating")
            pass
        if line == "size":
            self._show("sort size")
        elif line == "name":
            self._show("sort name")
        else:
            print("unspported sort key")

    def complete_sort(self, text, line, beginidx, endix):
        return ["size", "name"]

    def do_only(self, line):
        if line == "video":
            self._show("only video")
        elif line == "image":
            self._show("only image")

    def complete_only(self, text, line, beginidx, endix):
        return ["video", "image"]


class EditCmd(cmd.Cmd):
    prompt = "Edit > "
    add_complete = ["actress", "tag"]
    change_complete = ["release_date", "director", "rating", "distributor", "designation", "maker", "type"]
    remove_complete = ["actress", "tag"]

    def __init__(self, searcher, updater):
        super().__init__()
        self.searcher = searcher
        self.updater = updater
        self.mediaEntry = None

    def setMedieEntry(self, mediaEntry):
        self.mediaEntry = mediaEntry
        self.entry_id = self.mediaEntry._id
        self.do_show("")

    def _verifyField(self, field, op):
        if not hasattr(self.mediaEntry, field):
            print("No such field in MediaEntry.")
            return False
        elif (op == "add" or op == "remove") and \
                not isinstance(self.mediaEntry.__dict__[field], list):
            print("Operation is not supported in this field. Use `change` instead")
            return False
        elif field in ["path", "name", "size", "duration"]:
            print("Immutable Field: {}".format(field))
            return False
        return True

    def do_exit(self, line):
        return True

    def emptyline(self):
        return True

    def default(self, line):
        try:
            op, field, *values = line.split()
        except:
            return True
        if self._verifyField(field, op):
            queryList = []
            for value in " ".join(values).split(","):
                queryList.append({op : {field : value.strip('"')}})
            self.updater.update_all(self.entry_id, queryList)
        self.do_show("")

    # def completedefault(self, text, line, beginidx, endidx):
    #     return ["add", "change", "remove", "delete"]

    def do_add(self, line):
        self.default("add " + line)

    def do_change(self, line):
        self.default("change " + line)

    def do_remove(self, line):
        self.default("remove " + line)

    def do_delete(self, line):
        self.updater.delete(self.entry_id)
        print("entry {} is deleted".format(self.entry_id))

    def complete_add(self, text, line, beginidx, endix):
        return [field for field in self.add_complete if field.startswith(text)]

    def complete_change(self, text, line, beginidx, endix):
        return [field for field in self.change_complete if field.startswith(text)]

    def complete_remove(self, text, line, beginidx, endix):
        return [field for field in self.remove_complete if field.startswith(text)]

    def do_show(self, line):
        self.mediaEntry = self.searcher.search_by_id(self.entry_id)[0]
        print(self.mediaEntry)

