import re

print("Reading word lists...", end="", flush=True)
all_words_file = open("words/nl-all.txt")
all_words = all_words_file.read().splitlines()
all_words_file.close()
print(" [DONE]")
print(f"Loaded {len(all_words)} words")

print("Calculating lists...", end="", flush=True)
word_spec = [
    {"pattern":"^[a-z]{2}$","out":"words/nl-2.txt"},
    {"pattern":"^[a-z]{3}$","out":"words/nl-3.txt"},
    {"pattern":"^[a-z]{4}$","out":"words/nl-4.txt"},
    {"pattern":"^[a-z]{5}$","out":"words/nl-5.txt"},
    {"pattern":"^[a-z]{6}$","out":"words/nl-6.txt"},
    {"pattern":"^[a-z]{7}$","out":"words/nl-7.txt"},
    {"pattern":"^[a-z]{8}$","out":"words/nl-8.txt"},
    {"pattern":"^[a-z]{9}$","out":"words/nl-9.txt"},
    {"pattern":"^[a-z]{10}$","out":"words/nl-10.txt"},
    {"pattern":"^[a-z]{11}$","out":"words/nl-11.txt"},
    {"pattern":"^[a-z]{12}$","out":"words/nl-12.txt"},
    {"pattern":"^[a-z]{13}$","out":"words/nl-13.txt"},
]
word_lists = dict()

def write_word(file: str, text: str):
    if not file in word_lists:
        word_lists[file] = list()
        
    word_lists[file].append(f"{text}\n")

for word in all_words:
    for spec in word_spec:
        if re.search(spec["pattern"], word) != None:
            write_word(spec["out"], word.upper())

print(" [DONE]") 
print(len(word_lists))

for file in word_lists:
    word_list = word_lists[file]
    print(f"Writing { len(word_list) } words to { file }...", end="", flush=True)
    
    writer = open(file, mode="w")
    writer.writelines(word_list)
    writer.close()
    print(f" [DONE]")