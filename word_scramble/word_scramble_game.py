import random
from game import Game

word_list = [
    # Original 100 words
    "abstract", "abundant", "adjacent", "advocate", "ambiguous",
    "ambitious", "analyze", "anticipate", "apparatus", "apparent",
    "architect", "authentic", "beneficial", "bizarre", "brilliant",
    "capacity", "catalyst", "cautious", "chronicle", "cognitive",
    "collaborate", "commence", "commodity", "competent", "conclude",
    "confident", "consequent", "consistent", "contemplate", "convince",
    "corporate", "correlate", "dedicate", "deficient", "deliberate",
    "designate", "determine", "diligent", "elaborate", "eliminate",
    "eloquent", "emergent", "emphasize", "encounter", "endeavor",
    "evaluate", "evidence", "excellent", "excessive", "explicit",
    "facilitate", "factual", "feasible", "fragment", "generate",
    "genuine", "gratitude", "hesitate", "identical", "identify",
    "illuminate", "imminent", "implement", "implicit", "indicate",
    "influence", "innovate", "inspect", "integrate", "interpret",
    "intimate", "intricate", "intuitive", "literacy", "maintain",
    "manifest", "maximize", "meticulous", "minimize", "moderate",
    "momentous", "narrative", "necessity", "negotiate", "objective",
    "obstacle", "optimize", "peculiar", "perceive", "persuade",
    "plausible", "pragmatic", "precede", "precise", "prevalent",
    "profound", "prominent", "reconcile", "relevant", "resilient",
    
    # Additional 900 words
    "abandon", "absolute", "absorb", "academic", "accelerate",
    "acceptable", "accompany", "accomplish", "accumulate", "accurate",
    "achieve", "acknowledge", "acquire", "activate", "adapt",
    "adequate", "adjust", "administer", "admire", "admission",
    "advance", "advantage", "adventure", "adversity", "affiliate",
    "affluent", "aggregate", "aggressive", "agitate", "algorithm",
    "alienate", "allocate", "alternate", "amend", "amplify",
    "analogy", "anchor", "animate", "announce", "anonymous",
    "antagonist", "apology", "appetite", "applause", "applicable",
    "appoint", "appreciate", "approach", "appropriate", "arbitrary",
    "archive", "arduous", "arrange", "articulate", "artificial",
    "ascend", "aspect", "assemble", "assert", "assess",
    "assign", "associate", "assume", "assure", "astonish",
    "athletic", "atmosphere", "attach", "attain", "attempt",
    "attend", "attitude", "attribute", "augment", "authority",
    "automate", "available", "average", "aviation", "await",
    "balance", "bankrupt", "bargain", "barrier", "behavior",
    "believe", "beneficial", "benevolent", "biology", "blossom",
    "boundary", "brevity", "broadcast", "burden", "cabinet",
    "calculate", "calendar", "campaign", "capable", "capital",
    "capture", "cardinal", "category", "celebrate", "central",
    "ceremony", "challenge", "champion", "channel", "chapter",
    "character", "charity", "chemical", "circumstance", "citizen",
    "clarify", "classify", "climate", "cluster", "coincide",
    "collapse", "collect", "colonial", "colorful", "combine",
    "comfort", "command", "comment", "commerce", "commission",
    "commit", "committee", "communicate", "community", "compare",
    "compete", "compile", "complain", "complete", "complex",
    "comply", "compose", "compound", "comprehend", "compress",
    "comprise", "compute", "conceal", "concede", "conceive",
    "concentrate", "concept", "concern", "conclude", "concrete",
    "condemn", "conduct", "confer", "confess", "confide",
    "configure", "confirm", "conflict", "conform", "confront",
    "confuse", "congress", "connect", "conscious", "consensus",
    "consent", "conserve", "consider", "consist", "console",
    "constant", "constitute", "constrain", "construct", "consult",
    "consume", "contain", "continue", "contract", "contrary",
    "contribute", "control", "controversy", "convenient", "convert",
    "coordinate", "copyright", "cordial", "correct", "correlate",
    "correspond", "corrupt", "costume", "council", "counsel",
    "counter", "courage", "courtesy", "create", "creature",
    "credible", "credit", "criteria", "critical", "critique",
    "crucial", "crystal", "cultivate", "cultural", "curious",
    "currency", "current", "curtain", "custody", "customer",
    "cylinder", "database", "debate", "decline", "decorate",
    "decrease", "deduce", "defend", "deficit", "define",
    "degrade", "delegate", "delete", "delicate", "deliver",
    "demand", "democracy", "demonstrate", "denote", "dense",
    "depart", "depend", "depict", "deploy", "deposit",
    "depress", "derive", "describe", "desert", "design",
    "desire", "despair", "destroy", "detail", "detect",
    "develop", "deviate", "device", "devote", "diagnose",
    "diagram", "dialogue", "dictate", "differ", "digest",
    "digital", "dignity", "dilemma", "dimension", "diminish",
    "diplomat", "direct", "disable", "disagree", "disappear",
    "discard", "discharge", "discipline", "discourse", "discover",
    "discrete", "discuss", "disease", "disguise", "dismiss",
    "display", "dispose", "dispute", "disrupt", "dissolve",
    "distinct", "distort", "distribute", "disturb", "diverse",
    "divide", "divine", "document", "domestic", "dominant",
    "donate", "dormant", "double", "dramatic", "drastic",
    "duration", "dynamic", "earnest", "eclipse", "ecology",
    "economy", "edition", "educate", "effective", "efficient",
    "elastic", "elderly", "element", "eligible", "eliminate",
    "embark", "embrace", "emerge", "emotion", "employ",
    "empower", "enable", "enclose", "encore", "encounter",
    "endorse", "endure", "enforce", "engage", "engineer",
    "enhance", "enlarge", "enlighten", "enrich", "ensure",
    "entitle", "entrance", "envelope", "environment", "episode",
    "equate", "equipment", "equivalent", "escalate", "escape",
    "escort", "essence", "establish", "estate", "estimate",
    "ethical", "evaluate", "evoke", "evolve", "exact",
    "examine", "exceed", "exchange", "exclude", "execute",
    "exercise", "exhaust", "exhibit", "expand", "expect",
    "expend", "expense", "expert", "expire", "explain",
    "explode", "explore", "export", "expose", "express",
    "extend", "external", "extract", "extreme", "fabric",
    "factor", "faculty", "failure", "fashion", "feature",
    "federal", "feedback", "festival", "fiction", "filter",
    "finance", "finite", "flexible", "flourish", "fluctuate",
    "forecast", "foreign", "format", "formula", "foster",
    "foundation", "fraction", "framework", "freedom", "frequent",
    "frontier", "function", "fundamental", "furnish", "gallery",
    "gateway", "generate", "generous", "genius", "gentle",
    "gesture", "global", "gorgeous", "govern", "graduate",
    "graphic", "grateful", "gravity", "guarantee", "guardian",
    "guidance", "habitat", "harbor", "harvest", "hazard",
    "healthy", "heritage", "heroic", "hesitate", "hidden",
    "historic", "holiday", "honesty", "horizon", "horror",
    "hostile", "household", "housing", "humor", "hybrid",
    "hydrogen", "hygiene", "hypothesis", "identical", "identify",
    "ideology", "ignite", "ignore", "illegal", "illustrate",
    "imagine", "imitate", "immense", "immune", "impact",
    "imply", "import", "impose", "improve", "impulse",
    "inactive", "incline", "include", "income", "increase",
    "indicate", "indirect", "industry", "infinite", "inflict",
    "inform", "inhabit", "inherit", "initial", "inject",
    "injure", "innocent", "inquire", "insight", "inspire",
    "install", "instance", "instinct", "institute", "instruct",
    "insult", "insure", "integral", "intellect", "intense",
    "interact", "interest", "internal", "interpret", "interview",
    "intimate", "intrigue", "invade", "invent", "invest",
    "invite", "involve", "isolate", "issue", "itemize",
    "journey", "jubilee", "justice", "justify", "kingdom",
    "kinetic", "ladder", "landing", "landscape", "language",
    "lateral", "latitude", "launch", "legacy", "legend",
    "legislate", "leisure", "liberal", "library", "license",
    "lifestyle", "lifetime", "lighting", "likewise", "limited",
    "linear", "lingering", "liquid", "listen", "literal",
    "literary", "locate", "logical", "loyalty", "luxury",
    "machine", "magnetic", "magnitude", "maintain", "majority",
    "manage", "manifest", "manner", "manual", "margin",
    "marine", "market", "marshal", "martial", "material",
    "mature", "maximum", "measure", "mechanic", "mediate",
    "medical", "medieval", "medium", "melody", "member",
    "memorable", "mental", "mentor", "merchant", "mercury",
    "meridian", "merit", "message", "method", "metric",
    "microbe", "military", "mineral", "minimal", "minister",
    "miracle", "mission", "mistake", "mixture", "mobile",
    "model", "modern", "modify", "module", "moisture",
    "molecule", "monitor", "monopoly", "moral", "mortgage",
    "motion", "motivate", "motive", "multiple", "municipal",
    "muscle", "musical", "mutual", "mystery", "natural",
    "navigate", "negative", "neglect", "negotiate", "neutral",
    "nominal", "normal", "notable", "notice", "notify",
    "notion", "nourish", "novelty", "nuclear", "nullify",
    "numeric", "nurture", "observe", "obvious", "occupy",
    "occur", "ocean", "offend", "office", "operate",
    "opinion", "oppose", "optical", "optimal", "option",
    "oracle", "orbital", "organic", "orient", "origin",
    "ornament", "outlook", "output", "outrage", "overcome",
    "overlay", "override", "overseas", "overtake", "overtime",
    "pacific", "package", "parallel", "pardon", "parent",
    "partial", "particle", "partner", "passage", "passion",
    "passive", "patent", "patient", "pattern", "payment",
    "peacful", "penalty", "pending", "pension", "people",
    "perceive", "perfect", "perform", "period", "permit",
    "persist", "person", "persuade", "physical", "picture",
    "pioneer", "pipeline", "placid", "planet", "platform",
    "plausible", "pleasant", "pledge", "plenty", "plural",
    "poetic", "policy", "popular", "portion", "portrait",
    "position", "positive", "possible", "postage", "potential",
    "poverty", "powder", "powerful", "practical", "practice",
    "precious", "precise", "predict", "prefer", "premise",
    "premium", "prepare", "present", "preserve", "preside",
    "pressure", "prestige", "prevent", "previous", "primary",
    "principle", "priority", "privacy", "private", "privilege",
    "probable", "problem", "proceed", "process", "produce",
    "product", "profile", "program", "progress", "project",
    "promise", "promote", "proper", "property", "propose",
    "prospect", "protect", "protest", "provide", "public",
    "publish", "purpose", "qualify", "quality", "quarter",
    "question", "quicken", "quietly", "radical", "random",
    "rapid", "rational", "reaction", "realize", "reason",
    "recall", "receive", "reckon", "recognize", "recommend",
    "record", "recover", "recruit", "reduce", "refer",
    "reflect", "reform", "refuse", "regard", "regular",
    "regulate", "reinforce", "reject", "relate", "release",
    "reliable", "relieve", "religion", "remain", "remark",
    "remedy", "remember", "remind", "remote", "remove",
    "render", "renew", "repair", "repeat", "replace",
    "report", "require", "rescue", "research", "reserve",
    "reside", "resolve", "resort", "resource", "respect",
    "respond", "restore", "restrict", "result", "retain",
    "retire", "retreat", "return", "reveal", "revenge",
    "revenue", "reverse", "review", "revise", "revive",
    "revolve", "reward", "rhythm", "ridicule", "rigorous",
    #  "aberration", "acquiescence", "ameliorate", "anachronistic", "antipathy",
    # "apocryphal", "apotheosis", "archetype", "assiduous", "atavistic",
    # "attenuate", "bellicose", "bifurcate", "cacophony", "callipygian",
    # "capricious", "cartesian", "catharsis", "circumlocution", "circumspect",
    # "cognizant", "concomitant", "condescending", "conflagration", "congruent",
    # "conscientious", "convivial", "cryptographic", "cynosure", "demagogue",
    # "denouement", "derivative", "diaphanous", "dichotomy", "discombobulate",
    # "dissonance", "duplicitous", "ebullient", "efficacious", "egregious",
    # "ephemeral", "epistolary", "equanimity", "erudite", "esoteric",
    # "ethereal", "euphemistic", "exacerbate", "excruciating", "exigent",
    # "existential", "exponential", "fastidious", "filibuster", "fortuitous",
    # "garrulous", "genuflect", "grandiloquent", "hegemony", "hermetic",
    # "hierarchical", "holistic", "homogeneous", "hyperbole", "hypothetical",
    # "idiosyncratic", "impecunious", "imperceptible", "impetuous", "incendiary",
    # "incontrovertible", "indeterminate", "ineffable", "ineluctable", "inexorable",
    # "infinitesimal", "insidious", "inviolable", "irascible", "juxtaposition",
    # "kinesthetic", "labyrinthine", "legerdemain", "lexicographer", "lugubrious",
    # "magnanimous", "malfeasance", "mellifluous", "mendacious", "mercurial",
    # "metamorphosis", "misanthrope", "mitigate", "nebulous", "nefarious",
    # "obfuscate", "obstreperous", "oleaginous", "oscillate", "palimpsest",
    # "paradigmatic", "paradoxical", "parsimonious", "pedagogical", "perspicacious",
    # "philosophical", "pneumatic", "pontificate", "precipitous", "presumptuous"
]


