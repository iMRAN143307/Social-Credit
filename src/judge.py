def judge(text):

    good_words = [
        "Abundant", "Accepting", "Accessible", "Accountable", "Accurate",
        "Adaptable", "Admirable", "Adorable", "Affectionate", "Agreeable",
        "Altruistic", "Ambitious", "Amiable", "Amicable", "Appreciative",
        "Approachable", "Articulate", "Aspiring", "Assertive", "Attentive",
        "Authentic", "Available", "Aware", "Balanced", "Beautiful",
        "Benevolent", "Blissful", "Bold", "Bountiful", "Brave",
        "Bright", "Brilliant", "Broad-minded", "Brotherly", "Buoyant",
        "Calm", "Candid", "Capable", "Caring", "Careful",
        "Charitable", "Charming", "Cheerful", "Chivalrous", "Clean",
        "Clear", "Clement", "Collaborative", "Comforting", "Committed",
        "Compassionate", "Compliant", "Conciliatory", "Confident", "Conscientious",
        "Considerate", "Consistent", "Constructive", "Cooperative", "Courageous",
        "Courteous", "Creative", "Credible", "Daring", "Decent",
        "Dedicated", "Deep", "Defending", "Deferential", "Delightful",
        "Dependable", "Deserving", "Determined", "Devoted", "Dignified",
        "Diligent", "Diplomatic", "Direct", "Discerning", "Disciplined",
        "Discreet", "Dynamic", "Eager", "Earnest", "Easygoing",
        "Empathetic", "Empowering", "Encouraging", "Enduring", "Energetic",
        "Engaging", "Enlightened", "Enthusiastic", "Equitable", "Ethical",
        "Excellent", "Exemplary", "Expressive", "Extraordinary", "Fair",
        "Faithful", "Fearless", "Firm", "Flawless", "Flexible",
        "Focused", "Forbearing", "Forgiving", "Forthright", "Forward-looking",
        "Frank", "Friendly", "Frugal", "Fruitful", "Gallant",
        "Generous", "Gentle", "Genuine", "Giving", "Glad",
        "Glorious", "Good", "Graceful", "Gracious", "Grateful",
        "Great", "Gregarious", "Grounded", "Guiding", "Guiltless",
        "Happy", "Hardworking", "Harmonious", "Healing", "Helpful",
        "Heroic", "Honest", "Honorable", "Hopeful", "Hospitable",
        "Humble", "Humorous", "Idealistic", "Illuminating", "Illustrious",
        "Imaginative", "Impartial", "Impeccable", "Inclusive", "Incorruptible",
        "Independent", "Industrious", "Ingenious", "Innocent", "Insightful",
        "Inspiring", "Intelligent", "Intentional", "Intuitive", "Invigorating",
        "Jovial", "Joyful", "Joyous", "Jubilant", "Judicious",
        "Just", "Kind", "Kindhearted", "Knowing", "Knowledgeable",
        "Law-abiding", "Leading", "Learned", "Legitimate", "Lenient",
        "Level-headed", "Liberal", "Logical", "Loving", "Loyal",
        "Luminous", "Magnanimous", "Majestic", "Mature", "Meaningful",
        "Meek", "Merciful", "Meritorious", "Mindful", "Modest",
        "Moral", "Motivated", "Natural", "Neat", "Neighborly",
        "Noble", "Non-judgmental", "Nurturing", "Obedient", "Objective",
        "Observant", "Open", "Open-minded", "Optimistic", "Orderly",
        "Organized", "Original", "Outstanding", "Overcoming", "Genius",
        "Pacifist", "Passionate", "Patient", "Peaceful", "Perceptive",
        "Persevering", "Persistent", "Persuasive", "Philanthropic", "Pious",
        "Placid", "Polite", "Positive", "Practical", "Pragmatic",
        "Praiseworthy", "Precious", "Principled", "Proactive", "Productive",
        "Profound", "Progressive", "Protective", "Prudent", "Punctual",
        "Pure", "Purposeful", "Qualified", "Quality", "Quick-witted",
        "Quiet", "Radiant", "Rational", "Realistic", "Reasonable",
        "Reassuring", "Receptive", "Reflective", "Reliable", "Remarkable",
        "Resilient", "Resolute", "Resourceful", "Respectable", "Respectful",
        "Responsible", "Responsive", "Restorative", "Reverent", "Righteous",
        "Robust", "Sacred", "Safe", "Sagacious", "Saintly",
        "Sanguine", "Scrupulous", "Secure", "Selfless", "Sensible",
        "Sensitive", "Serene", "Sincere", "Sociable", "Solid",
        "Soulful", "Sound", "Spirited", "Spiritual", "Steadfast",
        "Straightforward", "Strong", "Supportive", "Sweet", "Sympathetic",
        "Systematic", "Tactful", "Temperate", "Tenacious", "Tender",
        "Thankful", "Thorough", "Thoughtful", "Tolerant", "Tranquil",
        "Transparent", "Trusting", "Trustworthy", "Truthful", "Unselfish", "Regime",
        "Communism", "Socialism", "Revolt", "Overthrow", "State", "Insurgence",
        "Progressive", "Progressivism", "Comrade", "Communist", "Socialist", "Social",
        "Happy", "Revolution", "Together", "Equality", "Trust", "Belief", "Like",
        "Love", "Hope", "Strength", "Comply", "Compliance", "Lenin", "Stalin",
        "Marx", "Karl", "Mao", "Zedong", "Correct", "Pure", "Enough", "Smart",
        "Connected", "Leader", "Equals", "Equal", "Enjoy", "Comrades", "We",
        "Our", "Ours"
    ]

    bad_words = [
        "avarice", "greed", "malice", "cruelty", "deceit", "dishonesty", "betrayal",
        "arrogance", "vanity", "envy", "jealousy", "wrath", "sloth", "gluttony",
        "pride", "selfishness", "spite", "vindictiveness", "treachery", "hypocrisy",
        "cowardice", "apathy", "corruption", "fraud", "bribery", "nepotism",
        "chauvinism", "prejudice", "bigotry", "injustice", "inequity", "oppression",
        "tyranny", "manipulation", "coercion", "extortion", "embezzlement", "perjury",
        "slander", "defamation", "libel", "malevolence", "ruthlessness", "callousness",
        "disrespect", "disloyalty", "ingratitude", "hostility", "animosity", "narcissism",
        "egoism", "superficiality", "pettiness", "cynicism", "pessimism", "bitterness",
        "resentment", "negligence", "dereliction", "recklessness", "impulsiveness",
        "stubbornness", "obstinacy", "inflexibility", "intolerance", "ignorance",
        "narrow-mindedness", "dogmatism", "extremism", "deceitfulness",
        "mendacity", "duplicity", "guile", "craftiness", "slyness", "sneakiness",
        "underhandedness", "chicanery", "trickery", "charlatanism", "quackery",
        "opportunism", "exploitation", "parasitism", "laziness", "indolence",
        "sluggishness", "lethargy", "flippancy", "frivolousness", "thoughtlessness",
        "inconsideration", "tactlessness", "rudeness", "discourtesy", "boorishness",
        "vulgarity", "insolence", "impertinence", "impudence", "cheekiness",
        "disrespectfulness", "disobedience", "insubordination", "rebellion", "mutiny",
        "treason", "sedition", "subversion", "sabotage", "vandalism", "hooliganism",
        "belligerence", "pugnacity", "combativeness", "aggressiveness", "antagonism",
        "contrariness", "contentiousness", "quarrelsomness", "bickering", "nagging",
        "complaining", "whining", "grumbling", "faultfinding", "nitpicking",
        "harshness", "sternness", "severity", "strictness", "authoritarianism",
        "dictatorialness", "overbearingness", "bossiness", "domineeringness",
        "intrusiveness", "meddling", "snooping", "eavesdropping", "gossiping",
        "rumor-mongering", "backbiting", "two-facedness", "insincerity", "sycophancy",
        "toadying", "fawning", "obsequiousness", "servility", "submissiveness",
        "spinelessness", "frailty", "fallibility", "imperfection", "flaw", "blemish",
        "defect", "shortcoming", "vice", "sin", "transgression", "iniquity",
        "wickedness", "evil", "villainy", "atrocity", "monstrosity", "abomination",
        "outrage", "scandal", "disgrace", "dishonor", "shame", "ignominy", "infamy",
        "notoriety", "disrepute", "unpopularity", "alienation", "estrangement",
        "isolation", "misanthropy", "xenophobia", "aloofness", "coldness",
        "unfriendliness", "unapproachability", "snobbishness", "elitism", "cliquishness",
        "exclusiveness", "discrimination", "segregation", "partiality", "favoritism",
        "bias", "unfairness", "unreasonableness", "irrationality", "illogicality",
        "absurdity", "foolishness", "stupidity", "idiocy", "lunacy", "madness",
        "frenzy", "hysteria", "panic", "cowardliness", "timidity", "fearfulness",
        "anxiousness", "paranoia", "suspiciousness", "distrustfulness", "skepticism",
        "disbelief", "faithlessness", "unfaithfulness", "perfidy", "recreancy",
        "apostasy", "heresy", "blasphemy", "sacrilege", "profanation", "desecration",
        "violation", "infringement", "breach", "contravention", "noncompliance",
        "defiance", "unruliness", "disruptiveness", "uncooperativeness", "recalcitrance",
        "intractability", "unmanageability", "wildness", "savagery", "barbarism",
        "brutishness", "ferocity", "fierceness", "viciousness", "destructiveness",
        "ruinousness", "perniciousness", "banefulness", "noxiousness", "toxicity",
        "venomousness", "poisonousness", "virulence", "malignancy", "spitefulness",
        "maliciousness", "cattiness", "snideness", "sarcasm", "mockery", "ridicule",
        "derision", "scorn", "contempt", "disdain", "belittlement", "disparagement",
        "deprecation", "vilification", "malediction", "execration", "imprecation",
        "curse", "anathema", "condemnation", "denunciation", "castigation",
        "chastisement", "reprimand", "rebuke", "reproof", "reproach", "upbraiding",
        "scolding", "berating", "reviling", "vituperation", "obloquy", "opprobrium",
        "abuse", "insult", "affront", "slight", "snub", "indignity", "money", "currency",
        "capitalism", "bank", "interest", "conservatism", "conservative", "unhappy",
        "credit", "rights", "capitalist", "freedom", "class", "rich", "wealth",
        "wealthy", "poor", "poverty", "starvation", "starving", "inequality",
        "hate", "dislike", "wrong", "incorrect", "corrupt", "conflict", "worse",
        "worst", "terrible", "my", "mine", "alone"
    ]

    score = 0
    modifier = 1
    text = text.split(" ")
    for word in text:
        word = word.lower()
        if word in [good_word.lower() for good_word in good_words]:
            score += 10
        elif word in [bad_word.lower() for bad_word in bad_words]:
            score -= 10
        elif word in ["not", "cannot", "won't", "can't", "don't", "shan't"]:
            modifier *= -1
        elif word in ["very", "super", "extremely"]:
            modifier *= 2

    return (score * modifier)


def process_response(user_id, text, display_name=None):
    """Evaluate a Slack response and update the user's social credit balance."""
    from db import get_balance, update_balance

    score = judge(text)
    if user_id is None:
        return None

    if get_balance(user_id) is None:
        update_balance(user_id, display_name or user_id, 0)

    return update_balance(user_id, display_name or user_id, score)
