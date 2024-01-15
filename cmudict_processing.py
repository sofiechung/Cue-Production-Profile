import string

cmupath = "cmudict.0.7a"
DICT = open(cmupath)

word_dict = {}
num_syllables = {}
syllable_dict = {}
stress_dict = {}

for entry in DICT:
  if not entry.startswith(";;;"):
    word = entry.split()[0].lower()
    phones = entry.split()[1:]
    num_vowels = len([phone for phone in phones if phone[-1] in string.digits])
    print
    num_syllables[word] = str(num_vowels)

    syllable_list = []
    stress_list_dict = {}

    syllable_count = 1
    syll_constituent = "o"
    syll_const_num = 1
    for i in range(len(phones)):
      phone = phones[i].lower()
      if phone[-1] in string.digits:
        stress_list_dict[str(syllable_count)] = str(phone[-1])
        if syllable_count == 1:
          syll_constituent = "a"
        elif syllable_count == num_vowels:
          syll_constituent = "c"
        syllable_list.append("n" + str(syllable_count))
        syllable_count += 1
        syll_const_num = 1
        # phone = phone[:len(phone)-1]
      else:
        if syll_constituent == "c":
          syllable_list.append(syll_constituent + str(syllable_count-1) + str(syll_const_num))
        else:
          syllable_list.append(syll_constituent + str(syllable_count) + str(syll_const_num))
        syll_const_num += 1
      phones[i] = phone

    syllable_dict[word] = syllable_list
    stress_dict[word] = stress_list_dict

