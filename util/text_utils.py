class TextUtils:
    @staticmethod
    def enbolden(text):
        return f"\033[1;4m{text}\033[0m"
    
    @staticmethod
    def find_replace_enbolden(text, word):
        return text.replace(word, TextUtils.enbolden(word))