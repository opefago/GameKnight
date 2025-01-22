import string
PREPOSITIONS = [
    "to", "toward", "towards", "into", "onto", "upon", "in", "inside", "within", "through", 
    "across", "over", "under", "beneath", "below", "behind", "beside", "between", "beyond", 
    "by", "near", "next", "past", "throughout", "along", "amid", "among", "around", "at", 
    "before", "behind", "below", "beneath", "beside", "between", "beyond", "by", "down", 
    "from", "in", "inside", "into", "near", "off", "on", "onto", "out", "outside", "over", 
    "through", "to", "toward", "towards", "under", "up", "with", "within", "without", 
]

VERBS = [
    "go", "move", "walk", "run", "jump", "climb", "crawl", "swim", "fly", "drive", "ride", "sail", 
    "travel", "transport", "navigate", "look", "see", "watch", "observe", "notice", "view", "examine", 
    "inspect", "scan", "peer", "gaze", "stare", "glance", "glimpse", "peek", "spy", "spot", "discern", 
    "discriminate", "distinguish", "disclose", "reveal", "uncover", "expose", "display", "demonstrate", 
    "illustrate", "depict", "portray", "represent", "picture", "paint", "sketch", "draw", "design", 
    "draft", "outline", "trace", "compose", "attack", "assault", "hit", "strike", "punch", "kick",
    "fight", "battle", "combat", "confront", "challenge",  "engage", "burn",
    "be", "have", "do", "say", "get", "make", "go", "know", "take",
    "come", "think", "want", "give", "use", "find", "tell", "ask", "work",
    "seem", "feel", "try", "leave", "call", "need", "become", "put", "mean", "keep",
    "let", "begin", "help", "talk", "turn", "start", "show", "hear", "play",
    "like", "live", "believe", "hold", "bring", "happen", "write", "provide",
    "sit", "stand", "lose", "pay", "meet", "include", "continue", "set", "learn", "change",
    "lead", "understand", "watch", "follow", "stop", "create", "speak", "read", "allow", "add",
    "spend", "grow", "open", "walk", "win", "offer", "remember", "love", "consider", "appear",
    "buy", "wait", "serve", "die", "send", "expect", "build", "stay", "fall", "cut",
    "reach", "kill", "remain",
    
]

