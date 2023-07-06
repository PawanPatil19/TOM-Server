
NUMBER_OF_WORDS_PER_LINE = 5
def get_formatted_learning_details(details):
    words = details.split()
    phrases = [' '.join(words[i:i+NUMBER_OF_WORDS_PER_LINE]) for i in range(0, len(words), NUMBER_OF_WORDS_PER_LINE)]
    return '\n'.join(phrases)