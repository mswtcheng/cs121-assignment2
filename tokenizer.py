#Reads the input text and returns a list of tokens
#Time complexity: O(n) where n is the total number of characters in the text.
#Explanation: Splitting each line of the text into words takes O(n) time. Checking if each character in a word is alphanumeric takes O(n) time. Overall time complexity is therefore O(n) time.
def tokenize(text):
    tokens = []

    # Splits the text into lines and then into words
    lines = text.splitlines()
    for line in lines:
        words = line.split()
        # Tokenizes each word in the list of words
        for word in words:
            token = ''
            for char in word:
                if char.isalnum():  
                    token += char.lower() 
            if token: 
                tokens.append(token)
    return tokens

#Counts occurrences of each token in the list
#Time complexity: O(n) where n is the total number of tokens.
#Explanation: Looping through the list of tokens takes O(n) time. Checking if a token is in the dictionary and updating the count is takes O(1) time. Overall time complexity is therefore O(n) time.
def compute_frequencies(tokens, frequencies):
    #If a token is not in frequencies, a new one is created with the value of 1. Otherwise, the existing token has its value increased by 1.
    for token in tokens:
        if token in frequencies:
            frequencies[token] += 1
        else:
            frequencies[token] = 1
            
    return frequencies

#Displays word frequencies in decreasing order
#Time complexity: O(n log n), where n is the number of unique tokens.
#Explanation: Sorting the list by frequency takes O(n log n) time. Printing each token and its frequency takes O(n) time. Overall time complexity is therefore O(n log n) time.
def print_frequencies(frequencies, output_format=" - "):
    #Sorts frequencies from greatest to least
    sorted_frequencies = sorted(frequencies.items(), key=lambda item: item[1], reverse=True)

    #Prints frequencies. output_format can vary depending on given parameter, but is " - " by default.
    for token, freq in sorted_frequencies:
        print(f"{token}{output_format}{freq}")


#Takes two list of tokens and returns the number of similar token
#Time complexity: O(nm) where n is the length of the tokens1 and m is the length of tokens2.
#Explanation: Comparing the two token lists involves a nested loop involving tokens1 and tokens2, resulting in O(nm) time. 
def compare_files(tokens1, tokens2):
    counter = 0
    #Checks if each token in tokens1 is in tokens2, and increases the counter by 1 if it is. 
    for token in tokens1:
        if token in tokens2:
            print(token)
            counter += 1

    return counter