VERBS_WITH_ALIASES = {
    # "go": ["go", "move", "walk", "run", "jump", "climb", "crawl", "swim", "fly", "drive", "ride", "sail", "travel", "transport", "navigate"],
    # "look": ["look", "see", "watch", "observe", "notice", "view", "examine", "inspect", "scan", "peer", "gaze", "stare", "glance", "glimpse", "peek", "spy", "spot", "discern", "discriminate", "distinguish"],
    # "attack": ["attack", "assault", "hit", "strike", "punch", "kick", "fight", "battle", "combat", "confront", "challenge", "engage"],
    # 'go': ['move', 'travel'],
    # 'move': ['go', 'walk'],
    # 'walk': ['move', 'go'],
    "go": ["go", "move", "walk", "run", "travel", "head", "proceed"],
    "help": ["help", "commands", "command", "?"],
    "objective": ["objective", "goal", "mission", "task"],
    "hint": ["hint", "hints", "clue", "clues"],
    "close": ["close", "shut"],
    "put": ["put", "place", "insert"],
    "combine": ["combine", "enter", "input"],  # For combination locks
    "lift": ["lift", "raise", "move", "shift", "check under"],
    # Observation verbs
    "look": ["look", "see", "watch", "observe", "inspect", "notice", "view", "examine", "inspect", "scan", "peer", "gaze", "stare", "glance", "glimpse", "peek", "spy", "spot", "discern", "discriminate", "distinguish", "scan", "search", "inspect", "study"],
    # Analysis verbs
    # 'discern': ['distinguish', 'recognize'],
    # 'discriminate': ['distinguish', 'differentiate'],
    # 'distinguish': ['discern', 'recognize'],
    
    # Revelation verbs
    # 'disclose': ['reveal', 'expose'],
    # 'reveal': ['expose', 'show'],
    # 'uncover': ['expose', 'reveal'],
    # 'expose': ['reveal', 'show'],
    # 'display': ['show', 'exhibit'],
    # 'demonstrate': ['show', 'display'],
    
    # Representation verbs
    # 'illustrate': ['depict', 'show'],
    # 'depict': ['portray', 'represent'],
    # 'portray': ['represent', 'depict'],
    # 'represent': ['depict', 'portray'],
    # 'picture': ['draw', 'paint'],
    # 'paint': ['draw', 'sketch'],
    # 'sketch': ['draw', 'paint'],
    # 'draw': ['sketch', 'paint'],
    
    # Design verbs
    # 'design': ['create', 'draft'],
    # 'draft': ['compose', 'write'],
    # 'outline': ['sketch', 'draft'],
    # 'trace': ['draw', 'sketch'],
    # 'compose': ['create', 'write'],
    
    # Combat verbs
    'attack': ['strike', 'assault', 'hit', 'punch', 'kick', 'fight', 'battle', 'combat', 'confront', 'challenge', 'engage'],
    
    # Basic verbs
    # 'be': ['exist', 'remain'],
    # 'have': ['possess', 'own'],
    'do': ['perform', 'execute'],
    'say': ['tell', 'speak', 'talk', 'communicate', 'convey', 'express', 'converse'],
    'get': ['obtain', 'acquire'],
    # 'make': ['create', 'produce'],
    # 'know': ['understand', 'comprehend'],
    "take": ["take", "get", "grab", "pick", "collect", "acquire", 'grasp'],
    # 'come': ['arrive', 'approach'],
    # 'think': ['believe', 'consider'],
    # 'want': ['desire', 'wish'],
    'give': ['provide', 'offer'],
    'use': ['utilize', 'employ'],
    'find': ['discover', 'locate'],
    # 'work': ['labor', 'function'],
    # 'seem': ['appear', 'look'],
    # 'feel': ['sense', 'experience'],
    # 'try': ['attempt', 'endeavor'],
    # 'leave': ['depart', 'exit'],
    # 'call': ['name', 'summon'],
    # 'need': ['require', 'want'],
    # 'become': ['grow', 'turn'],
    # 'put': ['place', 'set'],
    # 'mean': ['signify', 'indicate'],
    # 'keep': ['maintain', 'retain'],
    # 'let': ['allow', 'permit'],
    # 'begin': ['start', 'commence'],
    # 'help': ['assist', 'aid'],
    # 'turn': ['rotate', 'spin'],
    'start': ['begin', 'commence'],
    # 'show': ['display', 'demonstrate'],
    # 'hear': ['listen', 'perceive'],
    # 'play': ['perform', 'act'],
    # 'like': ['enjoy', 'prefer'],
    # 'live': ['exist', 'dwell'],
    # 'believe': ['think', 'trust'],
    # 'hold': ['grasp', 'keep'],
    # 'bring': ['carry', 'transport'],
    # 'happen': ['occur', 'transpire'],
    # 'write': ['compose', 'record'],
    # 'provide': ['supply', 'furnish'],
    # 'sit': ['rest', 'settle'],
    # 'stand': ['rise', 'remain'],
    # 'lose': ['misplace', 'forfeit'],
    # 'pay': ['compensate', 'settle'],
    # 'meet': ['encounter', 'gather'],
    # 'include': ['contain', 'comprise'],
    # 'continue': ['proceed', 'persist'],
    # 'set': ['place', 'position'],
    # 'learn': ['study', 'acquire'],
    # 'change': ['alter', 'modify'],
    # 'lead': ['guide', 'direct'],
    # 'understand': ['comprehend', 'grasp'],
    # 'follow': ['pursue', 'track'],
    # 'stop': ['halt', 'cease'],
    # 'create': ['make', 'produce'],
    # 'speak': ['talk', 'say'],
    # 'allow': ['permit', 'let'],
    # 'add': ['include', 'insert'],
    # 'spend': ['use', 'expend'],
    # 'grow': ['develop', 'increase'],
    # 'open': ['unlock', 'expand'],
    # 'win': ['succeed', 'triumph'],
    # 'offer': ['propose', 'present'],
    # 'remember': ['recall', 'recollect'],
    # 'love': ['adore', 'cherish'],
    # 'consider': ['think', 'contemplate'],
    # 'appear': ['seem', 'emerge'],
    # 'buy': ['purchase', 'acquire'],
    # 'wait': ['stay', 'remain'],
    # 'serve': ['help', 'assist'],
    # 'die': ['expire', 'perish'],
    # 'send': ['transmit', 'dispatch'],
    # 'expect': ['anticipate', 'await'],
    # 'build': ['construct', 'create'],
    # 'stay': ['remain', 'continue'],
    # 'descend': [ 'fall'],
    "drop": ["drop", "leave", "put", "place", "discard"],
    "talk": ["talk", "speak", "converse", "chat", "discuss", "communicate", "confer", "dialogue", "interact", "negotiate", 'question', 'ask', 'query', 'inquire'],
    # 'cut': ['slice', 'divide'],
    # 'reach': ['arrive', 'attain'],
    # 'kill': ['slay', 'eliminate'],
    # 'remain': ['stay', 'continue'],
    # 'burn': ['ignite', 'consume'],
    "inventory": ["inventory", "inv", "i", "items", "bag"],
    "quit": ["quit", "exit", "bye", "goodbye", "end"],
    "read": ["read", "examine", "inspect", "look", "check", 'peruse', 'study'],
    "examine": ["examine", "inspect", "look", "check", "study"],
    "open": ["open", "unlock", "access"],

}