class WordScrambleGame(Game):
    def __init__(self):
        pass

    def name(self):
        return "Word Scramble"
    
    def __pick_word(self):
        return random.choice(word_list)
    
    def __scramble_word(self, word):
        """
        Scrambles a word while ensuring the scrambled version is different
        from the original word.
        """
        # Convert to list for scrambling
        word_list = list(word.lower().replace(" ", ""))
        
        # Keep scrambling until we get a different arrangement
        while True:
            random.shuffle(word_list)
            scrambled = ''.join(word_list)
            if scrambled != word.lower().replace(" ", ""):
                return scrambled
    def game_round(self, word):
        # Remove spaces and make lowercase for easier comparison
        original = word.lower().replace(" ", "")
        
        # Scramble the word
        scrambled = self.__scramble_word(word)

        print(f"\nOriginal word: {word}")
        print(f"Scrambled word: {scrambled.upper()}")
        print("Unscramble this word!")
        
        while True:
            guess = input("\nEnter your guess: ").lower().replace(" ", "")
            
            if guess == original:
                print(f"Congratulations! You unscrambled the word correctly: {word}")
                return True
            else:
                print(f"Wrong! Try again!")
               
    def play(self):
        print("🎮 Welcome to Word Scramble Game! 🎮")
        while True:
            word = self.__pick_word()
            self.game_round(word)
            play_again = input("\n🔄 Do you want to play again? (yes/no): ").strip().lower()
            if play_again != "yes":
                break
        pass