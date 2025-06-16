import google.generativeai as genai
import os
import unicodedata

class GeminiProcessor:
    def __init__(self):
        # Load the Gemini API key from environment variables and configure the API
        self.api_key = os.getenv("API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

    @staticmethod
    def standardize_word(word):
        """
        Ensures consistent formatting of words in the dictionary.
        - Converts to lowercase.
        - Removes accents.
        - Removes spaces (words are joined if needed).
        This function is used to prevent any inconsistencies in the API output, even if the prompt already specifies the desired format.
        """
        word = word.lower()
        word = unicodedata.normalize('NFD', word)
        word = ''.join(c for c in word if unicodedata.category(c) != 'Mn')
        return word.replace(" ", "")  # Joins words if there is more than one per line

    def extend_dictionary(self, dictionary_path):
        """
        Expands the dictionary by interacting with the Gemini API.
        - For each word in the dictionary, 10 additional contextually related words are generated.
        - Words are translated to Spanish if needed and combined words are added if relevant.
        - The result is saved to the original dictionary file.
        Returns:
            The path to the updated dictionary or None if an error occurs.
        """
        try:
            # Load the content of the original dictionary
            with open(dictionary_path, "r", encoding="utf-8") as f:
                content = f.read()

            name_file = os.path.basename(dictionary_path)

            prompt = (
                f"Hello, Gemini. I am going to send you my file {name_file}. It is a text file that contains one word per line. " 
                f"All these words come from information I legally obtained from the data published by an Instagram profile. "
                f"I want you to return a file with the same name: {name_file}. The file you have to return must meet the following requirements:\n"
                f"-	All words must be in Spanish. If there are any in another language, translate them and replace the word with its meaning in Spanish.\n"
                f"-	For each word in the file, you must create 10 additional words that are related to that word and the context of the file’s content.\n"
                f"-	If any two or more words in the file can be combined to form a new existing word, you must also add that. But add it as one single word, with no spaces or separators.\n"
                f"-	The format of the file must be like the original: only one word per line.\n"
                f"-	Do not include any comments, just the words in sequence and with no blank lines.\n"
                f"-	All the words you add must be in lowercase and without accents.\n"
                f"It is very important that you only return the file and you do not reply to my prompt or add anything other than one word per line in the file. "
                f"Also, it is very important that there is only one word per line and that there are no extra spaces or blank lines. "
                f"Do not delete the original words that were in {name_file}.\n"
                f"The content of the file is as follows:\n {content}"
            )

            response = self.model.generate_content(prompt)

            # Process the response and delete the first and last line because Gemini returns ''' in the first and last line
            lines = response.text.strip().splitlines()
            lines = lines[1:-1]

            # Standardize all words
            normalized_lines = [self.standardize_word(line.strip()) for line in lines if line.strip()]

            with open(dictionary_path, "w", encoding="utf-8") as f:
                f.write("\n".join(normalized_lines))

            print(f"Successfully generated file: {dictionary_path}")
            return dictionary_path

        except Exception as e:
            print("Error connecting with Gemini.")
            print("Details:", e)
            return None

    def reduce_dictionary(self, dictionary_path):
        """
        Reduces the dictionary by removing irrelevant or unnecessary terms using the Gemini API.
        - The API receives the dictionary and is instructed to return only the most relevant words.
        - The result is saved back to the original dictionary file.

        Returns:
            The path to the updated dictionary, or None if an error occurs.
        """
        try:
            with open(dictionary_path, "r", encoding="utf-8") as f:
                content = f.read()

            name_file = os.path.basename(dictionary_path)

            prompt = (
                f"Hello, Gemini. I am going to send you my file {name_file}. It is a text file that contains one word "
                f"per line. All these words come from information I legally obtained from an Instagram profile. "
                f"I want you to remove the words that you consider unnecessary or irrelevant for data extraction. "
                f"Return the file with the same name: {name_file}.\n"
                f"Do not include any comments, just the words by following the format of my file {name_file}, with no blank lines.\n"
                f"File content: \n {content}"
            )

            response = self.model.generate_content(prompt)
            
            # Save the result back to the file
            with open(dictionary_path, "w", encoding="utf-8") as f:
                f.write(response.text)

            print(f"Successfully generated file: {dictionary_path}")
            return dictionary_path

        except Exception as e:
            print("Error connecting with Gemini.")
            print("Details:", e)
            return None