ARTICLES = [ "a", "an", "the", "some ", "few", "many", "several", "this", "that", "these", "those", "to", "with", "at", "on"]

class CommandParseError(Exception):
    pass

class CommandParser:
    def __init__(self):
        self.verbs = VERBS_WITH_ALIASES
        
        self.articles = ARTICLES
        self.prepositions = PREPOSITIONS
        self.directions = ['north', 'south', 'east', 'west', 'up', 'down']
    
    def normalize_verb(self, word):
        """Convert verb aliases to their base form"""
        for base_verb, aliases in self.verbs.items():
            # print(base_verb, aliases)
            if word == base_verb or word in aliases:
                return base_verb
        return None


    #parse the sentence into action, direct object, and indirect object
    def parse_command(self, text):
        #split the sentence into words
        words = text.split()

        if len(words) == 0:
            raise CommandParseError("No words in sentence")
        #initialize the action, direct object, and indirect object
        action = ""
        directObject = ""
        indirectObject = ""
        #initialize the current object
        currentObject = ""
        command = {
            'action': None,
            'direct_object': None,
            'indirect_object': None,
            'direction': None,
            'preposition': None
        }

        if words[0].lower() in self.directions:
            command['direction'] = words[0].lower()
            command['action'] = 'go'
            return command

        #if the word is a verb, set the action to the word
        normalized = self.normalize_verb(words[0].lower())
        action = normalized
        #iterate over the words in the sentence
        for word in words[1:]:
            #if the word is a preposition, set the current object to the direct object
            if word.lower() in self.prepositions:
                command['preposition'] = word.lower()
                directObject = currentObject
                currentObject = ""
            elif word.lower() in self.directions:
                command['direction'] = word.lower()
            #otherwise, add the word to the current object
            elif word.lower() not in self.articles:
                currentObject += word + " "
        #set the indirect object to the current object
        if directObject == "":
            directObject = currentObject
        else:
            indirectObject = currentObject
        
        command['action'] = action if action else None
        command['direct_object'] = directObject.strip() if directObject else None
        command['indirect_object'] = indirectObject.strip() if indirectObject else None
        return command
    
    def comparePhrases(slef, object1, object2):
        if object1.lower().strip() == object2.lower().strip():
            return True
        
        #remove all articles from the phrases
        object1 = " ".join([word for word in object1.split() if word.lower() not in ARTICLES])
        object2 = " ".join([word for word in object2.split() if word.lower() not in ARTICLES])
        #Remove punctuations
        object1 = object1.translate(str.maketrans('', '', string.punctuation))
        object2 = object2.translate(str.maketrans('', '', string.punctuation))
        if object1.lower().strip() == object2.lower().strip():
            return True
        return False

# if __name__ == "__main__":
#     parser = CommandParser()
#     print(parser.parse_command("examine the small mailbox"))
#     print(parser.parse_command("attack the nasty-looking troll with the garlic"))
#     print(parser.parse_command("strike the nasty-looking troll with the garlic"))
#     print(parser.parse_command("look at the glass bottle"))
#     # print(parser.parse_command("burn down the white house with the lantern"))
#     print(parser.parse_command("attack the mailbox with the elvish sword"))
#     print(parser.parse_command("go north"))
#     print(parser.parse_command("south"))
#     print(parser.parse_command("go to north"))
#     print(parser.parse_command("drop ball into basket"))
#     print(parser.parse_command("take key from the table"))
#     # print(parser.parse_command("burn down the house with the lantern"))
#     print(parser.parse_command("find the white house"))
#     print(parser.parse_command("locate the white house"))

#     print(parser.comparePhrases("the small mailbox", "the small mailbox"))
#     print(parser.comparePhrases("the small mailbox", "small mailbox."))
#     print(parser.comparePhrases("the old man", "old man"))
#     print(parser.comparePhrases("the evil witch", "witch"))